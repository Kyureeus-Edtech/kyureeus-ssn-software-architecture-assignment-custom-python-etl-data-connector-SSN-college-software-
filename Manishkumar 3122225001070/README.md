# AbuseIPDB ETL Connector

---

## 📌 Overview
This project implements a **custom Python ETL (Extract, Transform, Load) data connector** that retrieves IP address abuse information from the **AbuseIPDB API**, transforms it by adding an ingestion timestamp, and loads the data into a **MongoDB** collection for storage and analysis.

---

## 🔗 API Details
- **API Name:** AbuseIPDB API
- **Base URL:** `https://api.abuseipdb.com/api/v2/check`
- **Format:** JSON
- **Authentication:** API Key (stored securely in `.env` file)
- **Official Documentation:** [https://docs.abuseipdb.com/](https://docs.abuseipdb.com/)

**Example Request Parameters:**
- `ipAddress` → The IP address to check (e.g., `8.8.8.8`)
- `maxAgeInDays` → The time window in days for reports (default: 90)

---

## ⚙️ ETL Pipeline

### **1. Extract**
Fetches abuse report data for a given IP address from the AbuseIPDB API using the `requests` library and API key authentication.

### **2. Transform**
- Appends an `ingested_at` timestamp to each record for tracking purposes.

### **3. Load**
Inserts the transformed record into:
- **Database:** `etl_assignment`
- **Collection:** `abuseipdb_raw`

---
