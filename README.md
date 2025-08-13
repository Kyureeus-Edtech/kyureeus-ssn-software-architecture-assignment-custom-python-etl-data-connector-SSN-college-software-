## Name: Nisha Ganesh

## Register Number: 3122 22 5001 084

<hr>

## AbuseIPDB ETL Connector

This project connects to the [AbuseIPDB](https://www.abuseipdb.com/) API to:

1. Retrieve a list of blacklisted IP addresses.
2. Check detailed abuse reports for each IP.
3. Store the results in a MongoDB database.

---

## API Endpoints Used

### **1. Blacklist API**

Retrieves a list of the most reported IP addresses.

**Endpoint:**

GET [https://api.abuseipdb.com/api/v2/blacklist]()

### **2. Check API**

Retrieves detailed information for a given IP address.

**Endpoint:**

GET [https://api.abuseipdb.com/api/v2/check]()

<hr>

<h4>USAGE</h4>

<h5>1. Install dependencies</h5>

pip install -r requirements.txt

<h5>2. Create .env file</h5>

```
ABUSEIPDB_API_KEY=your_api_key_here
MONGODB_URI=your_mongo_uri
MONGO_DB_NAME=abuseipdb
MONGO_COLLECTION_NAME=abuseipdb_raw
```

<h5>3. Run the ETL pipeline</h5>

python main.py

<hr>

<h4>Sample Data Inserted in MongoDB</h4>

```
{
  "_id": {
    "$oid": "689b5c73ab1d4ad44190c9e3"
  },
  "ipAddress": "170.79.37.82",
  "isPublic": true,
  "ipVersion": 4,
  "isWhitelisted": false,
  "abuseConfidenceScore": 100,
  "countryCode": "PE",
  "usageType": "Fixed Line ISP",
  "isp": "Telefonica del Peru S.A.A.",
  "domain": "telefonica.com.pe",
  "hostnames": [],
  "isTor": false,
  "totalReports": 2058,
  "numDistinctUsers": 585,
  "lastReportedAt": "2025-08-12T15:20:14+00:00",
  "ingested_at": {
    "$date": "2025-08-12T15:23:24.344Z"
  },
  "ingestedAt": "2025-08-12T15:23:24.344164+00:00"
}
```

<hr>

<h3>Error Handling Code</h3>

<h5>1. Invalid Response</h5>

```python
if not blacklist_data or not isinstance(blacklist_data, list):
    logging.warning("[Warning] Blacklist API returned no data or invalid format.")
    return
```

<h5>2. Empty Payload</h5>

```python
if details is None:
    logging.warning(f"[Warning] No response for {ip}, skipping.")
    continue
```

<h5>3. Rate Limits</h5>

```python
if isinstance(details, dict) and details.get("errors"):
    error_msg = details["errors"][0].get("detail", "").lower()
    if "rate limit" in error_msg:
        logging.warning("[Warning] Rate limit hit, sleeping...")
        time.sleep(RATE_LIMIT_SLEEP)
        continue
```

<h5>4. Connectivity Errors</h5>

```python
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    ...
    client.admin.command('ping')
except Exception as e:
    logging.error(f"[Error] Could not connect to MongoDB: {e}")
    return
```

<hr>

<h4>Assignment Outcomes</h4>

* A data provider was identified (AbuseIPDB Connector) and the API documentation, endpoints and authentication were studied.
* A .env file was created to store API keys and secrets and environment variables were loaded using required libraries.
* An ETL pipeline was designed to connect to the API and collect data.
* This data was transformed and stored in a MongoDB collection.
* The pipeline was designed to include various error handlers for successful working.
