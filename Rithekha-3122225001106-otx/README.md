# OTX AlienVault ETL Connector

## Overview
This ETL connector extracts threat intelligence data from the OTX AlienVault API and loads it into MongoDB.

## API Details
- **Provider**: OTX AlienVault  
- **Base URL**: `https://otx.alienvault.com`  
- **Endpoint**: `/api/v1/pulses/subscribed`  
- **Authentication**: API Key (via `X-OTX-API-KEY` header)  
- **Data Format**: JSON  
- **Rate Limit**: ~1000 requests/hour  

## Setup Instructions

### 1. Get API Key
- Visit [https://otx.alienvault.com](https://otx.alienvault.com)  
- Create an account and get your API key  

### 2. Configure Environment Variables
Add the following to your environment or `.env` file:  
```env
OTX_API_KEY=your_api_key
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=etl_assignment
COLLECTION_NAME=otx_pulses_raw
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run ETL
```bash
python etl_connector.py
```

## Usage Example
**Command:**
```bash
python etl_connector.py
```

**Expected Output:**
```text
[INFO] Connecting to OTX AlienVault API...
[INFO] Retrieved 50 pulses from API.
[INFO] Inserted data into MongoDB collection: otx_pulses_raw
[INFO] ETL process completed successfully.
```

## Sample API Response
```json
{
  "count": 1,
  "results": [
    {
      "id": "12345678",
      "name": "Suspicious IP Addresses",
      "created": "2025-08-14T12:34:56",
      "modified": "2025-08-14T12:34:56",
      "indicators": [
        {
          "indicator": "8.8.8.8",
          "type": "IPv4",
          "created": "2025-08-14T12:34:56"
        }
      ]
    }
  ]
}
```

## Author
Rithekha K 3122225001106