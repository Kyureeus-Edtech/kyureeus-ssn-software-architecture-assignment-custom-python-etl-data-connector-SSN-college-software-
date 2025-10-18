# Wayback Machine ETL Connectors

## Overview
This repository contains three ETL connectors that interact with the Internet Archive's Wayback Machine APIs. Each connector extracts data, transforms it for MongoDB compatibility, and loads it into dedicated MongoDB collections.

- Availability Connector (`etl_connector1.py`): checks for the closest archived snapshot of a URL.
- CDX Search Connector (`etl_connector2.py`): retrieves historical snapshot metadata via the CDX API.
- Save Page Now Connector (`etl_connector3.py`): requests the Wayback Machine to archive a live page now and stores the result link.

## Setup Instructions
1. Copy `ENV_TEMPLATE` to `.env` and fill in values for MongoDB and Wayback endpoints/collections:
	 - MongoDB
		 - `MONGO_URI`
		 - `MONGO_DB`
		 - `MONGO_COLLECTION_AVAILABILITY`
		 - `MONGO_COLLECTION_CDX`
		 - `MONGO_COLLECTION_SAVE`
	 - Wayback
		 - `WAYBACK_BASE_URL` (e.g., `https://archive.org`)
		 - `WAYBACK_CDX_BASE_URL` (e.g., `https://web.archive.org/cdx/search/cdx`)
		 - `WAYBACK_SAVE_BASE_URL` (e.g., `https://web.archive.org`)
2. Install dependencies:
	 ```
	 pip install -r requirements.txt
	 ```
3. Start MongoDB locally or provide a remote connection string in the `.env` file.

---

## Availability ETL Connector (`etl_connector1.py`)

### Overview
Checks the Wayback Machine for the closest available archived snapshot for each input URL and saves a summary document to MongoDB.

### Run
```
python etl_connector1.py
```

### Example Output (MongoDB document)
```
{
	"url": "https://example.com",
	"queried_at": "2025-10-18T12:00:00Z",
	"timestamp_requested": "20250101",
	"tag": null,
	"snapshot_status": "200",
	"snapshot_url": "https://web.archive.org/web/20250101000000/https://example.com/",
	"snapshot_timestamp": "20250101000000"
}
```

### Wayback Availability API Details
- Base URL: `{WAYBACK_BASE_URL}/wayback/v1/available`
- HTTP Method: `GET`
- Query Parameters used by this connector:
	- `url` (required): Target URL to check.
	- `timestamp` (optional): A YYYYMMDDhhmmss (or prefix) timestamp hint.
	- `closest` (optional): Strategy for selecting snapshot (e.g., `either`).
	- `status_code` (optional): Optional filter passed through by the connector.
	- `tag` (optional): Optional metadata passed through by the connector.
- Request Body: None (parameters are sent as query params)
- Headers: None required
- Authentication: None
- Example Request:
	```
	GET {WAYBACK_BASE_URL}/wayback/v1/available?url=https://example.com&timestamp=20250101
	```
- Response Format (excerpt):
	```json
	{
		"archived_snapshots": {
			"closest": {
				"status": "200",
				"url": "https://web.archive.org/web/20250101000000/https://example.com/",
				"timestamp": "20250101000000"
			}
		}
	}
	```

Notes:
- The connector transforms the response into a flat MongoDB document with `queried_at` and requested timestamp.
- Actual available parameters or response fields may vary; see Internet Archive docs for details.

---

## CDX Search ETL Connector (`etl_connector2.py`)

### Overview
Queries the CDX API to list historical snapshots for a URL within a time range, then stores normalized records to MongoDB.

### Run
```
python etl_connector2.py
```

### Example Output (MongoDB documents)
```
[
	{
		"url": "https://example.com",
		"queried_at": "2025-10-18T12:00:00Z",
		"timestamp": "20230615094500",
		"original": "https://example.com/",
		"statuscode": "200"
	},
	{
		"url": "https://example.com",
		"queried_at": "2025-10-18T12:00:00Z",
		"timestamp": "20220101010101",
		"original": "https://example.com/",
		"statuscode": "200"
	}
]
```

### CDX API Endpoint Details
- Base URL: `{WAYBACK_CDX_BASE_URL}` (e.g., `https://web.archive.org/cdx/search/cdx`)
- HTTP Method: `GET`
- Query Parameters used by this connector:
	- `url` (required): Target URL or URL pattern.
	- `from` (optional): Start timestamp (YYYYMMDD or YYYYMMDDhhmmss).
	- `to` (optional): End timestamp (YYYYMMDD or YYYYMMDDhhmmss).
	- `filter` (optional): One or more filters, e.g. `statuscode:200`.
	- `fl` (optional): Fields list, e.g. `timestamp,original,statuscode`.
	- `collapse` (optional): Collapse strategy, e.g. `digest` to deduplicate.
	- `output` (optional): Response format, set to `json` by this connector.
- Request Body: None
- Headers: None required
- Authentication: None
- Example Request:
	```
	GET {WAYBACK_CDX_BASE_URL}?url=example.com&from=20000101&to=20250101&filter=statuscode:200&fl=timestamp,original,statuscode&collapse=digest&output=json
	```
- Response Format: JSON array of rows. This connector expects either objects with keys or arrays in the order of requested fields.

Notes:
- The connector normalizes each row into a document with `url`, `queried_at`, `timestamp`, `original`, and `statuscode`.
- CDX can return large result sets; consider adding additional filters or date bounds.

---

## Save Page Now ETL Connector (`etl_connector3.py`)

### Overview
Requests the Wayback Machine to archive a live URL immediately (Save Page Now) and stores the resulting archive URL and status in MongoDB.

### Run
```
python etl_connector3.py
```

### Example Output (MongoDB document)
```
{
	"url": "https://example.com",
	"archive_url": "https://web.archive.org/save/https://example.com",
	"response_status": 200,
	"saved_at": "2025-10-18T12:00:00Z"
}
```

### Save Page Now API Details
- Base URL: `{WAYBACK_SAVE_BASE_URL}/save/`
- HTTP Method: `POST`
- Query Parameters used by this connector:
	- `url` (required): The live URL to archive now.
	- `tags` (optional): Optional metadata tags to associate.
- Request Body: None (parameters are sent as query params)
- Headers: `User-Agent` is supported and recommended (the connector allows configuring it).
- Authentication: None required for basic usage; heavy use may be rate limited.
- Example Request:
	```
	POST {WAYBACK_SAVE_BASE_URL}/save/?url=https://example.com
	```
- Response Format: The service may redirect or return headers; this connector records the final response URL and status code.

Notes:
- Saving pages can be rate limited. Consider backoff/retry strategies for larger batches.
- Some URLs may be disallowed by site robots, legal restrictions, or Wayback policies.

---

## Notes and Troubleshooting
- These connectors use configuration modules under `config/` that read values defined in `.env`.
- Ensure your MongoDB instance is reachable from where you run the scripts.
- If you encounter HTTP 429 or other rate-limit errors, reduce request rate or add delays.
- Collections used by default (override in config):
	- Availability: `MONGO_COLLECTION_AVAILABILITY`
	- CDX: `MONGO_COLLECTION_CDX`
	- Save: `MONGO_COLLECTION_SAVE`

## License
For academic use as part of the Software Architecture assignment. Review Internet Archive Terms of Use before running against public endpoints.

