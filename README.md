# AbuseCH ETL Connector

Python ETL pipeline to fetch threat intelligence feeds from URLHaus and FeodoTracker and store them into MongoDB.  
Developed by **Srivathsan Sundarrajan** (Roll No: XXXX) for SSN CSE Software Architecture Assignment.

---

## 📌 Overview

This project demonstrates building custom Python ETL connectors for security-related data.  
The ETL pipeline extracts data from public threat feeds, transforms it for MongoDB compatibility, and loads it into separate collections with ingestion timestamps.

---

## 🛠️ Feeds / Endpoints Used

| Connector        | Feed URL                                               | Notes                         |
|-----------------|-------------------------------------------------------|-------------------------------|
| `recent_urls`    | https://urlhaus.abuse.ch/downloads/csv_recent/       | Latest malicious URLs         |
| `online_urls`    | https://urlhaus.abuse.ch/downloads/csv_online/       | Currently active URLs         |
| `feodotracker`   | https://feodotracker.abuse.ch/downloads/ipblocklist.csv | Malicious IP addresses        |

> These feeds are public and **do not require authentication**.

---

## ⚙️ ETL Pipeline Design

**1. Extract**  
- Fetch CSV feeds from URLHaus and FeodoTracker using `requests`.  

**2. Transform**  
- Clean column names  
- Remove duplicates  
- Add `_ingested_at` timestamp for audit purposes  

**3. Load**  
- Insert data into MongoDB collections:
  - `recent_urls_raw`  
  - `online_urls_raw`  
  - `feodotracker_raw`  

---

## 📂 Project Structure

/abuseCH_etl/
├── etl_connector.py # Main ETL script
├── requirements.txt # Python dependencies
├── README.md # This file
├── .gitignore # Ignore secrets and cache files
└── .env # MongoDB credentials (not committed)

🧪 Testing & Validation
-----------------------
Handles connectivity issues and retries 3 times on failure

Checks for empty feeds before inserting

Logs number of records fetched and inserted into MongoDB

_ingested_at timestamp ensures traceability

💻 Dependencies
--------------
pandas

requests

pymongo

python-dotenv

Install all dependencies:

pip install -r requirements.txt

🚀 How to Run
---------------
Clone the repository and switch to your branch

Create .env with MongoDB credentials

Install dependencies

Run ETL:

python etl_connector.py

📢 Notes
------------
Currently uses 3 feeds: URLHaus recent, URLHaus online, FeodoTracker IPs

Designed to be easily extended with additional connectors

Logs everything in console for debugging



Srivathsan Sundarrajan
Roll No: 3122225001141
SSN College of Engineering
