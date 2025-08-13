# VirusTotal ETL Connector

**Student:** KAVIN T 
**Roll Number:** 3122225001058

## What it does

Extracts file analysis data from VirusTotal API and loads it into MongoDB.

## Setup

1. **Get API Key**: Sign up at https://www.virustotal.com/gui/join-us
2. **Create .env file**:
   ```
   VIRUSTOTAL_API_KEY=your_api_key_here
   MONGODB_URI=database_name
   MONGODB_DATABASE=threat_intelligence
   ```
3. **Install packages**: `pip install -r requirements.txt`
4. **Run**: `python etl_connector.py`

## Files

- `etl_connector.py` - Main ETL script
- `.env` - API keys (don't commit this!)
- `requirements.txt` - Dependencies
- `README.md` - This file

## ETL Process

- **Extract**: Gets data from VirusTotal for sample file hashes
- **Transform**: Cleans data and adds timestamps
- **Load**: Saves to MongoDB collection `virustotal_raw`

Done!