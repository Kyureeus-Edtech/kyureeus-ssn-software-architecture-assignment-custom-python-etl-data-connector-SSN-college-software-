
# RDAP ETL Connector

**Student:** Nisha Ganesh
**Roll Number:** 3122225001084

## Overview

This Python ETL connector fetches data from **RDAP APIs** (Registration Data Access Protocol) and efficiently stores it in a MongoDB database. It is designed for robust extraction of key internet resource data, specifically covering  **domain** ,  **IP address** , and **Autonomous System Number (ASN)** information.

The pipeline includes crucial error handling and data integrity features.

## API Endpoints Used

The connector utilizes the public RDAP bootstrap services via the base URL `https://rdap.org`. The following three key endpoints are targeted:

| Resource Type                     | Endpoint Structure | Example Query                        |
| --------------------------------- | ------------------ | ------------------------------------ |
| **Domain**                  | `/domain/{name}` | `https://rdap.org/domain/iana.org` |
| **IP Address**              | `/ip/{address}`  | `https://rdap.org/ip/8.8.8.8`      |
| **Autonomous System (ASN)** | `/autnum/{asn}`  | `https://rdap.org/autnum/AS15169`  |

## Setup Instructions

### 1. Create `.env` file

A `.env` file is mandatory for securely configuring the connector's behavior and database connection. Create this file in the root directory of your project:

```
MONGO_URI=mongodb://localhost:27017
MONGO_DB=rdap_data
RDAP_BASE=[https://rdap.org](https://rdap.org)
REQUEST_TIMEOUT_SECONDS=20
MAX_RETRIES=5
BACKOFF_FACTOR=1.0
USER_AGENT=rdap-etl/1.0
```

### 2. Install dependencies

Ensure you have all the required Python packages installed to run the script successfully.

```
# Install all required Python packages
pip install requests pymongo python-dotenv
# Alternatively, if a requirements.txt file exists:
# pip install -r requirements.txt
```

## Target Configuration (`config.json`)

The ETL connector uses a `config.json` file to define the list of resources (domains, IPs, and ASNs) to be queried in a single run. 

```
{
  "domains": ["iana.org", "example.com", "github.com", "python.org", "openai.com"],
  "ips": ["8.8.8.8", "1.1.1.1", "52.216.4.4", "34.216.5.6", "192.168.1.1"],
  "autnums": ["AS15169", "AS13335", "AS16509", "AS32934", "AS8075"]
}
```

## Running the ETL Connector

Execute the Python script, passing the configuration file path using the `--targets-file` argument:

```
# Run using the config.json targets file
python etl_connector.py --targets-file config.json
```

## MongoDB Collection 

The ETL process uses the database specified by `MONGO_DB` (e.g., `rdap_data`) and stores data in three distinct collections, one for each resource type:

1. `rdap_domain_raw` 
2. `rdap_ip_raw`
3. `rdap_autnum_raw`

Each document includes an `ingestion_metadata` field detailing the source endpoint, query value, and the time of ingestion to support auditing.

Sample MongoDB Document:

```json
{
  "_id": {
    "$oid": "68f264fb2e3d1ac0f0af733c"
  },
  "source_url": "https://rdap.verisign.com/com/v1/domain/example.com",
  "first_ingested_at": {
    "$date": "2025-10-17T15:47:07.370Z"
  },
  "headers": Object,
  "http_status": 200,
  "ingested_at": {
    "$date": "2025-10-17T15:47:07.370Z"
  },
  "normalized": Object,
  "raw": Object
}
```

## Testing & Validation

The connector implements robust error handling using the following logic:

### Invalid Responses (Non-JSON)

Logs a critical error and raises a `RuntimeError` if the API returns a non-JSON response body.

```
def safe_get(url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    try:
        resp = session.get(url, params=params, timeout=REQUEST_TIMEOUT)
        payload = resp.json()  # Will raise ValueError if response is not JSON
    except ValueError:
        # Non-JSON body
        logger.error("Non-JSON response from %s (status %d): %s", url, resp.status_code, resp.text[:500])
        raise RuntimeError(f"Non-JSON response from {url} (status {resp.status_code})")
    return {"status_code": resp.status_code, "payload": payload, "url": resp.url}
```

### Empty Payloads

Skips the MongoDB insertion step and logs a warning if the API returns a 200 OK status but the response body contains no meaningful data.

```
resp = fetch_domain(domain_name)
if not resp.get("payload"):
    logger.warning("Empty payload for domain %s", domain_name)
    return  # skip insertion into MongoDB
doc = make_document(resp)
connector.upsert_doc("rdap_domain_raw", doc)
```

### Rate Limits (HTTP 429)

Automatically retries the request up to `MAX_RETRIES`. It prioritizes the `Retry-After` header for wait time, falling back to exponential backoff (`BACKOFF_FACTOR * 2^TRIES`).

```
if status == 429:
    # rate-limited: look for Retry-After header
    ra = resp.headers.get("Retry-After")
    wait = int(ra) if ra and ra.isdigit() else BACKOFF_FACTOR * (2 ** (tries - 1))
    logger.warning("Rate limited (429). Retry after %s seconds", wait)
    time.sleep(wait)
    if tries >= MAX_RETRIES:
        raise RuntimeError("Too many 429 responses")
    continue
```

### Connectivity/Network Errors

Handles general `requests.RequestException` errors (like timeouts or DNS failures) by implementing retries with an exponential backoff strategy up to `MAX_RETRIES`.

```
except requests.RequestException as e:
    logger.warning("Request error (try %d): %s", tries, e)
    if tries >= MAX_RETRIES:
        raise
    sleep = BACKOFF_FACTOR * (2 ** (tries - 1))
    logger.info("Sleeping %.1f seconds before retry", sleep)
    time.sleep(sleep)
    continue
```

### MongoDB Consistency (Upsert Logic)

Uses `source_url` as a unique natural key for update operations, preventing duplicate document entries for the same RDAP query. It also records the `first_ingested_at` timestamp only on creation.

```
def upsert_doc(self, collection_name: str, doc: Dict[str, Any]):
    coll = self.db[collection_name]
    source = doc.get("source_url")
    if source:
        result = coll.update_one(
            {"source_url": source},  # natural key
            {"$set": doc, "$setOnInsert": {"first_ingested_at": doc["ingested_at"]}},
            upsert=True,
        )
        logger.info("Upsert into %s matched=%s modified=%s upserted_id=%s", 
                    collection_name, result.matched_count, result.modified_count, result.upserted_id)
    else:
        coll.insert_one(doc)
```

## RDAP API Reference

The RDAP (Registration Data Access Protocol) API provides structured registration data for domains, IPs, and ASNs.

* Official RDAP documentation and public resolver: [https://www.iana.org/rdap](https://www.iana.org/rdap "null")
* RDAP endpoints used in this connector:
  1. Domain: `/domain/{name}`
  2. IP Address: `/ip/{address}`
  3. Autonomous System Number (ASN): `/autnum/{asn}`
