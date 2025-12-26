# MalShare ETL Python Connector

This ETL script connects to the MalShare public malware feed API, extracts the latest sample metadata, transforms it for MongoDB consumption, and loads the results into a specified collection.

## API Documentation

- **Base URL:** https://malshare.com/api.php
- **Endpoint Formula:** /api.php?api_key=API_KEY&action=getlist

## Setup

1. Install dependencies:
    ```
    pip install -r requirements.txt
    ```
2. Add a `.env` file:
    ```
    MALSHARE_API_KEY=your-malshare-api-key
    MONGODB_URI=your-mongodb-uri
    MONGODB_DB=malshare_db
    MONGODB_COLLECTION=malshare_raw
    ```
3. Run the connector:
    ```
    python etl_connector.py
    ```

## MongoDB

- Collection: `malshare_raw`
- Each entry includes an `ingested_at` timestamp.

## Error Handling

- Handles invalid API responses, empty payloads, and MongoDB errors.

## Example Output

