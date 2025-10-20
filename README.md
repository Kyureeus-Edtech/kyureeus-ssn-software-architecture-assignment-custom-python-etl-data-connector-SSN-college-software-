# RDAP ETL Pipeline

This project is a simple **Extract–Transform–Load (ETL)** pipeline that fetches **Registration Data Access Protocol (RDAP)** data from [rdap.org](https://rdap.org/) and stores it into a MongoDB database.

It retrieves information about **domains**, **IP addresses**, and **autonomous system numbers (ASNs)**, transforms the data to make it MongoDB-safe, and loads it into a specified collection for analysis or auditing.

---

## 🧩 Features

* Fetches RDAP data from three endpoints:

  * `/domain/{domain}`
  * `/ip/{ipAddress}`
  * `/autnum/{asnNumber}`
* Cleans data for MongoDB compatibility (replaces `.` and `$` in keys)
* Inserts all records into MongoDB with timestamps
* Handles network and API errors gracefully with structured logging

---

## 🏗️ Project Structure

```
rdap_etl/
├── etl_rdap.py      # Main ETL script
├── .env             # Environment variables (not committed to git)
├── requirements.txt # Python dependencies
└── README.md        # This file
```

---

## ⚙️ Requirements

* **Python 3.8+**
* **MongoDB** instance (local or remote)
* API access to [rdap.org](https://rdap.org/) (public and free)

---

## 📦 Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/rdap-etl.git
   cd rdap-etl
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate   # on macOS/Linux
   venv\Scripts\activate      # on Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## 🔧 Environment Setup

Create a `.env` file in the project root with the following variables:

```env
RDAP_BASE_URL=https://rdap.org/
MONGO_URI=mongodb://localhost:27017
MONGO_DB=etl_db
MONGO_COLLECTION=rdap_data
```

---

## ▶️ Running the ETL

Run the ETL process:

```bash
python etl_rdap.py
```

By default, the script will fetch RDAP data for:

* Domains: `example.com`, `openai.com`
* IPs: `8.8.8.8`, `2001:4860:4860::8888`
* ASN: `15169`

You can modify these lists in the `run_etl()` function inside `etl_rdap.py`.

---

## 🗄️ MongoDB Output

Each inserted document has the following structure:

```json
{
  "object_type": "domain",
  "object_key": "example.com",
  "rdap_data": { ...sanitized RDAP JSON... },
  "ingested_at": "2025-10-20T12:34:56.789Z"
}
```

---

## 🧥 Logging

Logs are printed to the console and include:

* Fetch start/completion per endpoint
* Warnings for failed requests
* MongoDB insertion stats
* Exception traces (if any)

Example log output:

```
2025-10-20 14:12:45 [INFO] Fetching RDAP domain data for: example.com
2025-10-20 14:12:46 [INFO] Inserted 3 RDAP records into etl_db.rdap_data
2025-10-20 14:12:46 [INFO] ETL process completed successfully.
```

---

## 🧠 Notes

* RDAP APIs are **rate-limited** — avoid sending too many requests simultaneously.
* The script automatically sanitizes MongoDB keys to prevent insertion errors.
* You can extend this project to include other RDAP objects like:

  * `/entity/{handle}`
  * `/nameserver/{hostname}`

---

## 📜 License

This project is open-source and available under the **MIT License**.
