
---




# CISA KEV ETL Data Connector

This project extracts data from the **CISA Known Exploited Vulnerabilities (KEV)** feed, transforms it into a structured format, and loads it into **MongoDB**.  
It is designed for cybersecurity threat intelligence ingestion and analysis.

---

## 1. Clone the Repository

```bash
git clone https://github.com/YourUsername/custom-cisa-kev-etl.git
cd custom-cisa-kev-etl
````

---

## 2. Create and Activate Virtual Environment

**Windows (CMD or PowerShell)**:

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Create and Configure `.env` File

The `.env` file stores **private configuration values** that your script uses.
It should be placed in the **root folder** of the project (next to `cisa_kev_etl.py`).

**Steps to create it:**

1. Make a new file in the project folder called `.env`
2. Open it with a text editor
3. Add the following **placeholders** and replace them with your own values:

```env
# MongoDB Configuration
MONGO_URI=your_mongodb_connection_string_here
DB_NAME=your_database_name_here
COLLECTION_NAME=your_collection_name_here

# API Configuration
CISA_URL=https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json
```

---

## 5. Run the ETL Script

```bash
python cisa_kev_etl.py
```

The script will:

* Download the CISA KEV feed
* Parse and structure the data
* Upsert records into your MongoDB collection

---

## 6. Verify Data in MongoDB

If MongoDB is running locally:

```bash
mongo
use your_database_name
db.your_collection_name.find().pretty()
```

---

```



