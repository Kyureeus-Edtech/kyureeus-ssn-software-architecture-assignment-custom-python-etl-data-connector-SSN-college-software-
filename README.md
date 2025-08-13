# Spamhaus DROP List ETL Connector

## Introduction
The **Spamhaus DROP List ETL Connector** is a Python-based tool that automates the process of fetching, parsing, and storing the Spamhaus DROP (Don't Route Or Peer) List into a MongoDB database.  
The DROP List identifies IP address ranges controlled by cybercriminals and is widely used by network administrators and security teams to block malicious traffic.

The connector:
- Retrieves the latest DROP list from Spamhaus.
- Parses entries into structured fields (CIDR, SBL ID, and description).
- Stores the processed data in MongoDB for integration into security workflows.
- Maintains metadata for tracking updates and ETL run status.

## Features
- **Automated Fetching:** Downloads the latest DROP list from the Spamhaus endpoint.
- **Data Parsing:** Extracts CIDR blocks, SBL IDs, and associated comments.
- **MongoDB Storage:** Saves raw and processed data for easy querying.
- **Metadata Management:** Tracks update timestamps, record counts, and source info.
- **Configurable:** All runtime settings are managed through environment variables.



## Prerequisites
Before running the connector, ensure you have:
- **Python 3.8+**
- **MongoDB** installed locally or remotely accessible
- Internet access to fetch the Spamhaus DROP List




## Configuration
The connector reads settings from environment variables.
You must create a .env file based on the ENV_TEMPLATE provided.

BASE_URL=your_base_url
ENDPOINT=your_endpoint
MONGO_URI=your_mongo_uri
DB_NAME=your_database_name
COLLECTION_NAME=your_collection_name
CONNECTOR_NAME=your_connector_name
REQUEST_TIMEOUT=your_request_timeout
USER_AGENT=your_user_agent_string
VERIFY_TLS=your_true_or_false
BATCH_SIZE=your_batch_size
METADATA_COLLECTION=your_metadata_collection_name

## Run the Connector
`python etl_connector.py`
