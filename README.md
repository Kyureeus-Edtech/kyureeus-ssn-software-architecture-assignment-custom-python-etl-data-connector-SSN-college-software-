

# 🧠 GreyNoise Multi-Endpoint ETL Data Connector

**Name:** Logeshwari L
**Roll Number:** 3122225001304

---

## 📘 Overview

This project is part of the **Software Architecture – ETL Data Connector Assignment** (Kyureeus EdTech, SSN CSE).
It extends the earlier single-endpoint connector to handle **multiple API endpoints** from GreyNoise — a threat intelligence provider.

The ETL pipeline follows:

```
Extract → Transform → Load (ETL)
```

Each endpoint’s data is extracted, optionally transformed, and stored into a **MongoDB collection** for analysis or reporting.

---

## ⚙️ Architecture

### 🔹 Pipeline Stages

**Extract:**

* Connects to multiple GreyNoise endpoints via REST API calls.
* Each endpoint is called sequentially, and responses are validated.

**Transform:**

* Basic validation and structuring of JSON payloads.
* Adds module metadata (endpoint name, fetch timestamp, etc.).

**Load:**

* Inserts each endpoint’s result into a MongoDB collection.
* Includes ingestion timestamps for tracking and versioning.

---

## 🌐 Endpoints Used

The connector fetches data from multiple GreyNoise API modules (v3):

| Endpoint                           | Description                         | Example URL                                                   |
| ---------------------------------- | ----------------------------------- | ------------------------------------------------------------- |
| `/v3/ping`                         | Tests API connectivity              | `https://api.greynoise.io/v3/ping`                            |
| `/v3/community/{ip}`               | Community lookup for IP reputation  | `https://api.greynoise.io/v3/community/8.8.8.8`               |
| `/v3/ip/{ip}`                      | Detailed IP context data            | `https://api.greynoise.io/v3/ip/8.8.8.8`                      |
| `/v3/gnql/query`                   | Run GNQL queries for noise data     | `https://api.greynoise.io/v3/gnql/query?query=last_seen:1d`   |
| `/v3/gnql/stats`                   | Statistics summary for GNQL queries | `https://api.greynoise.io/v3/gnql/stats?query=last_seen:30d`  |
| `/v3/noise/ips/{ip}/daily-summary` | Daily noise activity summary per IP | `https://api.greynoise.io/v3/noise/ips/8.8.8.8/daily-summary` |
| `/v3/ip/similar/{ip}`              | Finds IPs similar in behavior       | `https://api.greynoise.io/v3/ip/similar/8.8.8.8`              |
| `/v3/tags`                         | Lists GreyNoise tag metadata        | `https://api.greynoise.io/v3/tags`                            |

---

## 🔑 Secure Configuration

All credentials and environment settings are stored securely in a **`.env`** file (not committed to Git).

**Example `.env` file:**

```
GREYNOISE_API_KEY=your_api_key_here
MONGO_URI=mongodb://localhost:27017
MONGO_DB=threat_intel
COLLECTION_NAME=greynoise_full
TARGET_IP=8.8.8.8
```

**`.gitignore` contents:**

```
.env
__pycache__/
```

---

## 🧩 Project Structure

```
/greynoise-multi-endpoint/
├── etl_connector.py
├── .env
├── requirements.txt
├── README.md
└── logs/      # Optional for extended logging
```

* `etl_connector.py`: Main ETL script
* `.env`: Secure credentials (local only)
* `requirements.txt`: Python dependencies
* `README.md`: Documentation & usage instructions
* `logs/`: Optional folder for logs
