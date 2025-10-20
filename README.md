# Cloudflare Trace API ETL Connector
**Course:** Software Architecture (Kyureeus EdTech, SSN CSE)  
**Assignment:** Custom Python ETL Data Connector  
**Student:** Anandharaj D (3122225001009, CSE A) , Assignment - 2

---

## 🎯 Overview
This ETL connector collects diagnostic data from **three Cloudflare Trace API endpoints**, transforms it into structured JSON, and loads it into a MongoDB database.

It demonstrates:
- Multi-endpoint data extraction  
- Secure use of `.env` variables  
- Data transformation and MongoDB insertion  
- Logging, error handling, and project structure best practices  

---

## 🧱 ETL Pipeline
**Extract → Transform → Load**

| Stage | Description |
|--------|--------------|
| **Extract** | Fetches raw trace data from: <br> - `https://www.cloudflare.com/cdn-cgi/trace` <br> - `https://1.1.1.1/cdn-cgi/trace` <br> - `https://cloudflare-dns.com/cdn-cgi/trace` |
| **Transform** | Converts plain text (key=value pairs) into JSON and adds metadata (`_source`, `_ingested_at`, `_timestamp`). |
| **Load** | Inserts structured records into MongoDB collection `cloudflare_trace_raw`. |

---

## ⚙️ Setup

1. Clone the assignment repository and checkout your branch:
   ```bash
   git checkout Anandharaj_D_3122225001009_CSE_A_ETL_ASSGN2
