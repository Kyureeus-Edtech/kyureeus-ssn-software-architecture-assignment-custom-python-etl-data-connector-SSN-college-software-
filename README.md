# ThreatFox IOCs ETL Data Connector

This project contains a Python ETL (Extract–Transform–Load) script to fetch Indicators of Compromise (IOCs) from the ThreatFox API, transform them into a clean format, and load them into a MongoDB collection.

## 🚀 How to Run

### 1️⃣ Prerequisites
- Python 3.8+ installed
- A MongoDB Atlas account (or local MongoDB instance)
- A ThreatFox API key (optional, but required for authenticated queries)

### 2️⃣ Clone & Install
```bash
git clone <your-repo-url>
cd <repo-name>
pip install -r requirements.txt

3️⃣ Set Up Credentials

Create a .env file in the project root and add:

# ThreatFox API key (get it from https://threatfox.abuse.ch/)
THREATFOX_API_KEY="your-threatfox-api-key"

# MongoDB connection string (Atlas or local instance)
MONGO_URI="your-mongo-uri"


💡 If you don't provide THREATFOX_API_KEY, the script will use the public feed with limited data.

4️⃣ Execute the ETL Script
python etl_connector.py

5️⃣ What the Script Does

Extract: Retrieves recent IOCs from ThreatFox API or public feed.

Transform: Cleans, normalizes timestamps, and prepares data for storage.

Load: Inserts unique IOCs into MongoDB, avoiding duplicates.

6️⃣ Example Output
[2025-08-14 21:56:46] Starting extraction... (limit=50)
[2025-08-14 21:56:49] Extraction successful! Retrieved 362 records in 3.29s.
[2025-08-14 21:56:49] Transformation completed: 362 records transformed in 0.08s.
[2025-08-14 21:56:49] Load completed: 350 new records inserted in 1.12s.
[2025-08-14 21:56:49] ===== ETL SUMMARY =====
[2025-08-14 21:56:49] Extracted: 362
[2025-08-14 21:56:49] Transformed: 362
[2025-08-14 21:56:49] Loaded: 350
[2025-08-14 21:56:49] =======================

📌 Notes

If using MongoDB Atlas, ensure your IP address is added to the Network Access list.

Increase timeout in code if you have a slow network connection.

Free tier Atlas clusters may take 30–60 seconds to wake from idle.