# SSL Labs ETL Connector

## Overview
This connector extracts SSL/TLS configuration scan results from the **Qualys SSL Labs API (v4)**, transforms the data, and loads it into a MongoDB collection. It handles the asynchronous nature of the API by polling for results before ingestion.

## Setup Instructions
1.  Create a `.env` file with the following variables:
    ```
    MONGO_URI=mongodb://your-mongo-host:27017/
    DB_NAME=cybersecurity_data
    SSLLABS_EMAIL=your_registered_email@example.com
    ```
    **Note:** You must register your email with SSL Labs to use the v4 API.

2.  Create a `requirements.txt` file with the following:
    ```
    requests
    pymongo
    python-dotenv
    xmltodict
    ```

3.  Install dependencies:
    ```
    pip install -r requirements.txt
    ```

4.  Start MongoDB locally or ensure the `MONGO_URI` is accessible.

5.  Run the connector:
    ```
    python etl_connector.py
    ```

## Example Output
Documents inserted into MongoDB will be the full JSON report from the SSL Labs API, with an `ingestion_timestamp` added. The `host` field is used as the unique ID for upserting.

```json
{
  "host": "google.com",
  "port": 443,
  "protocol": "TCP",
  "status": "READY",
  "endpoints": [
    {
      "ipAddress": "142.250.190.174",
      "grade": "A",
      "details": {
        "protocols": [
          { "id": 772, "name": "TLS", "version": "1.3" },
          { "id": 771, "name": "TLS", "version": "1.2" }
        ],
        "cipherSuites": [ /* ... */ ],
        "cert": { /* ... */ }
      }
    }
  ],
  "ingestion_timestamp": "2025-10-18T22:30:00.123456Z",
  "_id": "..."
}