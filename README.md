# URLHaus CSV ETL Connector

**Author:** Mugilkrishna D U  
**Roll No:** 3122 22 5001 073  
**Year/Sec:** CSE B  
**Department:** Computer Science & Engineering, SSN College of Engineering

## Overview

This ETL (Extract, Transform, Load) connector framework fetches malware URL data from the **URLHaus CSV API**, transforms it into a MongoDB-friendly JSON format, and loads it into a dedicated MongoDB collection. The connector supports secure environment variable management, basic data cleaning, and timestamp-based ingestion tracking.

## API Details

* **Provider:** Abuse.ch – URLHaus
* **Base URL (CSV Download):** `https://urlhaus.abuse.ch/downloads/csv_online/`
* **CSV Endpoint (GET):** https://urlhaus.abuse.ch/downloads/csv_online/ – downloads CSV data containing recent malicious URLs.
* **JSON API Endpoint (POST):** https://urlhaus.abuse.ch/api/ – accepts a JSON payload { "query": "get_recent" } to retrieve recent data in structured format.
* **Query:** `get_recent`
* **Format:** CSV with comment lines (lines starting with `#`)
* **Documentation:** https://urlhaus.abuse.ch/api/

## Authentication & Security

1. The URLHaus public CSV endpoint does not require authentication.
2. MongoDB credentials are stored in a local `.env` file (not committed to Git, for obvious security reasons).

## MongoDB Storage Strategy

* **Collection Name:** `{CONNECTOR_NAME}_raw` (e.g., `urlhaus_connector_raw`)
* **Primary Fields:**
   * `ingested_at` → Timestamp of ingestion (UTC)
   * All CSV columns mapped directly into document fields

## Transformations Applied

* CSV is parsed into a Pandas DataFrame with comment line filtering
* `ingested_at` field added to each record with UTC timestamp
* Records converted to list of JSON-like dictionaries before loading
* Empty or invalid CSV content is handled gracefully

## Error Handling

* **CSV fetch failure:** Logs error and exits without writing to database
* **Empty CSV content:** Skips transformation and loading steps
* **MongoDB connection errors:** Handled with try/except blocks and logged for debugging
* **Network timeouts:** 30-second timeout configured for API requests

## Testing & Validation

* Verified data load for multiple runs
* Tested behavior with invalid MongoDB URI and the connector exits gracefully
* Tested with network failures and invalid CSV URLs
* Checked insertion counts to confirm data integrity

## Example Input (CSV Row)

```csv
# URLhaus CSV data
id,dateadded,url,url_status,threat,tags,urlhaus_link,reporter
1234567,2025-08-13,https://malicious.example,online,malware,"exe,zip",https://urlhaus.abuse.ch/url/1234567/,researcher
```

## Example Output (MongoDB Document)

```json
{
  "3603095": 3603094,
  "_id": {
    "$oid": "689e1ffb76cdf7ac5f1f395f"
  },
  "2025-08-14 17:29:06": "2025-08-14 17:25:15",
  "http://112.248.140.118:33710/bin.sh": "http://116.138.188.124:33595/bin.sh",
  "online": "online",
  "2025-08-14 17:29:06.1": "2025-08-14 17:25:15",
  "malware_download": "malware_download",
  "32-bit,elf,mips,Mozi": "32-bit,elf,mips,Mozi",
  "https://urlhaus.abuse.ch/url/3603095/": "https://urlhaus.abuse.ch/url/3603094/",
  "geenensp": "geenensp",
  "ingested_at": {
    "$date": "2025-08-14T17:42:19.386Z"
  }
}
```

## Installation & Usage

1. **Clone the repository** and navigate to your project folder.
2. **Create `.env` file** using the template provided:
   ```bash
   cp .env.example .env
   # Edit .env with your specific configuration
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Ensure MongoDB is running** on your system or update `MONGO_URI` in `.env` for remote MongoDB instance.
5. **Run the connector:**
   ```bash
   python url_haus_etl_connector.py
   ```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `CSV_API_URL` | URLHaus CSV endpoint | `https://urlhaus.abuse.ch/downloads/csv_online/` |
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017` |
| `MONGO_DB` | Target database name | `etl_assgn1` |
| `CONNECTOR_NAME` | Prefix for collection names | `urlhaus_connector` |

## Logging

The connector provides informational and error logging to help with debugging:

* `[INFO]` messages for successful operations
* `[ERROR]` messages for failures and exceptions
* Progress indicators for each ETL step
