# URLhaus ETL Data Connector

This project is a custom **Extract–Transform–Load (ETL)** Python script that downloads malicious URL data from the [abuse.ch URLhaus API](https://urlhaus.abuse.ch/), transforms it into a clean JSON format, and stores it into a MongoDB collection for later analysis.

---

## ⚙️ Prerequisites

- **Python** 3.9 or newer
- **MongoDB** installed and running locally or accessible remotely
- `pip` for installing dependencies

---

## 📌 Features
- **Extracts** the latest malicious URLs from the CSV feed
- **Transforms** the feed by:
  - Skipping comment/metadata lines
  - Retaining proper column headers
  - Cleaning whitespace and empty fields
- **Loads** into MongoDB in structured format (`id`, `dateadded`, `url`, etc.)
- Configurable parameters via environment variables

---

## 🔌 Data Source / API

**Base URL:**  
`https://urlhaus.abuse.ch`

**CSV Feed Endpoint:**  
`/downloads/csv_online/`

When fetched, the feed includes metadata lines starting with `#` followed by a header row and data rows in CSV format.

**Example CSV row:**
"id","dateadded","url","url_status","last_online","threat","tags","urlhaus_link","reporter"
"3602008","2025-08-13 16:22:12","http://123.7.222.250:53807/bin.sh","online","2025-08-13 16:22:12","malware_download","32-bit,elf,mips,Mozi","https://urlhaus.abuse.ch/url/3602008/","geenensp"

---

## 📂 Project Structure

custom-python-etl-data-connector-Athish369/
│
├── etl_connector.py # Main ETL script: Extract, Transform, Load
├── requirements.txt # Python dependencies list
├── .env # Environment variables (not tracked in git)
├── .gitignore # Git ignore rules
├── README.md # Project documentation

---

## ▶️ Usage

Run the ETL pipeline:
    python etl_connector.py


**Process Flow:**
1. **Fetch** data from `BASEURL + API_ENDPOINT`
2. **Parse & clean** CSV to structured records
3. **Insert** cleaned records into MongoDB

---

## 📂 MongoDB Output Format

Documents in MongoDB will look like:

{
  "_id": {
    "$oid": "689cce4ebfdab45fbea5790f"
  },
  "id": "3602141",
  "dateadded": "2025-08-13 17:25:17",
  "url": "http://125.41.227.78:47639/bin.sh",
  "url_status": "online",
  "last_online": "2025-08-13 17:25:17",
  "threat": "malware_download",
  "tags": "32-bit,elf,mips,Mozi",
  "urlhaus_link": "https://urlhaus.abuse.ch/url/3602141/",
  "reporter": "geenensp"
}