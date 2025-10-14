# Cloudflare Request Tracer ETL Connector

---

## 📘 API Provider
**Name:** Cloudflare Request Tracer  
**Base URL:** https://api.cloudflare.com/client/v4  
**Endpoint:** /accounts/{ACCOUNT_ID}/request-tracer/trace  
**Authentication:** Required (X-Auth-Email, X-Auth-Key)

---

## 🧠 Description
This connector uses the authenticated Cloudflare API to trace HTTP requests through Cloudflare’s network.  
It extracts trace data, transforms key fields, and stores them into MongoDB for analysis and debugging.

---

## ⚙️ Pipeline Design
| Stage | Function | Description |
|--------|-----------|-------------|
| **Extract** | `extract_data()` | Sends a POST request to Cloudflare Request Tracer API |
| **Transform** | `transform_data()` | Parses and restructures JSON into key metrics |
| **Load** | `load_data()` | Inserts the result into MongoDB collection |

---

## 🗃️ MongoDB
- **Database:** `Cloudflare`  
- **Collection:** `Request_Trace_Raw`  
- Each record includes an `ingested_at` timestamp for audit tracking.

---

## ▶️ Run Instructions
1. Install dependencies  
   ```bash
   pip install -r requirements.txt
