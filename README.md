# 📌 CISA KEV – ETL Data Connector

This project is a **Python ETL pipeline** that:
1. **Extracts** the [Known Exploited Vulnerabilities (KEV)](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) feed from CISA.
2. **Transforms** the data into a clean, query-friendly format (while also storing the raw payload).
3. **Loads** the data into a MongoDB database, using **upserts** to avoid duplicates.

---

## 🚀 Features
- **Automatic retries** for API requests (handles network hiccups & rate limits).
- **Raw + transformed collections** in MongoDB.
- **Upsert by CVE ID** — re-runs won't duplicate entries.
- **Audit fields**: ingestion time, ETag, Last-Modified.
- **Index creation** for faster queries on key fields.

---

## 📂 Project Structure
.
├── etl_connector.py # Main ETL script
├── requirements.txt # Dependencies
├── .env.example # Example env file for config
├── .gitignore # Ignore .env and local files
└── README.md # Documentation (this file)