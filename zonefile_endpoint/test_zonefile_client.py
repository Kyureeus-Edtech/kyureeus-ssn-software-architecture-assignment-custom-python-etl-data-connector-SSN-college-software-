import os
import sys
import json
import gzip
import pathlib
import datetime
from io import BytesIO

import responses
import pytest

# Ensure project root is on sys.path for test imports when running from zonefile_endpoint folder
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

AUTH_ENV_VARS = {
    "CZDS_AUTH_URL": "https://auth.example.local/api/authenticate",
    "CZDS_USERNAME": "test-user",
    "CZDS_PASSWORD": "test-pass",
    "CZDS_ZONEFILES_URL": "https://czds-api.example.local/czds/downloads",
    "CZDS_API_BASE": "https://czds-api.example.local",
    "CZDS_ZONE_TIMEOUT_SECONDS": "5",
    "CZDS_ZONE_RETRIES": "1",
}

def _import_module(monkeypatch):
    for k, v in AUTH_ENV_VARS.items():
        monkeypatch.setenv(k, v)
    # reload modules to pick up env
    import importlib
    if "authentication_endpoint.authreq" in sys.modules:
        del sys.modules["authentication_endpoint.authreq"]
    if "authreq" in sys.modules:
        del sys.modules["authreq"]
    if "zonefile_client" in sys.modules:
        del sys.modules["zonefile_client"]
    # import authreq & zonefile_client
    import authentication_endpoint.authreq as authreq
    import zonefile_client
    return authreq, zonefile_client

@responses.activate
def test_list_zonefiles_and_logging(monkeypatch):
    authreq, zonefile_client = _import_module(monkeypatch)

    # mock auth token
    responses.add(responses.POST, AUTH_ENV_VARS["CZDS_AUTH_URL"], json={"accessToken": "tok", "expiresIn": 3600}, status=200)

    # stub list response
    sample = [
        {"tld": "com", "size": 12345, "lastModified": "2025-01-01T00:00:00Z"},
        {"tld": "net", "size": 234, "lastModified": "2025-01-02T00:00:00Z"}
    ]
    responses.add(responses.GET, AUTH_ENV_VARS["CZDS_ZONEFILES_URL"], json=sample, status=200)

    raw = []
    latest = []
    # monkeypatch mongo logging functions so no DB required
    monkeypatch.setattr(zonefile_client, "_log_zone_raw", lambda d: raw.append(d))
    monkeypatch.setattr(zonefile_client, "_upsert_zone_latest", lambda d: latest.append(d))

    client = zonefile_client.ZonefileClient()
    items = client.list_zonefiles()
    assert isinstance(items, list)
    assert len(items) == 2
    assert any(x.get("tld") == "com" for x in items)
    # ensure our patched logging functions were called
    assert len(raw) >= 2
    assert len(latest) >= 2

@responses.activate
def test_download_zonefile_and_logging(monkeypatch, tmp_path):
    authreq, zonefile_client = _import_module(monkeypatch)

    # mock auth
    responses.add(responses.POST, AUTH_ENV_VARS["CZDS_AUTH_URL"], json={"accessToken": "tok", "expiresIn": 3600}, status=200)

    # create gz compressed bytes for a small sample zone file
    sample_text = b"example.com. 3600 IN A 1.2.3.4\n"
    buf = BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
        gz.write(sample_text)
    gz_bytes = buf.getvalue()

    download_url = f"{AUTH_ENV_VARS['CZDS_ZONEFILES_URL']}/com"
    responses.add(responses.GET, download_url, body=gz_bytes, status=200, content_type="application/gzip")

    logged = []
    history = []
    latest = []
    monkeypatch.setattr(zonefile_client, "_log_zone_raw", lambda d: logged.append(d))
    monkeypatch.setattr(zonefile_client, "_append_zone_history", lambda d: history.append(d))
    monkeypatch.setattr(zonefile_client, "_upsert_zone_latest", lambda d: latest.append(d))

    client = zonefile_client.ZonefileClient()
    dest = tmp_path / "downloads"
    dest.mkdir(parents=True, exist_ok=True)
    path = client.download_zonefile("com", str(dest))
    assert path.exists()
    # file should be non-empty
    assert path.stat().st_size > 0
    # verify logged metadata & history
    assert any("download_meta" in r or "raw" in r for r in logged)
    assert len(history) >= 1
    assert len(latest) >= 1

def test_verify_checksum(tmp_path):
    # build a small file
    p = tmp_path / "test.gz"
    content = b"hello world"
    p.write_bytes(content)
    # compute expected
    import hashlib
    h = hashlib.sha256()
    h.update(content)
    expected = h.hexdigest()
    from zonefile_client import verify_checksum
    res = verify_checksum(str(p), expected_hex=expected)
    assert res["match"] is True
    assert res["sha256"] == expected
