# MITRE ATT&CK TAXII API Connector

## Overview

This ETL (Extract, Transform, Load) connector fetches cybersecurity threat intelligence data from the MITRE ATT&CK TAXII 2.1 API and stores it in a MongoDB database. The connector implements a structured data pipeline that processes collections, manifests, objects, and versions from the MITRE ATT&CK framework.

## Features

- TAXII 2.1 API Integration: Connects to the official MITRE ATT&CK TAXII server
- MongoDB Storage: Stores processed data with timestamps for audit trails
- Error Handling: Robust error handling for API requests and database operations
- Data Limiting: Implements smart data limiting to prevent overwhelming storage
- Structured ETL Pipeline: Four-step ETL process for comprehensive data extraction

## Requirements

- Python 3.7+
- MongoDB instance (local or remote)
- Internet connection for API access

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables by creating a `.env` file:
```env
MONGO_URI=mongodb://localhost:27017/
```

## Usage

### Basic Usage

Run the connector to perform the complete ETL pipeline:

```bash
python MittreTaxiAPI_connector.py
```

## ETL Pipeline Steps

### 1. Collections Extraction (`etl_collections`)
- Fetches available collections from the TAXII server
- Stores collection metadata in MongoDB
- Returns collection IDs for subsequent processing
- Limit: Processes first 3 collections to prevent 429 error which occurs due to too many requests to the server.

### 2. Manifest Extraction (`etl_manifest`)
- Retrieves manifest data for each collection
- Contains metadata about available objects
- Limit: 3 objects per collection

### 3. Objects Extraction (`etl_objects`)
- Fetches actual threat intelligence objects
- Processes STIX objects containing attack patterns, techniques, etc.
- Limit: 3 objects per collection, 3 items in x_mitre_contents

### 4. Versions Extraction (`etl_versions`)
- Retrieves version history for each object
- Enables tracking of changes over time
- No specific limit applied

## Data Storage Structure

Data is stored in MongoDB with the following collections:

### `collections`
```json
{
  "data": [...],
  "ingested_at": "2025-10-03T10:30:00Z"
}
```

### `manifest`
```json
{
  "data": {
    "collection_id": "uuid",
    "objects": [...]
  },
  "ingested_at": "2025-10-03T10:30:00Z"
}
```

### `objects`
```json
{
  "data": {
    "collection_id": "uuid",
    "objects": [...]
  },
  "ingested_at": "2025-10-03T10:30:00Z"
}
```

### `versions`
```json
{
  "data": {
    "collection_id": "uuid",
    "object_id": "uuid",
    "versions": {...}
  },
  "ingested_at": "2025-10-03T10:30:00Z"
}
```

## API Endpoints

The connector uses the following MITRE ATT&CK TAXII 2.1 endpoints:

- Base URL: `https://attack-taxii.mitre.org/api/v21`
- Collections: `/collections`
- Manifest: `/collections/{collection_id}/manifest`
- Objects: `/collections/{collection_id}/objects`
- Versions: `/collections/{collection_id}/objects/{object_id}/versions`

## Error Handling

The connector implements comprehensive error handling:

- API Request Errors: Timeout handling (30 seconds), HTTP status validation
- Database Errors: MongoDB connection and insertion error handling
- Data Validation: Checks for data availability before processing
- Resource Cleanup: Ensures MongoDB connections are properly closed

## Configuration Options

### Timeout Settings
- Default API timeout: 30 seconds
- Modify in `fetch_data()` function if needed

### Data Limits
Current limits can be adjusted in the code:
- Collections processed: 3
- Objects per collection: 3
- x_mitre_contents items: 3

### Headers
The connector uses proper TAXII 2.1 headers:
```python
headers = {"Accept": "application/taxii+json;version=2.1"}
```

## Troubleshooting

### Common Issues

1. MongoDB Connection Error
   - Verify `MONGO_URI` in `.env` file
   - Ensure MongoDB service is running
   - Check network connectivity

2. API Timeout
   - Check internet connection
   - Verify MITRE TAXII server availability
   - Consider increasing timeout value

3. Permission Errors
   - Ensure MongoDB user has read/write permissions
   - Verify database access credentials

## Performance Notes

- The connector implements data limiting to prevent overwhelming storage as the website is not allowing responses beyond a limit it has been reduced to 3.
- MongoDB operations are optimized with proper connection handling
- API requests include reasonable timeouts
- Consider implementing caching for repeated requests

## Contributing

When modifying the connector:

1. Maintain the four-step ETL structure
2. Preserve error handling mechanisms
3. Update data limits as needed
4. Test with different MongoDB configurations
5. Validate against TAXII 2.1 specification

## Support

For issues related to:
- MITRE ATT&CK Data: Visit [MITRE ATT&CK](https://attack.mitre.org/)
- TAXII Specification: See [OASIS TAXII 2.1](https://docs.oasis-open.org/cti/taxii/v2.1/)
- MongoDB: Check [MongoDB Documentation](https://docs.mongodb.com/)