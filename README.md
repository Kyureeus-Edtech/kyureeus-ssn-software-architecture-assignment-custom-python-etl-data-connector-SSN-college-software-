# Multi-Source Threat Intelligence ETL Pipeline

## Submitted by
- Name: Sundaresh Karthic Ganesan 
- Reg. Number: 3122225001143 
- College: SSN College of Engineering  
- Course: Software Architecture (Kyureeus EdTech)

---

## 1. Overview

This ETL (Extract, Transform, Load) pipeline is a modular and robust Python script designed to gather cybersecurity intelligence from multiple public APIs, handle various data formats, and load the information into a MongoDB database.

The connector is built with a configuration-driven design, making it easy to add new data sources without changing the core code. It handles **JSON**, **XML**, and **Plain Text** formats, transforming them into a standardized structure for clean and efficient storage.

## 2. Data Sources

The pipeline is currently configured to pull data from two primary providers: **CISA.gov** and **Blocklist.de**.

| API Provider      | Endpoint                   | Data Format | Target MongoDB Collection     |
| ----------------- | -------------------------- | ----------- | ----------------------------- |
| **CISA.gov** | KEV Catalog                | JSON        | `cisa_kev_catalog_raw`        |
| **CISA.gov** | Alerts & Advisories        | XML         | `cisa_alerts_raw`             |
| **CISA.gov** | ICS Advisories             | XML         | `cisa_ics_advisories_raw`     |
| **CISA.gov** | News & Events              | XML         | `cisa_news_raw`               |
| **Blocklist.de** | All IPs                    | Text        | `blocklist_de_all_raw`        |
| **Blocklist.de** | SSH Attackers              | Text        | `blocklist_de_ssh_raw`        |
| **Blocklist.de** | Bot IPs                    | Text        | `blocklist_de_bots_raw`       |

## 3. ETL Pipeline Phases

### 1. Extract
- Fetches raw data from each configured endpoint using GET requests.
- Handles common network errors, including connection issues, request timeouts, and bad HTTP status codes (e.g., 404, 500).

### 2. Transform
- Parses the raw data based on its specified format (JSON, XML, or Text).
- For structured data (JSON/XML), it navigates to the list of records.
- For plain text data (Blocklist.de), it converts each line into a structured dictionary.
- Enriches every record with a consistent `ingestion_timestamp` for auditing.

### 3. Load
- Connects to a MongoDB database using credentials from a secure `.env` file.
- Uses an efficient **upsert** strategy (`ReplaceOne` with `upsert=True`) to load data. This prevents duplicates by updating existing records or inserting new ones based on a unique ID.

## 4. MongoDB Details

- **Database**: Defined by `DB_NAME` in the `.env` file (e.g., `cybersecurity_data`).
- **Collections Created**:
  - `cisa_kev_catalog_raw`
  - `cisa_alerts_raw`
  - `cisa_ics_advisories_raw`
  - `cisa_news_raw`
  - `blocklist_de_all_raw`
  - `blocklist_de_ssh_raw`
  - `blocklist_de_bots_raw`

## 5. Setup and Installation

### Step 1: Install Dependencies
You will need Python 3.8+ and the libraries listed in `requirements.txt`.
bash
pip install -r requirements.txt
`

### Step 2: Configure Environment Variables

Create a `.env` file in the project's root directory with the following content, replacing the placeholder with your MongoDB connection string.

ini
# .env file
MONGO_URI="mongodb+srv://<username>:<password>@<cluster-url>/<dbname>?retryWrites=true&w=majority"
DB_NAME="cybersecurity_data"


### Step 3: Run the Pipeline

Execute the script from your terminal.

bash
python etl_pipeline.py


The script will log its progress for each endpoint to the console.

## 6\. Learnings

This project demonstrates how to:

  - Design a flexible, configuration-driven ETL pipeline in Python.
  - Handle multiple real-world data formats (JSON, XML, Text) within a single script.
  - Implement robust error checking for network requests and data processing.
  - Use an efficient `upsert` strategy to load data into MongoDB, ensuring data integrity.
  - Securely manage credentials and configurations using environment variables.

## References

- CISA KEV Catalog: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- Blocklist.de API: https://www.blocklist.de/en/api.html
- Requests Library: https://docs.python-requests.org/
- PyMongo Documentation: https://pymongo.readthedocs.io/
- Dotenv for Python: https://pypi.org/project/python-dotenv/ 