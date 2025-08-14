# NVD CVE ETL Connector

This project is a Python ETL (Extract, Transform, Load) pipeline for fetching CVE (Common Vulnerabilities and Exposures) data from the **National Vulnerability Database (NVD)** API, transforming it into a MongoDB-friendly format, and loading it into a MongoDB collection.

---

## 📌 API Details

* **API Provider:** [NVD (National Vulnerability Database)](https://nvd.nist.gov/developers)
* **Base URL:** `https://services.nvd.nist.gov`
* **Endpoint:** `/rest/json/cves/2.0`
* **Authentication:** Optional API key (`apiKey` header). Without an API key, rate limits are much lower.
* **Pagination:**

  * `startIndex` (integer) — starting position of the results
  * `resultsPerPage` (integer, max 2000) — number of results returned per page
* **Rate Limits:**

  * Without API key: \~1 request every 6 seconds
  * With API key: Up to 50 requests per 30 seconds
* **Response Format:** JSON
* **Key Fields Returned:**

  * `cve.id` — CVE Identifier
  * `published` — Publication date
  * `lastModified` — Last modified date
  * `descriptions` — List of vulnerability descriptions by language
  * `metrics` — CVSS scoring data
  * `references` — List of reference URLs

---

## ⚙️ Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

**`requirements.txt` should include:**

```
pymongo
requests
python-dotenv
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root using the template below:

```
# Optional NVD API key for higher rate limits
NVD_API_KEY=your_api_key_here

# API details
BASE_URL=https://services.nvd.nist.gov
API_ENDPOINT=/rest/json/cves/2.0

# MongoDB connection
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=etl_db
COLLECTION_NAME=nvd_raw
```

---

## 🚀 Running the ETL Pipeline

Run the pipeline:

```bash
python etl_connector.py
```

The script will:

1. Extract CVE data from the NVD API
2. Transform it to include only relevant fields for MongoDB
3. Load it into the specified MongoDB collection

---

## 💃 MongoDB Document Example

```json
{
  "cve_id": "CVE-2025-1234",
  "published": "2025-02-10T12:34Z",
  "lastModified": "2025-02-11T10:20Z",
  "description": "Example vulnerability description",
  "severity": "HIGH",
  "score": 8.5,
  "references": ["https://example.com/vuln"],
  "ingestion_timestamp": "2025-08-14T15:30:00Z"
}
```

---

## 🥪 Testing & Validation

* Verify MongoDB insertion by connecting to the database and running:

  ```bash
  mongo
  use etl_db
  db.nvd_raw.findOne()
  ```
* Handle network errors, empty payloads, and rate limits gracefully.
* Use API key to improve request throughput.

