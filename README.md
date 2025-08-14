# ThreatFox ETL Connector

**Author:** Samyuktha D  
**Roll Number:** 3122225001309

## Project Description

This project is a Python-based ETL (Extract, Transform, Load) connector that fetches IoCs (Indicators of Compromise) from the ThreatFox API, cleans and deduplicates the data, and inserts it into a MongoDB collection.

- **Extract**: Fetches JSON data from ThreatFox API.
- **Transform**: Cleans the data (removes nulls, adds ingestion timestamp, computes unique hash for deduplication).
- **Load**: Upserts the cleaned data into MongoDB with unique `doc_hash`.

## API Endpoint

- ThreatFox API Endpoint: `https://threatfox-api.abuse.ch/api/v1/`
- Authentication: Auth-Key (provided via `.env`)

## Setup Instructions

1. Clone the repository:

```bash
git clone https://github.com/Kyureeus-Edtech/custom-python-etl-data-connector-samyuktha150.git
cd custom-python-etl-data-connector-samyuktha150


2. Create a virtual environment and activate it:

python -m venv venv

# Windows PowerShell
venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat

# Linux / macOS
source venv/bin/activate


3. Install dependencies:

pip install -r requirements.txt


4. Create a .env file and add your MongoDB URI and ThreatFox API key:

MONGODB_URI=your_mongodb_uri
THREATFOX_AUTH_KEY=a5f2b65f597d8aeca7558550edcee95d2d21797818a452d5

5. To run: 
python etl_connector.py
