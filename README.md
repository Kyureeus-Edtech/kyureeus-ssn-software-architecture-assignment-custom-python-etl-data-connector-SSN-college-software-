# NVD CVE ETL Connector

**Author:** Mugilkrishna D U  
**Roll No:** 3122 22 5001 073  
**Year/Sec:** CSE B  
**Department:** Computer Science & Engineering, SSN College of Engineering

## Overview

This ETL (Extract, Transform, Load) connector framework fetches Common Vulnerabilities and Exposures (CVE) data from the **National Vulnerability Database (NVD) API**, transforms it into a MongoDB-friendly JSON format, and loads it into dedicated MongoDB collections. The connector supports both current CVE data and CVE change history, with secure environment variable management, timestamp-based ingestion tracking, and intelligent upsert logic to prevent duplicate entries.

## API Details

### CVE API (`etl_cve.py`)
* **Provider:** National Institute of Standards and Technology (NIST) – NVD
* **Base URL:** `https://services.nvd.nist.gov/rest/json/cves/2.0`
* **Endpoints Used:**
  * By CVE ID: `?cveId=CVE-2019-1010218`
  * By CVSS v3 Severity: `?cvssV3Severity=CRITICAL`
  * By CVSS v2 Metrics: `?cvssV2Metrics=AV:N/AC:H/Au:N/C:C/I:C/A:C`
* **Format:** JSON with nested vulnerability data structure
* **Documentation:** https://nvd.nist.gov/developers/vulnerabilities

### CVE History API (`etl_cve_history.py`)
* **Provider:** National Institute of Standards and Technology (NIST) – NVD
* **Base URL:** `https://services.nvd.nist.gov/rest/json/cvehistory/2.0`
* **Endpoints Used:**
  * By Date Range: `?changeStartDate=2021-08-04T13:00:00.000%2B01:00&changeEndDate=2021-10-22T13:36:00.000%2B01:00`
  * By CVE ID: `?cveId=CVE-2025-0001`
  * Paginated Results: `?resultsPerPage=20&startIndex=0`
* **Format:** JSON with `cveChanges` array containing change records
* **Documentation:** https://nvd.nist.gov/developers/vulnerabilities

## Authentication & Security

1. The NVD public API endpoints do not require authentication for basic usage.
2. MongoDB credentials are stored in a local `.env` file (not committed to Git for security purposes).
3. API requests include a 30-second timeout to prevent indefinite hanging.

## MongoDB Storage Strategy

### CVE Data Collections
* **Collection Naming Pattern:** `{CONNECTOR_NAME}_{endpoint_name}`
  * Examples: `cve_connector_cve_by_id`, `cve_connector_cve_critical_cvssv3`
* **Primary Fields:**
  * `cve.id` → CVE identifier (used as unique key)
  * `ingested_at` → Timestamp of ingestion (UTC)
  * All JSON fields from API response preserved in nested structure

### CVE History Collections
* **Collection Naming Pattern:** `{CONNECTOR_NAME}_{endpoint_name}`
  * Examples: `cve_connector_history_date_range`, `cve_connector_history_by_cveid`
* **Primary Fields:**
  * `cve.id` → CVE identifier (primary unique key when available)
  * `timestamp` + `action` → Fallback composite key for records without CVE ID
  * `ingested_at` → Timestamp of ingestion (UTC)
  * Change details extracted from nested `change` field

## Transformations Applied

### CVE Data (`etl_cve.py`)
* JSON response parsed to extract `vulnerabilities` array
* `ingested_at` field added to each vulnerability record with UTC timestamp
* Nested CVE structure preserved for comprehensive data retention
* Records prepared for bulk upsert operations

### CVE History (`etl_cve_history.py`)
* JSON response parsed to extract `cveChanges` array
* `change` field extracted from each element (drill-down transformation)
* `ingested_at` field added with UTC timestamp
* Composite unique identifiers generated for records without explicit CVE IDs

## Error Handling

* **API fetch failure:** Logs detailed error messages and returns None without crashing
* **Empty or invalid JSON:** Skips transformation and loading steps gracefully
* **Missing expected keys:** Validates presence of required fields before processing
* **MongoDB connection errors:** Handled with try/except blocks and informative error logging
* **Network timeouts:** 30-second timeout configured for all API requests
* **Duplicate prevention:** Upsert logic ensures no duplicate CVE entries across multiple runs

## Upsert Logic

### CVE Data
* **Unique Key:** `cve.cveId` field used as primary identifier
* **Operation:** Updates existing records or inserts new ones based on CVE ID match

### CVE History
* **Primary Key:** `cve.id` when available
* **Fallback Key:** Composite of `timestamp` + `action` for records without CVE ID
* **Operation:** Bulk upsert prevents duplicates while updating changed records

## Testing & Validation

* Verified data load for multiple API endpoints across both scripts
* Tested behavior with invalid MongoDB URI – connector exits gracefully
* Tested with network failures and malformed API URLs
* Confirmed upsert logic prevents duplicate entries on repeated runs
* Validated insertion and modification counts match expected results
* Checked nested field extraction in CVE history transformations

## Example Input (CVE API JSON)

```json
{
  "vulnerabilities": [
    {
      "cve": {
        "id": "CVE-2019-1010218",
        "sourceIdentifier": "josh@bress.net",
        "published": "2019-07-22T18:15:10.837",
        "descriptions": [
          {
            "lang": "en",
            "value": "cherrypy before 18.0.0 is vulnerable to..."
          }
        ]
      }
    }
  ]
}
```

## Example Output (MongoDB Document - CVE)

```json
{
  "_id": {
    "$oid": "689e2a3c8d1f9ba7e3c5d891"
  },
  "cve": {
    "id": "CVE-2019-1010218",
    "sourceIdentifier": "josh@bress.net",
    "published": "2019-07-22T18:15:10.837",
    "descriptions": [
      {
        "lang": "en",
        "value": "cherrypy before 18.0.0 is vulnerable to..."
      }
    ]
  },
  "ingested_at": {
    "$date": "2025-10-21T10:30:45.123Z"
  }
}
```

## Example Input (CVE History API JSON)

```json
{
  "cveChanges": [
    {
      "change": {
        "cve": {
          "id": "CVE-2025-0001"
        },
        "eventName": "Initial Analysis",
        "timestamp": "2025-01-15T08:23:41.000",
        "action": "Added"
      }
    }
  ]
}
```

## Example Output (MongoDB Document - CVE History)

```json
{
  "_id": "CVE-2025-0001",
  "cve": {
    "id": "CVE-2025-0001"
  },
  "eventName": "Initial Analysis",
  "timestamp": "2025-01-15T08:23:41.000",
  "action": "Added",
  "ingested_at": {
    "$date": "2025-10-21T10:32:18.456Z"
  }
}
```

## Installation & Usage

1. **Clone the repository** and navigate to your project folder.

2. **Create `.env` file** with the following variables:
   ```bash
   cp .env.example .env
   # Edit .env with your specific configuration
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ensure MongoDB is running** on your system or update `MONGO_URI` in `.env` for remote MongoDB instance.

5. **Run the CVE connector:**
   ```bash
   python etl_cve.py
   ```

6. **Run the CVE History connector:**
   ```bash
   python etl_cve_history.py
   ```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017` |
| `CVE_DB` | Target database for CVE data | `cve_database` |
| `CVE_HISTORY_DB` | Target database for CVE history | `cve_history_database` |
| `CONNECTOR_NAME` | Prefix for collection names | `cve_connector` |

## Logging

Both connectors provide comprehensive informational and error logging:

* `[INFO]` messages for successful operations and progress updates
* `[WARNING]` messages for empty datasets or skipped operations
* `[ERROR]` messages for failures with detailed exception information
* Progress indicators for each ETL step (Extract, Transform, Load)
* Insertion and modification counts for database operations

## Project Structure

```
.
├── etl_cve.py              # Main CVE data ETL connector
├── etl_cve_history.py      # CVE change history ETL connector
├── .env                    # Environment configuration (not in Git)
├── .env.example            # Template for environment variables
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Dependencies

```
requests>=2.31.0
pymongo>=4.6.0
python-dotenv>=1.0.0
```

## Future Enhancements

* Rate limiting compliance for NVD API (50 requests per rolling 30-second window)
* API key support for higher rate limits (50 requests per 30 seconds with key)
* Incremental loading based on last ingestion timestamp
* Data validation and schema enforcement
* Automated scheduling with cron or task scheduler
* Enhanced error recovery and retry logic