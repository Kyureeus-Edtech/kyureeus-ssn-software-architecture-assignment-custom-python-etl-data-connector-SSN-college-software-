# CyberGreen Metrics ETL Connector

## Overview
This connector extracts cybersecurity metric data from the CyberGreen Metrics API, transforms it by adding an ingestion timestamp, and loads it into a MongoDB collection.

## API Details
- Base URL: https://api.cybergreen.net
- Endpoint: /metrics
- Query Params: name, date
- Response Format: JSON

## How to Run
1. Create `.env` file from `.env_template`
2. Install dependencies:
   pip install -r requirements.txt
3. Run script:
   python etl_connector.py

## Example Output
{
    "name": "open_resolvers",
    "date": "2023-01-01",
    "value": 12345,
    "ingested_at": "2025-08-14T07:00:00Z"
}

## Author
Anierudh H S (3122225001012)
