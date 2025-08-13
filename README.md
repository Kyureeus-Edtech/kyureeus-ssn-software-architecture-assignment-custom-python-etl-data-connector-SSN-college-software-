# SSN ETL – NVD CVE Connector - Pranav Moorthi - 312222 5001 093

A Python ETL script to fetch CVE data from the NVD API and store it in MongoDB with error handling for connectivity, rate limits, and data integrity.

## Features
- Fetch CVEs from NVD API with retries and rate-limit handling.
- Validate API responses for missing or empty data.
- Insert records into MongoDB with acknowledgment checks.
- Timestamp each record with UTC time.

## Requirements
- Python 3.8+
- MongoDB
- NVD API key (optional but recommended)

## Installation
```bash
git clone https://github.com/custom-python-etl-data-connector-pranav2210176.git
cd custom-python-etl-data-connector-pranav2210176
pip install -r requirements.txt
```
## Project Tree
```
.
├── cve_connector.py # Main script
├── requirements.txt # Python dependencies
├── .env # Environment variables
└── README.md # Documentation
```
