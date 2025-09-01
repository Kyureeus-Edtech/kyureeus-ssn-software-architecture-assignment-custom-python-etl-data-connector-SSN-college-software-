# URLhaus CSV ETL Connector

## Introduction
The **URLhaus CSV ETL Connector** is a Python-based tool that automates the process of fetching, parsing, and storing the [URLhaus Online CSV Feed](https://urlhaus.abuse.ch/downloads/csv_online/) into a MongoDB database.  

URLhaus is operated by abuse.ch and provides information about malicious URLs used for malware distribution. This connector allows security analysts and researchers to ingest URLhaus data into MongoDB for analysis, correlation, and integration into security workflows.

The connector:

- Retrieves the latest malicious URL feed from URLhaus.  
- Parses the CSV data into structured fields (`id`, `dateadded`, `url`, `url_status`, `last_online`, `threat`, `tags`, `urlhaus_link`, `reporter`).  
- Stores the processed data in MongoDB for further investigation and integration.  
- Maintains metadata such as ingestion timestamps to support audits and ETL updates.  

---

## Features
- **Automated Fetching**: Downloads the latest online malicious URL feed from URLhaus.  
- **Data Parsing**: Extracts all relevant fields from the CSV feed.  
- **MongoDB Storage**: Saves raw and transformed data for easy querying.  
- **Metadata Management**: Tracks ingestion timestamps and record counts.  
- **Configurable**: All runtime settings are managed through environment variables.  

---

## Prerequisites
Before running the connector, ensure you have:

- Python **3.8+**  
- MongoDB installed locally or remotely accessible  
- Internet access to fetch the URLhaus feed  

---

## Configuration
The connector reads settings from environment variables. You must create a `.env` file based on the `.env_template` provided:

```env
BASE_URL=your_base_url
ENDPOINT=your_endpoint
MONGO_URI=your_mongo_uri
DB_NAME=your_database_name
COLLECTION_NAME=your_collection_name
CONNECTOR_NAME=your_connector_name

