# Software Architecture Assignment: Custom Python ETL Data Connector
# DShield Top Attackers ETL Connector

**Student Name:** Diya Seshan 
**Roll Number:** 3122 22 5001 030 
**Dept & Year:** CSE-A, 4th year
**Date:** 13-08-2025

## Overview

Python ETL pipeline that:
    - **Extracts** daily Top Attackers feed from DShield 
    - **Transforms** into structured MongoDB documents
    - **Loads** into MongoDB with audit fields and deduplication


## API Provider Details

**Provider:** DShield (SANS Internet Storm Center)  
**Base URL:** https://www.dshield.org  
**Endpoint:** `/ipsascii.html`  
**Data Format:** ASCII/TXT (whitespace-delimited table)  
**Authentication:** None required (public feed)  
**Response Structure:** Text-based table with IP addresses and attack statistics

### API Documentation Summary
- **Headers:** Standard HTTP headers, no special authentication required
- **Query Parameters:** None
- **Pagination:** Single feed file (no pagination)
- **Response Format:** ASCII text with tab/space delimited columns
- **Update Frequency:** Daily updates


## Usage

### Test Run (No Database Writes)
```bash
python etl_connector.py --dry-run
```

### Production Run
```bash
python etl_connector.py
```

### Limit Records (for testing)
```bash
python etl_connector.py --limit 10
```

## Data Structure

### Input Format (DShield Feed)
The DShield feed contains lines like:
```
# DShield Top Attackers Report
# Date: 2024-12-XX
IP_Address    Reports    Targets    First_Seen    Last_Seen
192.168.1.1   150        45         2024-12-01    2024-12-15
10.0.0.1      89         23         2024-12-02    2024-12-14
```

### Output Format (MongoDB Documents)
```json
{
  "_id": "ObjectId(...)",
  "ip": "192.168.1.1",
  "reports": "150",
  "targets": "45",
  "first_seen": "2024-12-01",
  "last_seen": "2024-12-15",
  "_ingested_at": "2024-12-15T10:30:00.123456+00:00",
  "_source": "dshield_top_attackers",
  "_source_url": "https://www.dshield.org/ipsascii.html",
  "_source_row": "192.168.1.1   150        45         2024-12-01    2024-12-15",
  "_row_hash": "abc123...",
  "_http_meta": {
    "etag": "\"abc123\"",
    "last_modified": "Mon, 15 Dec 2024 10:00:00 GMT",
    "content_length": "2048",
    "content_type": "text/plain"
  }
}
```

## Features

### ETL Pipeline Components

**Extract:**
- HTTP requests with retry logic and timeout handling
- Respects rate limits with exponential backoff
- Captures HTTP metadata (ETag, Last-Modified, etc.)

**Transform:**
- Parses ASCII table format with flexible column detection
- Extracts and validates IPv4 addresses
- Normalizes field names for MongoDB compatibility
- Adds audit fields (ingestion timestamp, source tracking)

**Load:**
- Upserts based on row hash for idempotent operations
- Creates unique indexes for deduplication
- Bulk write operations for efficiency
- Error handling for MongoDB connection issues

## Testing & Validation

### Test Scenarios Covered
- Valid API responses
- Empty payloads
- Malformed data
- Network timeouts
- Rate limiting
- MongoDB connection issues
- Duplicate data handling

### Sample Test Output
```bash
$ python etl_connector.py --dry-run --limit 3
[INFO] Extracted 3 rows from https://www.dshield.org/ipsascii.html
[DRY-RUN] Preview of transformed docs:
  1. {'ip': '192.168.1.1', '_ingested_at': '2024-12-15T10:30:00.123456+00:00', '_row_hash': 'abc123...', '_source_row': '192.168.1.1   150        45         2024-12-01    2024-12-15'}
  2. {'ip': '10.0.0.1', '_ingested_at': '2024-12-15T10:30:00.123456+00:00', '_row_hash': 'def456...', '_source_row': '10.0.0.1      89         23         2024-12-02    2024-12-14'}
  3. {'ip': '172.16.0.1', '_ingested_at': '2024-12-15T10:30:00.123456+00:00', '_row_hash': 'ghi789...', '_source_row': '172.16.0.1     67         12         2024-12-03    2024-12-13'}
[DRY-RUN] Skipping MongoDB write.
```

## MongoDB Collection Details

**Collection Name:** `dshield_top_attackers_raw`  
**Database:** `dshield_etl` (configurable)  
**Indexes:** 
- `_row_hash` (unique) - for deduplication
- `ip` - for IP-based queries
- `_ingested_at` - for time-based queries

