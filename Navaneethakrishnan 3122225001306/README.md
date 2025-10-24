# AbuseIPDB ETL Connector



---

## 📌 Overview
This project is a **custom Python ETL (Extract, Transform, Load) data connector** that retrieves IP address abuse information from the **AbuseIPDB API**, transforms it by adding a timestamp, and loads the data into a **MongoDB** collection.

---

## 🔗 API Details
- **API Name:** AbuseIPDB API
- **Base URL:** `https://api.abuseipdb.com/api/v2/check`
- **Format:** JSON
- **Authentication:** API Key (stored securely in `.env` file)
- **Official Docs:** [https://docs.abuseipdb.com/](https://docs.abuseipdb.com/)

**Example Request Parameters:**
- `ipAddress` → IP to check (e.g., `8.8.8.8`)
- `maxAgeInDays` → Days to look back (default: 90)

---

## ⚙️ ETL Pipeline

### **1. Extract**
Fetch IP abuse data from the AbuseIPDB API using `requests` library with API key authentication.

### **2. Transform**
- Add `ingested_at` timestamp to each record.

### **3. Load**
Insert the transformed record into:
- **Database:** `etl_assignment`
- **Collection:** `abuseipdb_raw`

---

