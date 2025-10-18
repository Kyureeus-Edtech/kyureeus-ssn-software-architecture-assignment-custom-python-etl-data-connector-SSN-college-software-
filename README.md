```markdown
# 🧩 RIPEstat ETL Connector

**Author:** Ann Maria Thomas  
**Roll Number:** 3122 22 5001 014

---

## 📘 Overview

This project implements a **custom ETL (Extract–Transform–Load) connector** for the **[RIPEstat API](https://stat.ripe.net/)** — a public data service providing Internet resource information such as IP prefixes, ASNs, and routing data.

The connector extracts real-time data from multiple RIPEstat endpoints, transforms it for MongoDB compatibility, and loads it into a structured MongoDB collection for analysis and auditing.

---

## 🧱 Project Structure
```

/branch-name/
├── etl_connector.py # Main ETL pipeline script
├── .env # Environment variables (not committed)
├── requirements.txt # Python dependencies
├── README.md # Documentation (this file)
└── .gitignore # Ensures secrets are not pushed

````

---

## ⚙️ Environment Setup

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd <your-branch-name>
````

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # for Linux/Mac
venv\Scripts\activate      # for Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file

```env
# .env
RIPESTAT_BASE_URL=https://stat.ripe.net/data
MONGO_URI=mongodb://localhost:27017/
```

> ⚠️ Ensure `.env` is listed in `.gitignore` before committing.

---

## 🧠 ETL Pipeline Design

### **1. Extract**

The script connects to the **RIPEstat API**, sends HTTP GET requests to selected endpoints, and retrieves **raw JSON** responses.

### **2. Transform**

The raw data is cleaned and reformatted into a MongoDB-friendly structure.
Each document includes:

- `timestamp`: UTC time of ingestion
- `result`: parsed data section from the API response
- `status`: request status (e.g., success, error)

### **3. Load**

The transformed data is inserted into the MongoDB collection:

```
Database: ripe_database
Collection: ripestat_raw
```

Each record is timestamped for traceability and auditing.

---

## 🌐 API Endpoints Used

| Endpoint          | Description                                              | Example Parameters           |
| ----------------- | -------------------------------------------------------- | ---------------------------- |
| `/network-info`   | Provides general information about a network prefix.     | `{"resource": "8.8.8.0/24"}` |
| `/as-overview`    | Summarizes information for a specific Autonomous System. | `{"resource": "AS15169"}`    |
| `/routing-status` | Shows current routing and reachability status of an AS.  | `{"resource": "AS3333"}`     |

---

## ▶️ Running the Connector

Execute the following command:

```bash
python etl_connector.py
```

---

## 🖥️ Example Terminal Output

```bash
--- Processing network-info ---
Extracting data from: https://stat.ripe.net/data/network-info/data.json
✅ Data extracted successfully
Transformed document ready for MongoDB insertion:
{
    "timestamp": "2025-10-18T05:42:00Z",
    "result": {
        "prefix": "8.8.8.0/24",
        "resource": "8.8.8.0/24",
        "asns": [15169],
        "holders": ["Google LLC"]
    },
    "status": "ok"
}
✅ Data inserted successfully

--- Processing as-overview ---
✅ Data extracted successfully
✅ Data inserted successfully

--- Processing routing-status ---
⚠️ Error fetching data from routing-status: HTTPSConnectionPool(host='stat.ripe.net', port=443): Read timed out. (read timeout=10)
⚠️ No data to insert
```

---

## 🗃️ MongoDB Example Document

```json
{
  "_id": { "$oid": "67122a5b8f18b50e8a9e6a41" },
  "timestamp": "2025-10-18T05:42:00Z",
  "result": {
    "resource": "AS15169",
    "announced": true,
    "locations": ["Europe", "North America"]
  },
  "status": "ok"
}
```

---

## 🔍 Validation & Error Handling

- Automatically retries failed requests due to network timeouts
- Skips empty or invalid API responses
- Logs clear success/error messages in the terminal
- Includes `timeout=10` seconds for responsiveness

---

## 🧾 MongoDB Collection Strategy

- **Collection Name:** `ripestat_raw`
- **Database Name:** `ripe_database`
- **Structure:** One collection per connector
- **Audit Fields:** `timestamp`, `status`

---

## 🚀 Future Improvements

- Add retry logic and exponential backoff for rate-limited requests
- Store logs in a separate collection (`etl_logs`)
- Implement pagination handling for larger datasets
- Automate periodic ETL runs via `cron` or `Airflow`

---

## 🧩 Requirements

List these dependencies in your `requirements.txt` file:

```
requests
pymongo
python-dotenv
```

---

## ⚡ Troubleshooting

| Issue                       | Possible Fix                                                            |
| --------------------------- | ----------------------------------------------------------------------- |
| Timeout or connection error | Check internet or API availability                                      |
| MongoDB insert fails        | Verify `MONGO_URI` and database permissions                             |
| `.env` not loaded           | Ensure `python-dotenv` is installed and `.env` is in the same directory |

```

```
