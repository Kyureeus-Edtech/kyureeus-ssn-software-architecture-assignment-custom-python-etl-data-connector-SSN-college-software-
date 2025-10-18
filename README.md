# Software Architecture Assignment: Custom Python ETL Data Connector — Abuse.ch Threat Intelligence ETL Pipeline

This project implements a custom ETL (Extract, Transform, Load) data connector for Abuse.ch, a threat intelligence platform that provides open data on malware, botnets, and IOCs (Indicators of Compromise).

##  Assignment Overview

### Goal

Develop a Python-based ETL pipeline that connects to the Abuse.ch threat intelligence APIs, extracts recent data, transforms it into a structured format, and loads it into a MongoDB collection for further analysis and visualization.

### Integrated Sources

This connector integrates multiple Abuse.ch sources/endpoints:

- **MalwareBazaar** — malware sample metadata
- **URLHaus** — malicious URLs and status
- **ThreatFox** — Indicators of Compromise (IOCs) like hashes, domains, URLs

##  ETL Workflow

### Extract
Fetches recent data from the above Abuse.ch APIs using authenticated endpoints with the help of an Auth-Key.

### Transform
Cleans and restructures raw JSON data into MongoDB-friendly dictionaries — ensuring consistent formats, valid datatypes, and removal of unnecessary fields.

### Load
Bulk inserts structured documents into dedicated MongoDB collections (one per source), with ingestion timestamps for tracking.

## 🛠️ Features

- Connects to multiple Abuse.ch threat data feeds
- Fetches malware samples, URLs, and IOCs
- Handles API authentication (if required)
- Cleans and normalizes complex JSON data
- Transforms data into MongoDB-ready format
- Loads processed data into MongoDB efficiently
- Modular design: easily extendable to new feeds
- Includes detailed logging for every stage (ETL)

##  Project Structure

```
/Karthikeyan_CSEB_3122225001056_Assignment2/
├── main.py  - Main entry point that runs the entire ETL
├── endpoints/
│   └── malware_bazaar_endpoints.py      — Extracts data from Abuse.ch APIs
├── pipeline/
│   ├── transform.py    — Transforms and cleans JSON data
│   ├── load.py        — Loads processed data into MongoDB
│   └── extract.py           — Runs the full ETL pipeline
├── output_screenshots/
│   ├── mongosh_terminal_output.png
│   ├── sample_threatfox_document.png
|   ├── sample_malwarebazaar_document.png
|   ├── sample_urlhaus_document.png
│   └── logger_output.png
├── config.py                   — Loads environment variables and configuration
├── .env                        — Contains API endpoints and DB connection (not committed)
├── requirements.txt            — Lists Python dependencies
└── README.md                   — Documentation for this connector
```

##  API Endpoints Used

| Source | Description | Endpoint |
|--------|-------------|----------|
| **MalwareBazaar** | Malware sample metadata | `https://mb-api.abuse.ch/api/v1/` |
| **URLHaus** | Malicious URLs | `https://urlhaus-api.abuse.ch/v1/urls/recent/` |
| **ThreatFox** | IOCs like hashes, domains, and URLs | `https://threatfox-api.abuse.ch/api/v1/` |

##  Environment Configuration

Create a `.env` file in your project root directory with the following content:

```env
MONGO_URL=<YOUR_MONGO_URL>
MONGO_DB=<YOUR_MONGO_DB>
MONGO_COLLECTION= <YOUR_MONGO_COLLECTION>
ABUSECH_API_KEY=<YOUR_AUTH_KEY>

MALWAREBAZAAR_API=https://mb-api.abuse.ch/api/v1/
URLHAUS_API=https://urlhaus.abuse.ch/downloads/json_recent/
THREATFOX_API=https://threatfox-api.abuse.ch/api/v1/
```

## MongoDB Collection Strategy

- All data sources (MalwareBazaar, URLHaus, ThreatFox, FeodoTracker) are stored in a **single MongoDB collection**
- Each document includes a `source` field to identify which Abuse.ch service it came from
- Each document includes an ingestion timestamp field for tracking updates
- Data insertion uses bulk operations for performance efficiency


## Prerequisites
Before running this ETL pipeline, ensure you have:
- **Python 3.8+** installed  
- **MongoDB** (local or remote instance) running and accessible  
- **Get your authentication API key**  
  - Retrieve your API key from your account settings  
- **Git** (optional, for cloning the repository)  
- **pip** (Python package installer, included with Python)  

## Installation & Setup

1. Create a virtual environment (recommended): <br>
&nbsp; &nbsp;&nbsp;&nbsp;python -m venv venv

2. Activate the virtual environment: <br>
   &nbsp; &nbsp;&nbsp;&nbsp;Windows (PowerShell): .\venv\Scripts\Activate.ps1 <br>
    &nbsp; &nbsp;&nbsp;&nbsp;macOS/Linux: source venv/bin/activate

3. Install dependencies: <br>
    &nbsp; &nbsp;&nbsp;&nbsp;pip install -r requirements.txt

4. Set up the .env file: Create a file named .env in the project root with the following content: <br>
    &nbsp; &nbsp;&nbsp;&nbsp;ABUSECH_API_KEY=<YOUR_AUTH_KEY> <br>
    &nbsp; &nbsp;&nbsp;&nbsp;MONGO_URL=<YOUR_MONGO_URL> <br>
    &nbsp; &nbsp;&nbsp;&nbsp;MONGO_DB=<YOUR_MONGO_DB><br>
    &nbsp; &nbsp;&nbsp;&nbsp;MONGO_COLLECTION= <YOUR_MONGO_COLLECTION> <br>
    &nbsp; &nbsp;&nbsp;&nbsp;ABUSECH_API_KEY=<YOUR_AUTH_KEY> <br>
    &nbsp; &nbsp;&nbsp;&nbsp;MALWAREBAZAAR_API=https://mb-api.abuse.ch/api/v1/ <br>
    &nbsp; &nbsp;&nbsp;&nbsp;URLHAUS_API=https://urlhaus.abuse.ch/downloads/json_recent/ <br>
    &nbsp; &nbsp;&nbsp;&nbsp;THREATFOX_API=https://threatfox-api.abuse.ch/api/v1/ <br>

5. Run the ETL pipeline: <br>
    &nbsp; &nbsp;&nbsp;&nbsp;python main.py
