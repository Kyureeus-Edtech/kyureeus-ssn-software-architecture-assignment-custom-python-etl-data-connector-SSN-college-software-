
# Project: MalShare MongoDB ETL

---

## Purpose
Automates the process of collecting malware hash data from MalShare and storing it in MongoDB for further analysis or archiving.

---

## Quick Start

**1. Environment Setup**
	 - Copy your MalShare API key and MongoDB URI into a `.env` file (see `ENV_TEMPLATE` for reference).

**2. Install Requirements**
	 ```bash
	 pip install -r requirements.txt
	 ```

**3. Database**
	 - Ensure MongoDB is running locally or update your `.env` for remote access.

**4. Run Script**
	 ```bash
	 python etl_connector.py
	 ```

---

## Data Example

MongoDB will store documents like:

```json
{
	"md5": "...",
	"sha1": "...",
	"sha256": "...",
	"created_at": "2025-08-14T12:00:00Z"
}
```

---

## MalShare API Details

| Item           | Value/Description                                  |
|----------------|----------------------------------------------------|
| Endpoint       | `https://malshare.com/api.php`                     |
| Method         | `GET`                                              |
| Parameters     | `api_key` (required), `action=getlist` (required)  |
| Auth           | API key in query string                            |
| Request Body   | Not used                                           |
| Headers        | None required                                      |
| Example        | `GET https://malshare.com/api.php?api_key=YOUR_API_KEY&action=getlist` |

**Response Format:**

Returns a JSON array, each object includes:

| Field    | Description         |
|----------|---------------------|
| md5      | MD5 hash            |
| sha1     | SHA1 hash           |
| sha256   | SHA256 hash         |

Sample:
```json
[
	{
		"md5": "f7aa39965451575bebfcd82024b816a1",
		"sha1": "b69e51bc065cefa4be766385cff5234b26883dbc",
		"sha256": "5f2aff691b3a2e9e2e6862e7791199b5a66f20fd9de07fa08c8627e16e1e57de"
	},
	{
		"md5": "c2d2559a0cce7370e3b34d681fbce306",
		"sha1": "204b65cb33c670fed9e28733008f4ad8f26be042",
		"sha256": "4d6a8348229296c6b27032edbbe2f7f682d2b56cffec333f304c87845280747c"
	}
]
```

---

## Notes

- The `getlist` action returns all hashes in one response (no pagination).
- MalShare may enforce rate limits; see their docs for details.
- Invalid or missing API keys will result in an error message from the API.
