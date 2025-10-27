import importlib
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest
import responses

# Ensure project root is on sys.path so sibling packages are importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

AUTH_ENV_VARS = {
    "CZDS_AUTH_URL": "https://auth.example.local/api/authenticate",
    "CZDS_USERNAME": "test-user",
    "CZDS_PASSWORD": "test-pass",
    "CZDS_AUTH_TIMEOUT_SECONDS": "5",
    "CZDS_AUTH_RETRIES": "1",
    "CZDS_API_BASE": "https://czds-api.example.local"
}

def _import_module(monkeypatch):
    # set env vars before import
    for k, v in AUTH_ENV_VARS.items():
        monkeypatch.setenv(k, v)
    if "authreq" in sys.modules:
        del sys.modules["authreq"]
    if "requests_client" in sys.modules:
        del sys.modules["requests_client"]
    # import authreq then requests_client
    import authentication_endpoint.authreq  # ensures AuthClient present
    import requests_client
    return authentication_endpoint.authreq, requests_client

@responses.activate
def test_list_requests_and_logging(monkeypatch):
    authreq, requests_client = _import_module(monkeypatch)

    # stub auth token
    responses.add(responses.POST, AUTH_ENV_VARS["CZDS_AUTH_URL"], json={"accessToken": "t", "expiresIn": 3600}, status=200)

    # stub list requests
    sample = [{"id":"r1","tld":"example","status":"PENDING","requestedAt":"2025-01-01T00:00:00Z"}]
    responses.add(responses.GET, "https://czds-api.example.local/czds/requests", json=sample, status=200)

    # capture logs instead of writing to Mongo
    raw_events = []
    monkeypatch.setattr(requests_client, "_log_request_raw", lambda d: raw_events.append(("raw", d)))
    latest_events = []
    monkeypatch.setattr(requests_client, "_upsert_latest", lambda d: latest_events.append(("latest", d)))

    client = requests_client.RequestsClient()
    items = client.list_requests()
    assert isinstance(items, list)
    assert items[0]["id"] == "r1"
    assert any(e[0] == "raw" for e in raw_events)
    assert any(e[0] == "latest" for e in latest_events)

@responses.activate
def test_create_request_and_history(monkeypatch):
    authreq, requests_client = _import_module(monkeypatch)

    # stub auth token
    responses.add(responses.POST, AUTH_ENV_VARS["CZDS_AUTH_URL"], json={"accessToken": "t", "expiresIn": 3600}, status=200)

    # stub create request response
    create_resp = {"id":"r2","tld":"com","status":"PENDING","requestedAt":"2025-01-02T00:00:00Z"}
    responses.add(responses.POST, "https://czds-api.example.local/czds/requests", json=create_resp, status=200)

    raw = []
    hist = []
    latest = []
    monkeypatch.setattr(requests_client, "_log_request_raw", lambda d: raw.append(d))
    monkeypatch.setattr(requests_client, "_append_history", lambda d: hist.append(d))
    monkeypatch.setattr(requests_client, "_upsert_latest", lambda d: latest.append(d))

    client = requests_client.RequestsClient()
    data = client.create_request("com", comment="research")
    assert data["id"] == "r2"
    assert len(raw) == 1
    assert len(hist) == 1
    assert len(latest) == 1

@responses.activate
def test_get_request(monkeypatch):
    authreq, requests_client = _import_module(monkeypatch)
    responses.add(responses.POST, AUTH_ENV_VARS["CZDS_AUTH_URL"], json={"accessToken": "t", "expiresIn": 3600}, status=200)

    sample = {"id":"r3","tld":"net","status":"APPROVED","requestedAt":"2025-01-03T00:00:00Z"}
    responses.add(responses.GET, "https://czds-api.example.local/czds/requests/r3", json=sample, status=200)

    raw = []
    latest = []
    monkeypatch.setattr(requests_client, "_log_request_raw", lambda d: raw.append(d))
    monkeypatch.setattr(requests_client, "_upsert_latest", lambda d: latest.append(d))

    client = requests_client.RequestsClient()
    data = client.get_request("r3")
    assert data["id"] == "r3"
    assert len(raw) == 1
    assert len(latest) == 1