# MalShare ETL Connector

## Overview
This connector extracts malware hash data from the MalShare API, transforms it for MongoDB compatibility, and loads it into a MongoDB collection.

## Setup Instructions
1. Add your MalShare API key and MongoDB URI to a `.env` file based on the ENV_TEMPLATE
2. Install dependencies:
	 ```
	 pip install -r requirements.txt
	 ```
3. Start MongoDB locally or provide connection details in the `.env` file.
4. Run the connector:
	 ```
	 python etl_connector.py
	 ```

## Example Output
Documents inserted into MongoDB will look like:
```
{
	"md5": "...",
	"sha1": "...",
	"sha256": "...",
	"ingested_at": "2025-08-14T12:00:00Z"
}
```

## MalShare API Endpoint Details

- **Base URL:** `https://malshare.com/api.php`
- **HTTP Method:** `GET`
- **Query Parameters:**
	- `api_key` (required): Your MalShare API key. Example: `api_key=0ea8ebf...`
	- `action` (required): The action to perform. For listing hashes, use `action=getlist`.
	- Other actions (not used in this connector) may include `getfile`, `search`, etc. See MalShare docs for more.
- **Request Body:** None (all parameters are sent as query params)
- **Headers:** No special headers required for this endpoint.
- **Authentication:** API key passed as a query parameter.
- **Example Request:**
	```
	GET https://malshare.com/api.php?api_key=YOUR_API_KEY&action=getlist
	```
- **Response Format:** JSON array of objects, each with:
	- `md5`: MD5 hash of the malware sample
	- `sha1`: SHA1 hash
	- `sha256`: SHA256 hash
	Example response:
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

**Notes:**
- No pagination is supported for `getlist` (all results returned at once).
- Rate limits may apply; check MalShare documentation for details.
- If the API key is invalid or missing, the response will be an error message.
