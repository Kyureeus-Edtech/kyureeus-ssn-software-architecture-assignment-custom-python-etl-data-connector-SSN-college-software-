# Software Architecture Assignment: Custom Python ETL Data Connector
# Abuse.ch Feeds 

**Student Name:** Diya Seshan 

**Roll Number:** 3122 22 5001 030

**Dept & Year:** CSE-A, 4th year

**Date:** 21-10-2025

## Overview

Python ETL pipeline that:
    - **Extracts** threat intelligence data from Abuse.ch feeds (ThreatFox, FeodoTracker, URLhaus) 
    - **Transforms** into structured MongoDB documents
    - **Loads** into MongoDB with audit fields and deduplication


## API Provider Details
**1. ThreatFox**

Provider: Abuse.ch ThreatFox

Base URL: https://threatfox-api.abuse.ch

Endpoint: /api/v1/

Data Format: JSON

Authentication: Auth-Key via .env

Response Structure: JSON object with IOC data (domains, IPs, malware info)

**2. FeodoTracker**

Provider: Abuse.ch FeodoTracker

Base URL: https://feodotracker.abuse.ch

Endpoint: /downloads/ipblocklist.csv

Data Format: CSV

Authentication: None required

Response Structure: CSV file with IP addresses and first_seen dates

**3. URLhaus**

Provider: Abuse.ch URLhaus

Base URL: https://urlhaus-api.abuse.ch

Endpoint: /browse/tag/json/

Data Format: JSON

Authentication: Optional Auth-Key via .env

Response Structure: JSON object containing recent malicious URLs


## Usage

```bash
python etl_connector.py
```


## Data Structure

**ThreatFox- Sample Output**
```json
{
  "ioc": "maliciousdomain.com",
  "ioc_type": "domain",
  "threat_type": "malware",
  "malware": "Emotet",
  "first_seen": "2025-10-20",
  "last_seen": "2025-10-21",
  "reporter": "anonymous",
  "_ingested_at": "2025-10-21T14:32:00Z",
  "_source": "ThreatFox"
}
```

**FeodoTracker- Sample Output**
```json
{
  "ip": "185.62.188.189",
  "first_seen": "2025-10-20",
  "source": "FeodoTracker",
  "_ingested_at": "2025-10-21T14:32:05Z"
}
```

**URLhaus- Sample Output**
```json
{
  "url": "http://malicioussite.com/bad.exe",
  "host": "malicioussite.com",
  "firstseen": "2025-10-20",
  "status": "online",
  "tags": ["malware", "trojan"],
  "_ingested_at": "2025-10-21T14:32:10Z",
  "_source": "URLhaus"
}
```

## Features

### ETL Pipeline Components

**Extract:**
- HTTP requests with retry logic and timeout handling

- Captures CSV/JSON feeds and HTTP metadata

- Respects rate limits and API rules

**Transform:**

- Parses JSON or CSV formats

- Normalizes field names for MongoDB

- Adds audit fields (ingestion timestamp, source tracking)

**Load:**
- Upserts based on unique identifiers (row hash or IOC)

- Creates indexes for deduplication

- Bulk write operations for efficiency

- Handles MongoDB connectivity issues

### Sample Test Output
```bash
$ python etl_connector.py
INFO:root:Running ThreatFox connector
INFO:root:Inserted 6597 docs into threatfox_raw

INFO:root:Running FeodoTracker connector
INFO:root:FeodoTracker raw response count: 152
INFO:root:Inserted 152 docs into feodotracker_raw

INFO:root:Running URLhaus connector
INFO:root:Inserted 100 docs into urlhaus_raw

INFO:root:ETL run completed successfully
```

## MongoDB Collection Details

**Collections:** `threatfox_raw`, `feodotracker_raw`, `urlhaus_raw`  
**Database:** `abusech_db` (configurable via .env)  
**Indexes:** 
- `ioc`, `ip`, `url` (unique) - for deduplication
- `_ingested_at` - for time-based queries
