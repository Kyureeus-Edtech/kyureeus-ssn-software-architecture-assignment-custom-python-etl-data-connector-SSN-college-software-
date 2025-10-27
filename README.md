# CZDS ICANN Authentication Client – Python ETL Connector

**SSN College of Engineering — Software Architecture Assignment**
Kyureeus EdTech Program (Custom Data Connector – Authentication Endpoint)

---

## Overview

This repository implements a secure Python authentication client for the [ICANN CZDS](https://czds.icann.org) API — forming the first stage of a custom ETL pipeline.

It performs secure API authentication, manages tokens, and logs every authentication event to MongoDB for audit and observability.

---

## Features

* Secure authentication via `.env` (no hard-coded credentials)
* Thread-safe token caching and auto-refresh
* Retry with exponential backoff for transient errors
* MongoDB audit logging of success/failure events
* Full pytest suite for reliability
* TTL-based cleanup of Mongo audit logs

---

## Project Structure

```
/czds-auth-connector/
├── authreq.py           # Main authentication client
├── test_authreq.py      # Unit tests (pytest + responses)
├── .env.example         # Template environment file (copy as .env)
├── requirements.txt     # Dependencies
└── README.md            # Documentation
```

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/<your-username>/czds-auth-connector.git
cd czds-auth-connector
pip install -r requirements.txt
```

### 2. Configure environment

Create a file named `.env` in the root directory:

```ini
# ICANN CZDS Credentials
CZDS_USERNAME=your_icann_email
CZDS_PASSWORD=your_icann_password
CZDS_AUTH_URL=https://account-api.icann.org/api/authenticate

# MongoDB Audit Logging
MONGO_URI=mongodb://localhost:27017
MONGO_DB=czds_connectors
MONGO_AUTH_COLLECTION=czds_auth

# Timeout & Retry
CZDS_AUTH_TIMEOUT_SECONDS=15
CZDS_AUTH_RETRIES=3
```

> Do **not** commit your `.env` file to GitHub.
> A `.env.example` file is included as a safe template.

---

## Running the Authentication Client

```bash
python authreq.py
```

Example output:

```
Starting CZDS authentication test...
INFO:__main__:Authenticated successfully; token valid until Tue Oct 21 23:14:17 2025

Authentication successful.
Token preview: eyJraWQiOi...
Token expires at: 2025-10-21 17:44:17.380250+00:00
```

---

## MongoDB Logging

Every authentication attempt is recorded in MongoDB under `czds_auth`.

Example document:

```json
{
  "ingested_at": "2025-10-21T17:25:00Z",
  "username": "you@example.com",
  "status": "success",
  "http_status": 200,
  "token_length": 206,
  "expires_at": "2025-10-21T18:25:00Z",
  "source": "czds_auth"
}
```

Optional TTL index setup:

```python
from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
db = client["czds_connectors"]
db.czds_auth.create_index("ingested_at", expireAfterSeconds=30*24*3600)
```

---

## Testing

Run all tests:

```bash
pytest -v
```

Expected results:

```
collected 6 items
All tests passed
```

Tests use the `responses` library to simulate API calls and monkeypatch Mongo logging, so no real network or database access occurs.

---

## Submission Checklist

* [x] `.env` file created (securely, not committed)
* [x] Authentication client implemented (`authreq.py`)
* [x] MongoDB audit logging functional
* [x] All tests pass with `pytest -v`
* [x] README.md included with usage instructions
* [x] Branch pushed and Pull Request submitted with name and roll number

---

# CZDS Requests Management Endpoint (`requests_client.py`)

## 📘 Overview

This module implements the **Requests Management Endpoint** of the **ICANN Centralized Zone Data Service (CZDS) API**.

It allows authenticated users to:

* **List existing zone file requests**
* **Create new zone file access requests**
* **Retrieve details of a specific request**

The implementation is **secure, fault-tolerant, and MongoDB-integrated**, fully aligned with ICANN CZDS API structure and compliant with the guidelines in the submission checklist.

It integrates seamlessly with the **Authentication Endpoint (`authreq.py`)** to reuse access tokens and store audit trails.

---

## 🏷️ Directory Structure

```
Assign 2/
├── authentication_endpoint/
│   ├── authreq.py
│   └── test_authreq.py
└── requests_endpoint/
    ├── requests_client.py
    └── test_requests_client.py
```

---

## ⚙️ Environment Variables

The following environment variables must be defined in your `.env` file at the project root:

| Variable                   | Description                                          | Example                                    |
| -------------------------- | ---------------------------------------------------- | ------------------------------------------ |
| `CZDS_API_BASE`            | Base URL for the ICANN CZDS API                      | `https://czds-api.icann.org`               |
| `CZDS_REQUESTS_URL`        | Full URL for the Requests endpoint                   | `https://czds-api.icann.org/czds/requests` |
| `CZDS_REQ_TIMEOUT_SECONDS` | HTTP request timeout (seconds)                       | `20`                                       |
| `CZDS_REQ_RETRIES`         | Max number of retries for transient errors           | `3`                                        |
| `MONGO_REQS_RAW`           | MongoDB collection for raw request logs              | `czds_requests_raw`                        |
| `MONGO_REQS_LATEST`        | MongoDB collection for the latest normalized entries | `czds_requests_latest`                     |
| `MONGO_REQS_HISTORY`       | MongoDB collection for request history               | `czds_requests_history`                    |
| `CZDS_DEBUG`               | Enables verbose logging when set to `true`           | `true`                                     |

Additionally, the authentication endpoint (`authreq.py`) requires its own `.env` configuration for:
`CZDS_AUTH_URL`, `CZDS_USERNAME`, `CZDS_PASSWORD`, and Mongo connection settings.

---

## 🧬 Functional Overview

| Functionality                  | Method                    | Description                                           |
| ------------------------------ | ------------------------- | ----------------------------------------------------- |
| `list_requests()`              | `GET /czds/requests`      | Fetches and logs all accessible requests              |
| `create_request(tld, comment)` | `POST /czds/requests`     | Creates a new zone file access request                |
| `get_request(request_id)`      | `GET /czds/requests/{id}` | Retrieves details of a single request                 |
| CLI `--wait` mode              | optional flag             | Polls `list_requests()` until the new request appears |

All functions include:

* Retry with exponential backoff on transient errors
* Robust JSON and empty-body handling
* MongoDB logging for every response or fallback
* Full token management reuse from `AuthClient`

---

## 🧪 MongoDB Collections

| Collection              | Purpose                                                          | Sample Fields                                                                           |
| ----------------------- | ---------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `czds_requests_raw`     | Stores raw responses, HTTP metadata, headers, and debug payloads | `{ "response_status": 200, "response_headers": {...}, "response_text_preview": "..." }` |
| `czds_requests_latest`  | Tracks the most recent normalized entry for each `request_id`    | `{ "request_id": "r123", "tld": "com", "status": "PENDING" }`                           |
| `czds_requests_history` | Logs all state changes and events for auditing                   | `{ "event": "created", "payload": {...}, "ingested_at": <timestamp> }`                  |

You can inspect these in **MongoDB Compass** by connecting to your local or cloud database and browsing the collections.

Example filter in Compass to find a TLD’s recent activity:

```json
{ "raw.tld": "com" }
```

---

## 🧮 Command-Line Interface (CLI)

`requests_client.py` provides a simple CLI for manual testing or integration.

### ✅ List Requests

```bash
python requests_client.py list --limit 50
```

Fetches a list of the most recent requests and writes to MongoDB.

---

### 🆕 Create a New Request

```bash
python requests_client.py create com --comment "research"
```

Creates a new request for the `.com` zone.

If the API returns an empty body (which is common for successful POSTs), a structured fallback response is returned:

```json
{
  "status_code": 200,
  "message": "empty body (no JSON)",
  "source": "czds_requests_raw"
}
```

---

### ⏳ Create and Wait for Confirmation

```bash
python requests_client.py create com --comment "testing" --wait --wait-seconds 180 --poll-interval 5
```

This command will poll `list_requests()` every 5 seconds for up to 3 minutes until the new `.com` request appears, then display it.

---

### 🔍 Get a Specific Request

```bash
python requests_client.py get <request_id>
```

Retrieves the full details of a specific request and stores it in MongoDB collections.

---

## 🤖 Logging and Error Handling

* All operations are logged with timestamps and HTTP statuses.
* Non-JSON or empty-body responses are logged as structured fallback entries.
* MongoDB logging ensures traceability of all requests and responses.
* Transient failures (network resets, timeouts, etc.) are automatically retried with exponential backoff.

Example logs:

```
INFO:authentication_endpoint.authreq:Authenticated successfully; token valid until 2025-10-21 23:59:59
WARNING:__main__:create_request: non-JSON body returned (status 200). Returning fallback.
```

---

## 🔧 Testing

Run all endpoint tests from the project root:

```bash
pytest -q
```

Expected output:

```
collected 9 items

authentication_endpoint/test_authreq.py .......
requests_endpoint/test_requests_client.py ...

=================== 9 passed in 0.90s ===================
```

---

## 🔋 MongoDB Verification

To verify that requests are being logged, open **MongoDB Compass** and filter:

```json
{ "request_attempt_body.tld": "com" }
```

Check that new entries appear in:

* `czds_requests_raw`
* `czds_requests_latest`
* `czds_requests_history`

---

## 🔐 Integration with Authentication Endpoint

This module imports the `AuthClient` class and `request_with_auth()` helper from `authentication_endpoint/authreq.py`.
Tokens are refreshed and reused automatically across endpoints.

If you restructure folders, ensure imports remain valid:

```python
from authentication_endpoint.authreq import AuthClient, request_with_auth
```

If you run from the `requests_endpoint` folder, the module automatically adjusts the path using:

```python
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)
```

---

## 🛠️ Troubleshooting

| Symptom                                        | Cause                                      | Fix                                                            |
| ---------------------------------------------- | ------------------------------------------ | -------------------------------------------------------------- |
| `empty body (no JSON)`                         | API returns HTTP 200 with empty response   | Use `--wait` mode or poll `list_requests()` manually           |
| `401 Unauthorized`                             | Expired or invalid token                   | Re-run authentication endpoint to refresh token                |
| `ModuleNotFoundError: authentication_endpoint` | Incorrect run path                         | Run from project root or ensure sys.path includes project base |
| Mongo not updating                             | Missing or misconfigured `.env` Mongo vars | Verify Mongo connection and DB name                            |

---

## 📝 Summary

* **Secure, fault-tolerant CZDS Requests Management endpoint** with full MongoDB audit logging.
* Handles ICANN’s common 200-empty responses gracefully.
* Integrates authentication seamlessly and supports automatic polling with `--wait` mode.
* Fully tested via `pytest` (unit + integration).

---

# CZDS Zone File Download Endpoint (`zonefile_client.py`)

## 📘 Overview

This module implements the **Zone File Download Endpoint** of the **ICANN Centralized Zone Data Service (CZDS) API**. It provides functionality for authenticated users to:

* **List all available zone files** they are authorized to access.
* **Download specific zone files** (e.g., `.com`, `.net`, etc.) in compressed format.
* **Verify integrity** of downloaded zone files via SHA-256 checksum.

It integrates seamlessly with the **Authentication Endpoint (`authreq.py`)** and **Requests Management Endpoint (`requests_client.py`)** to ensure a complete data access workflow for CZDS.

All operations are **secure**, **fault-tolerant**, and **fully logged** into MongoDB collections for audit and monitoring.

---

## 🏷️ Directory Structure

```
Assign 2/
├── authentication_endpoint/
│   ├── authreq.py
│   └── test_authreq.py
├── requests_endpoint/
│   ├── requests_client.py
│   └── test_requests_client.py
└── zonefile_endpoint/
    ├── zonefile_client.py
    └── test_zonefile_client.py
```

---

## ⚙️ Environment Variables

The following entries must be added to the project root `.env` file:

| Variable                    | Description                                 | Example                                     |
| --------------------------- | ------------------------------------------- | ------------------------------------------- |
| `CZDS_API_BASE`             | Base URL for ICANN CZDS API                 | `https://czds-api.icann.org`                |
| `CZDS_ZONEFILES_URL`        | Full URL for the Zone File endpoint         | `https://czds-api.icann.org/czds/downloads` |
| `CZDS_ZONE_TIMEOUT_SECONDS` | Timeout for HTTP requests                   | `30`                                        |
| `CZDS_ZONE_RETRIES`         | Max retries for transient errors            | `3`                                         |
| `MONGO_ZONEFILES_RAW`       | MongoDB collection for raw logs             | `czds_zonefiles_raw`                        |
| `MONGO_ZONEFILES_LATEST`    | MongoDB collection for latest file metadata | `czds_zonefiles_latest`                     |
| `MONGO_ZONEFILES_HISTORY`   | MongoDB collection for download history     | `czds_zonefiles_history`                    |
| `CZDS_DEBUG`                | Enables verbose logging                     | `true`                                      |

The authentication `.env` variables (`CZDS_AUTH_URL`, `CZDS_USERNAME`, `CZDS_PASSWORD`) must also be configured for token generation.

---

## 🧬 Functional Overview

| Functionality                      | Method                       | Description                                |
| ---------------------------------- | ---------------------------- | ------------------------------------------ |
| `list_zonefiles()`                 | `GET /czds/downloads`        | Lists available zone files with metadata   |
| `download_zonefile(tld, dest_dir)` | `GET /czds/downloads/{tld}`  | Downloads compressed zone file (`.txt.gz`) |
| `verify_checksum(path, expected)`  | Local                        | Computes or validates file checksum        |
| CLI commands                       | `list`, `download`, `verify` | User-friendly command-line interaction     |

All functions are protected by token authentication and have retry with exponential backoff.

---

## 🧪 MongoDB Collections

| Collection               | Purpose                                        | Sample Fields                                                                        |
| ------------------------ | ---------------------------------------------- | ------------------------------------------------------------------------------------ |
| `czds_zonefiles_raw`     | Logs raw responses, file metadata, and headers | `{ "download_meta": {"tld": "com", "file_size": 12345}, "response_headers": {...} }` |
| `czds_zonefiles_latest`  | Tracks latest downloaded file per TLD          | `{ "tld": "com", "file_path": "...", "sha256": "...", "file_size": 12345 }`          |
| `czds_zonefiles_history` | Records all historical downloads               | `{ "tld": "com", "event": "downloaded", "status": "success" }`                       |

Indexes:

```javascript
db.czds_zonefiles_latest.createIndex({ "tld": 1 }, { unique: true })
db.czds_zonefiles_raw.createIndex({ "ingested_at": 1 }, { expireAfterSeconds: 7776000 }) // 90 days
db.czds_zonefiles_history.createIndex({ "ingested_at": 1 }, { expireAfterSeconds: 31536000 }) // 1 year
```

---

## 🧮 Command-Line Interface (CLI)

`zonefile_client.py` can be executed from the command line with the following subcommands:

### 🔍 List Available Zone Files

```bash
python zonefile_client.py list
```

**Example Output:**

```json
[
  { "tld": "com", "size": 1234567, "lastModified": "2025-10-21T10:00:00Z" },
  { "tld": "net", "size": 2345678, "lastModified": "2025-10-21T10:05:00Z" }
]
```

---

### 🔄 Download a Zone File

```bash
python zonefile_client.py download com --dest ./downloads
```

**Output:**

```
INFO:authentication_endpoint.authreq:Authenticated successfully; token valid until Wed Oct 22 00:00:00 2025
Saved to: downloads/com.txt.gz
```

MongoDB logs are automatically written to all three collections.

---

### 🔎 Verify a Downloaded File

```bash
python zonefile_client.py verify ./downloads/com.txt.gz
```

**Output:**

```json
{
  "path": "C:\\Users\\preet\\downloads\\com.txt.gz",
  "sha256": "abc123..."
}
```

To compare with an expected checksum:

```bash
python zonefile_client.py verify ./downloads/com.txt.gz --sha256 abc123...
```

**Output:**

```json
{
  "path": "...",
  "sha256": "abc123...",
  "match": true
}
```

---

## 🔖 Testing

### Run All Zone File Tests

```bash
pytest -q zonefile_endpoint/test_zonefile_client.py
```

Expected Output:

```
collected 3 items
zonefile_endpoint/test_zonefile_client.py ... [100%]
```

### What the Tests Cover

* Token authentication reuse
* Zone file listing (mocked JSON)
* Zone file downloading (mocked binary .gz)
* Checksum verification logic
* MongoDB logging simulation

---

## 🔋 MongoDB Verification

To check logged documents in **MongoDB Compass**:

1. Connect to your MongoDB instance.
2. Open your working database (e.g., `czds_connectors`).
3. Explore collections:

   * `czds_zonefiles_raw`
   * `czds_zonefiles_latest`
   * `czds_zonefiles_history`
4. Use filters like:

   ```json
   { "download_meta.tld": "com" }
   ```

   or

   ```json
   { "event": "downloaded" }
   ```

---

## 🔧 Integration with Authentication Endpoint

This module depends on `AuthClient` and `request_with_auth` from `authentication_endpoint/authreq.py`.

Token refresh and authentication are fully managed. Example import:

```python
from authentication_endpoint.authreq import AuthClient, request_with_auth
```

If you run directly from the `zonefile_endpoint` folder, the script automatically adjusts `sys.path` to ensure imports work.

---

## 🔐 Troubleshooting

| Symptom                              | Cause                            | Solution                             |
| ------------------------------------ | -------------------------------- | ------------------------------------ |
| `Missing required env var`           | `.env` missing or incorrect path | Place `.env` in project root         |
| `Failed to write czds_zonefiles_raw` | MongoDB not running              | Start MongoDB and check `MONGO_URI`  |
| `401 Unauthorized`                   | Expired token                    | Re-run authentication endpoint       |
| `empty body (no JSON)`               | API returned empty success       | Zone file might not yet be available |

---

## 📝 Summary

* Complete **CZDS Zone File Download Client** for listing, downloading, and verifying zone files.
* Secure authentication with automatic token reuse.
* Robust error handling and exponential retry.
* Full audit logging to MongoDB (raw, latest, history).
* Tested, production-ready, and compliant with ICANN CZDS API.

---

## Author

**Name:** Preethi Prative
**Roll Number:** 3122 22 5001 098
**Department:** Computer Science & Engineering
**Institution:** SSN College of Engineering

---

## License

This project is for educational purposes under the Kyureeus EdTech – SSN Software Architecture course.
No commercial redistribution or credential sharing is permitted.