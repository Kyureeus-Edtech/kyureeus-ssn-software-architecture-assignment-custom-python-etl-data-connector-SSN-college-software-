# test_authreq.py
import os
import sys
import importlib
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest
import responses

AUTH_ENV_VARS = {
    "CZDS_AUTH_URL": "https://auth.example.local/api/authenticate",
    "CZDS_USERNAME": "test-user",
    "CZDS_PASSWORD": "test-pass",
    "CZDS_AUTH_TIMEOUT_SECONDS": "5",
    "CZDS_AUTH_RETRIES": "3",
    # Mongo env not required for tests because we monkeypatch logging.
    # "MONGO_URI": "...",
    # "MONGO_DB": "..."
}

def _import_authreq_module():
    if "authreq" in sys.modules:
        del sys.modules["authreq"]
    return importlib.import_module("authreq")

@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    for k, v in AUTH_ENV_VARS.items():
        monkeypatch.setenv(k, v)
    if "authreq" in sys.modules:
        del sys.modules["authreq"]
    yield
    if "authreq" in sys.modules:
        del sys.modules["authreq"]

@responses.activate
def test_auth_success_and_mongo_logging(monkeypatch):
    authreq = _import_authreq_module()

    # capture mongo audit events
    events = []
    monkeypatch.setattr(authreq, "_log_auth_event", lambda d: events.append(d))

    token = "token-abc-123"
    expires_in = 3600
    responses.add(
        responses.POST,
        AUTH_ENV_VARS["CZDS_AUTH_URL"],
        json={"accessToken": token, "expiresIn": expires_in},
        status=200,
    )

    c = authreq.AuthClient()
    t = c.get_token()

    assert t == token
    assert c._expires_at is not None and c._expires_at > time.time()

    # verify audit event was logged
    assert any(e.get("status") == "success" for e in events)
    success_event = [e for e in events if e.get("status") == "success"][0]
    assert success_event.get("username") == AUTH_ENV_VARS["CZDS_USERNAME"]
    assert success_event.get("http_status") == 200
    assert "token_length" in success_event
    assert "expires_at" in success_event

@responses.activate
def test_auth_401_raises_and_mongo_logging(monkeypatch):
    authreq = _import_authreq_module()

    events = []
    monkeypatch.setattr(authreq, "_log_auth_event", lambda d: events.append(d))

    responses.add(
        responses.POST,
        AUTH_ENV_VARS["CZDS_AUTH_URL"],
        json={"message": "invalid credentials"},
        status=401,
    )

    c = authreq.AuthClient()
    with pytest.raises(authreq.AuthError):
        c.get_token()

    # verify failure audit event
    assert any(e.get("status") == "failure" and e.get("reason") == "credentials_rejected" for e in events)

@responses.activate
def test_transient_failure_then_success(monkeypatch):
    authreq = _import_authreq_module()

    events = []
    monkeypatch.setattr(authreq, "_log_auth_event", lambda d: events.append(d))

    token = "transient-token"
    expires_in = 60

    responses.add(
        responses.POST,
        AUTH_ENV_VARS["CZDS_AUTH_URL"],
        body=Exception("simulated connection reset"),
    )
    responses.add(
        responses.POST,
        AUTH_ENV_VARS["CZDS_AUTH_URL"],
        json={"accessToken": token, "expiresIn": expires_in},
        status=200,
    )

    c = authreq.AuthClient()
    t = c.get_token()
    assert t == token
    assert c._expires_at > time.time()
    # should have a success event eventually
    assert any(e.get("status") == "success" for e in events)

@responses.activate
def test_malformed_json_raises(monkeypatch):
    authreq = _import_authreq_module()

    events = []
    monkeypatch.setattr(authreq, "_log_auth_event", lambda d: events.append(d))

    responses.add(
        responses.POST,
        AUTH_ENV_VARS["CZDS_AUTH_URL"],
        body="this-is-not-json",
        status=200,
        content_type="text/plain",
    )

    c = authreq.AuthClient()
    with pytest.raises(authreq.AuthError):
        c.get_token()

    assert any(e.get("status") == "failure" and e.get("reason") == "invalid_json" for e in events)

@responses.activate
def test_concurrent_get_token_single_request(monkeypatch):
    authreq = _import_authreq_module()

    events = []
    monkeypatch.setattr(authreq, "_log_auth_event", lambda d: events.append(d))

    token = "concurrent-token"
    expires_in = 300

    responses.add(
        responses.POST,
        AUTH_ENV_VARS["CZDS_AUTH_URL"],
        json={"accessToken": token, "expiresIn": expires_in},
        status=200,
    )

    c = authreq.AuthClient()

    def worker():
        return c.get_token()

    num_threads = 8
    results = []
    with ThreadPoolExecutor(max_workers=num_threads) as ex:
        futures = [ex.submit(worker) for _ in range(num_threads)]
        for fut in as_completed(futures, timeout=10):
            results.append(fut.result())

    assert all(r == token for r in results)

    post_calls = [call for call in responses.calls if call.request.method == "POST"]
    assert len(post_calls) == 1, f"expected 1 POST to auth endpoint, got {len(post_calls)}"

@responses.activate
def test_request_with_auth_retries_on_401(monkeypatch):
    authreq = _import_authreq_module()

    events = []
    monkeypatch.setattr(authreq, "_log_auth_event", lambda d: events.append(d))

    initial_token = "old-token"
    new_token = "new-token"
    expires_in = 3600

    responses.add(
        responses.POST,
        AUTH_ENV_VARS["CZDS_AUTH_URL"],
        json={"accessToken": initial_token, "expiresIn": expires_in},
        status=200,
    )

    c = authreq.AuthClient()
    assert c.get_token() == initial_token

    target_url = "https://czds-api.example.local/some/resource"

    responses.add(responses.GET, target_url, status=401)
    responses.add(
        responses.POST,
        AUTH_ENV_VARS["CZDS_AUTH_URL"],
        json={"accessToken": new_token, "expiresIn": expires_in},
        status=200,
    )
    responses.add(responses.GET, target_url, json={"ok": True}, status=200)

    resp = authreq.request_with_auth(c, "GET", target_url)
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
    assert c.get_token() == new_token

    # token_invalidated event should be present (on 401 handling)
    assert any(e.get("status") == "token_invalidated" for e in events)
