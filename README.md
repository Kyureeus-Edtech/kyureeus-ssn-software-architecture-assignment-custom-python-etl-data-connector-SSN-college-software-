# 🌐 Cloudflare Trace ETL Pipeline

## Overview
This project implements a lightweight **ETL (Extract–Transform–Load)** pipeline to collect, process, and store **Cloudflare Trace** data from multiple endpoints into a **MongoDB** database.

Each endpoint (`/cdn-cgi/trace`) exposes connection metadata such as IP, data center, TLS version, and client information.  
The ETL pipeline extracts this data, adds timestamps and identifiers, and upserts it into MongoDB for analysis or monitoring.

---

## 🧩 Features
- Extracts Cloudflare Trace data from **three different hosts**.
- Transforms raw text data into structured JSON records.
- Adds `ingestion_timestamp`, `host`, and `host_ts` for versioned tracking.
- Performs **bulk upsert** operations into MongoDB for efficient storage.
- Modular design — each endpoint has its own configuration file.

---

## 🗂 Project Structure
```

cloudflare-trace-etl/
│
├── main_cf_trace_etl.py           # Core ETL controller
├── endpoint_cf_trace_1.py         # Endpoint 1 config (example.com)
├── endpoint_cf_trace_2.py         # Endpoint 2 config (yourdomain.com)
├── endpoint_cf_trace_3.py         # Endpoint 3 config (anotherdomain.com)
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
└── README.md                      # Project documentation

````

---

## ⚙️ Setup Instructions

### 1️⃣ Prerequisites
- **Python 3.9+**
- **MongoDB** (Atlas Cloud or local instance)
- Internet access to fetch Cloudflare `/cdn-cgi/trace`

---

### 2️⃣ Clone & Install
```bash
git clone https://github.com/yourusername/cloudflare-trace-etl.git
cd cloudflare-trace-etl
pip install -r requirements.txt
````

---

### 3️⃣ Configure Environment

Create a `.env` file in the root folder (use `.env.example` as reference):

```bash
MONGO_URI=mongodb+srv://etl_user:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
DB_NAME=cybersecurity_data
```

> 💡 If running MongoDB locally:
>
> ```
> MONGO_URI=mongodb://etl_user:StrongPass!@localhost:27017/?authSource=admin
> DB_NAME=cybersecurity_data
> ```

---

### 4️⃣ Configure Endpoints

Edit the endpoint files to match your own Cloudflare-proxied hosts:

Example (`endpoint_cf_trace_1.py`):

```python
ENDPOINT_CONFIG = {
    "name": "CF Trace for example.com",
    "api_type": "cf_trace",
    "host": "example.com",
    "format": "json",
    "collection": "cf_trace_example",
    "data_key_path": [],
    "id_key": "host_ts"
}
```

Repeat for `endpoint_cf_trace_2.py` and `endpoint_cf_trace_3.py`.

> ✅ Each endpoint is treated as an independent data source but stored under the same schema.

---

### 5️⃣ Run the ETL

```bash
python main_cf_trace_etl.py
```

You’ll see logs like:

```
2025-10-18 13:05:42 - INFO - [CF TRACE] Fetching: https://example.com/cdn-cgi/trace
2025-10-18 13:05:43 - INFO - Transforming 1 records...
2025-10-18 13:05:43 - INFO - MongoDB write to 'cf_trace_example' complete.
```

---

## 📊 Example Output (MongoDB)

Each document will look like:

```json
{
  "_id": "652f1c2b1c0a6aabc1234567",
  "host": "example.com",
  "ip": "203.0.113.45",
  "ts": 1729277000,
  "host_ts": "example.com_1729277000",
  "colo": "BOM",
  "tls": "TLSv1.3",
  "http": "2",
  "loc": "IN",
  "ingestion_timestamp": "2025-10-18T08:53:00Z"
}
```

---

## 🧠 How It Works

| Stage         | Function             | Description                                                        |
| ------------- | -------------------- | ------------------------------------------------------------------ |
| **Extract**   | `extract_cf_trace()` | Fetches `/cdn-cgi/trace`, parses `key=value` pairs.                |
| **Transform** | `transform_data()`   | Adds timestamps, host info, and normalizes schema.                 |
| **Load**      | `load_data()`        | Bulk upsert into MongoDB collection using `host_ts` as unique key. |

---

## 🧰 Troubleshooting

| Issue                                        | Cause                      | Fix                                            |
| -------------------------------------------- | -------------------------- | ---------------------------------------------- |
| `pymongo.errors.ServerSelectionTimeoutError` | MongoDB not reachable      | Check `MONGO_URI`, whitelist your IP in Atlas  |
| `requests.exceptions.ConnectionError`        | Host not behind Cloudflare | Use valid Cloudflare-protected domain          |
| Missing collection                           | No valid records inserted  | Ensure Cloudflare Trace returns non-empty data |

---

## 🧾 API Reference

### Cloudflare Trace Endpoint

```
GET https://<your-domain>/cdn-cgi/trace
```

**Response (plain text):**

```
fl=145f91
h=example.com
ip=203.0.113.45
ts=1729277000
visit_scheme=https
tls=TLSv1.3
colo=BOM
sni=plaintext
warp=off
gateway=off
```

The ETL automatically converts this to JSON and augments it.

---

## 🧪 Testing Connection

```bash
curl https://example.com/cdn-cgi/trace
```

If you see plain-text key=value lines, your endpoint is ready.

---

## 📦 Future Enhancements

* Add **Cloudflare Logpull API** integration.
* Support asynchronous batch runs via `asyncio`.
* Include Grafana dashboard for live visualization.

---

## 👤 Author

**Saisandeep Sangeetham**<br>
*B.E. Computer Science & Engineering, SSN College of Engineering*
📧 [saisandeep2210495@ssn.edu.in](mailto:saisandeep2210495@ssn.edu.in)



