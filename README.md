# ETL Data Connector for DShield Top Attackers  
This directory contains a custom Extract–Transform–Load (ETL) Python script that retrieves attacker IP data from the [DShield Top Attackers API](https://isc.sans.edu/) and stores it in MongoDB.  

## ✅ Submission Checklist

- [✅] Choose a data provider (API) and understand its documentation  
- [✅] Secure all API credentials using a `.env` file  
- [✅] Build a complete ETL pipeline: Extract → Transform → Load (into MongoDB)  
- [✅] Test and validate your pipeline (handle errors, invalid data, rate limits, etc.)  
- [✅] Follow the provided Git project structure  
- [✅] Write a clear and descriptive `README.md` in your folder with API details and usage instructions  
- [✅] **Include your name and roll number in your commit messages**  
- [✅] Push your code to your branch and submit a Pull Request  

---

## 📦 Project Structure

`/Rupnarayan-3122225001114-C/`  
├── etl_connector.py  
├── .env  
├── ENV_TEMPLATE
├── requirements.txt  
├── README.md
├── .gitignore

- **`.env`**: Contains sensitive MongoDB URI and API URL (not committed to Git).  
- **`etl_connector.py`**: Main ETL script.  
- **`requirements.txt`**: List of Python dependencies.  
- **`README.md`**: Instructions for running and understanding the connector.  

---

## 🗃️ MongoDB Guidelines

- Used one MongoDB collection for this connector: `dshield_raw`.  
- Stored ingestion timestamps (`_ingestion_time`) for audit and update purposes.  

---

## 📡 API Details

- **API Provider:** DShield Internet Storm Center  
- **Endpoint Used:** `https://isc.sans.edu/api/topips/records`  
- **Data Format:** Plain text with space-separated fields  
- **Fields Extracted:**  
  - `ip` → Attacker IP address  
  - `attacks` → Number of attacks from the IP  
  - `targets` → Number of unique targets  
  - `first_seen` → Date the IP was first seen attacking  
  - `last_seen` → Date the IP was last seen attacking  

---

## 📜 Sample Data Stored in MongoDB

```json
/** 
* Paste one or more documents here
*/
{
  "ip": "185.224.128.017",
  "attacks": 475183,
  "targets": 9728,
  "first_seen": "2022-11-18",
  "last_seen": "2025-08-11",
  "_ingestion_time": {
    "$date": "2025-08-14T14:13:28.263Z"
  }
}
