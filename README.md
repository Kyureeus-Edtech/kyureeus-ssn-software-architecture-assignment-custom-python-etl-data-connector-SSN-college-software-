# ThreatFox ETL Connector

## 📌 Overview

This Python ETL connector fetches **threat intelligence data** from the [ThreatFox Abuse.ch](https://threatfox.abuse.ch/) public JSON feed, transforms it for MongoDB storage, and loads it into a dedicated collection.

The script ensures **secure credentials handling**, **duplicate prevention**, and **robust error handling** for production-grade reliability.

---

## 🔗 API Details

- **API Name:** ThreatFox JSON Feed
- **Base URL:** https://threatfox.abuse.ch/export/json/threatfox_abuse_ch.json
- **Format:** JSON
- **Authentication:** None required
- **Description:** Provides a list of malicious indicators such as domains, IPs, and file hashes, updated regularly.

---

## 📂 Project Structure

/TarunR_3122225001148_C/
├── etl_connector.py # Main ETL script
├── requirements.txt # Python dependencies
├── README.md # Documentation
├── ENV_TEMPLATE # Placeholder environment variables (no secrets)
└── .env # Environment variables (DO NOT COMMIT)

---

## ⚙️ Setup Instructions

### 1️⃣ Clone Repository and Create Branch

git clone https://github.com/Kyureeus-Edtech/custom-python-etl-data-connector-TarunR7.git
cd custom-python-etl-data-connector-TarunR7
git checkout -b TarunR_3122225001148_C

### 2️⃣ Create .env File

1. Locate the `ENV_TEMPLATE` file in this project.
2. Copy it to a new file named `.env`:
3. Replace the placeholder values in .env with your actual credentials and configuration.
4. Register and get a free Auth-Key from the abuse.ch Authentication Portal

### 3️⃣ Install Dependencies

pip install -r requirements.txt

---

## 🚀 Running the ETL

python etl_connector.py

The script will:

1. Extract data from ThreatFox JSON feed
2. Transform the data by adding ingested_at timestamps and validating structure
3. Load the data into MongoDB (threatfox_raw collection) with duplicate prevention

---

## 🛡️ Duplicate Prevention

- MongoDB has a unique index on the id field from ThreatFox
- Already ingested entries will be skipped automatically

---

## 🧪 Error Handling & Validation

- Retries up to 3 times on connection failures or rate limits (429)
- Waits according to the Retry-After header if provided
- Validates JSON structure before processing
- Skips malformed records without breaking the ETL

---

## 📊 MongoDB Collection Details

- Collection Name: threatfox_raw
- Fields: As provided by ThreatFox feed + ingested_at timestamp
- Indexes: Unique index on id for duplicate prevention

Example document:
{
"query_status": "ok",
"data": [
{
"id": "41",
"ioc": "gaga.com",
"threat_type": "botnet_cc",
"threat_type_desc": "Indicator that identifies a botnet command&control server (C&C)",
"ioc_type": "domain",
"ioc_type_desc": "Domain that is used for botnet Command&control (C&C)",
"malware": "win.dridex",
"malware_printable": "Dridex",
"malware_alias": null,
"malware_malpedia": "https:\/\/malpedia.caad.fkie.fraunhofer.de\/details\/win.dridex",
"confidence_level": 50,
"first_seen": "2020-12-08 13:36:27 UTC",
"last_seen": null,
"reporter": "abuse_ch",
"reference": "https:\/\/twitter.com\/JAMESWT_MHT\/status\/1336229725082177536",
"tags": [
"exe",
"test"
]
},
[...]
]
}

---

## ✅ Submission Checklist

- [x] Chose ThreatFox API and understood documentation
- [x] Secured MongoDB credentials in .env
- [x] Built full ETL: Extract → Transform → Load
- [x] Added rate limit handling, retries, and validation
- [x] Prevented duplicate entries using MongoDB index
- [x] Wrote README with setup and API details
- [x] Ready to push branch and create Pull Request

---

## 📌 Commit Message Format

When committing your code, include:
Added ThreatFox ETL Connector - Your Name (Roll No. XXXX)
