**Name:** Dharunika S

**Roll Number:** 3122225001026

# OTX AlienVault ETL Connector

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![MongoDB](https://img.shields.io/badge/MongoDB-4.4%2B-green)
![License](https://img.shields.io/badge/license-MIT-orange)

A Python ETL pipeline that extracts threat intelligence data from AlienVault OTX, transforms it, and loads it into MongoDB.

## Features

- Secure API authentication with retry logic
- Data validation and transformation
- MongoDB document storage with timestamps
- Comprehensive error handling
- Configurable through environment variables

## Prerequisites

- Python 3.8+
- MongoDB instance
- AlienVault OTX API key
- Python packages: `requests`, `pymongo`, `python-dotenv`

## Environment Configuration

Create a `.env` file with the following variables:

```ini
OTX_API_KEY=your_api_key_here
MONGO_URI=mongodb://localhost:27017
DB_NAME=test_db
COLLECTION_NAME=test_data
```

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd etl-connector
   ```

```

2. Install dependencies: `pip install -r requirements.txt`
3. Run ETL: `python etl_connector.py`
4. Check MongoDB
```

## Data Model

```json
{

  "_id": "ObjectId(...)",
  "pulse_id": "5a3b9c8d7e6f5g4h3i2j1k",
  "name": "Mirai Botnet Activity",
  "description": "Recent Mirai C2 servers and targets",
  "author": "threat_researcher_42",
  "tags": ["botnet", "iot", "ddos"],
  "indicators_count": 27,
  "references": ["https://example.com/report"],
  "ingestion_time": "ISODate(2023-11-20T14:32:45.123Z)",
  "otx_modified": "2023-11-18T08:30:00Z"

}
```
