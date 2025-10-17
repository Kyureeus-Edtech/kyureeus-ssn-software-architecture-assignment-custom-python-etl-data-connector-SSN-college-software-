# Abuse.ch URLhaus ETL Pipeline – Multi-Format Data Extraction

**Author:** KEERTHANA G S  
**Roll Number:** 3122225001059  
**Date:** October 2025  

---

## Overview

This project implements an ETL (Extract, Transform, Load) pipeline that collects, transforms, and stores malware URL intelligence from the Abuse.ch URLhaus threat intelligence platform.

The pipeline fetches data from three different URLhaus endpoints — each providing malware URL indicators in different formats (CSV and TEXT) — and loads the structured data into MongoDB for storage and analysis.

---

## Key Features

- Extracts data from three public Abuse.ch endpoints  
- Handles multiple formats (CSV and plain text)  
- Parses, cleans, and transforms the data into MongoDB-ready documents  
- Stores the data in dedicated collections per source  
- Implements robust error handling, logging, and progress tracking  
- Modular and extendable for future integrations (e.g., ThreatFox, Feodo Tracker)

---

## Data Sources (Abuse.ch URLhaus)

| Endpoint | URL | Format | Description |
|-----------|-----|---------|-------------|
| Recent URLs (CSV) | `https://urlhaus.abuse.ch/downloads/csv_recent/` | CSV | Latest malware distribution URLs with full metadata |
| Online URLs (CSV) | `https://urlhaus.abuse.ch/downloads/csv_online/` | CSV | Currently active malware URLs |
| Recent URLs (TEXT) | `https://urlhaus.abuse.ch/downloads/text_recent/` | TEXT | Plain text list of recent malware URLs |

All endpoints are publicly accessible and do not require authentication.

---

## Architecture

### ETL Components

1. **Extract**  
   Downloads raw data from Abuse.ch URLhaus endpoints using the `requests` library.

2. **Transform**  
   - Parses CSV and text data into Python dictionaries  
   - Cleans and normalizes fields  
   - Adds standard metadata (timestamp, source, endpoint type)

3. **Load**  
   Inserts transformed records into MongoDB collections using the `pymongo` driver.

---

## MongoDB Structure

| Collection Name | Data Format | Description |
|-----------------|--------------|-------------|
| `urlhaus_recent_urls_csv` | CSV | Latest malware URLs (metadata) |
| `urlhaus_online_urls_csv` | CSV | Active malware URLs (metadata) |
| `urlhaus_text_urls` | TEXT | Raw URL list (no metadata) |

Each record includes an ingestion timestamp and metadata fields like:
```json
{
  "url": "http://malicious.example.com/file.exe",
  "url_status": "online",
  "threat": "malware_download",
  "tags": ["exe", "trojan"],
  "data_source": "abuse.ch_urlhaus",
  "endpoint": "recent_csv",
  "ingestion_timestamp": "2025-10-18T18:30:00Z"
}
