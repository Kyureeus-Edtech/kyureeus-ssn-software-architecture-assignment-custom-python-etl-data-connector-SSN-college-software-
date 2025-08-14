# ThreatFox IOCs ETL Pipeline

This Python script extracts Indicators of Compromise (IOCs) from the [ThreatFox API](https://threatfox.abuse.ch/) and loads them into a MongoDB collection.  
It follows a basic **ETL (Extract → Transform → Load)** pattern:

1. **Extract** – Fetch IOCs from the ThreatFox API.
2. **Transform** – Clean and format the data for database storage.
3. **Load** – Store the processed IOCs into MongoDB.

---

## Features
- Fetch latest IOCs from ThreatFox for the last 1 day.
- Automatically transforms raw data into MongoDB-friendly documents.
- Stores ingestion timestamp for each record.
- Configurable through `.env` file.

---

## Requirements

### Install Dependencies
```bash
pip install requests pymongo python-dotenv
