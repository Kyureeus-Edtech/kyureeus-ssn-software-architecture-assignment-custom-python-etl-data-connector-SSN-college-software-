# Qualys SSL Labs ETL Connector

### Author
**Name:** G Kavin Rajan  
**Roll Number:** 3122225001057

---

### 🧩 Overview
This project implements a **Python-based ETL pipeline** using the [Qualys SSL Labs API](https://api.ssllabs.com/api/v3/).  
It extracts data from **three endpoints**, transforms it for readability, and loads it into **MongoDB**.

---

### 🔗 API Endpoints Used
1. `/info` → General API information (version, limits)
2. `/analyze` → SSL/TLS configuration and grading per host
3. `/getEndpointData` → In-depth endpoint security data

---

### ⚙️ ETL Flow
| Phase | Script | Description |
|-------|---------|-------------|
| Extract | `extract.py` | Calls API endpoints |
| Transform | `transform.py` | Cleans and structures the JSON |
| Load | `load.py` | Inserts into MongoDB |

---

### 🛠️ Setup
```bash
pip install -r requirements.txt
