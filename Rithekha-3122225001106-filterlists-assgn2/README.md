# 🧹 FilterLists ETL Pipeline

This project performs **ETL (Extract, Transform, Load)** operations on data from the [FilterLists Directory API](https://filterlists.com) and stores the structured data into **MongoDB** collections for further analysis or visualization.

---

## 📘 Overview

The ETL pipeline:
1. **Extracts** data from the FilterLists API endpoints.
2. **Transforms** the JSON response into structured records.
3. **Loads** the cleaned data into MongoDB collections (prefixed by `filterlists_`).

Each dataset (e.g., `lists`, `licenses`, `languages`, etc.) is stored in a separate MongoDB collection with timestamps for easy tracking.

---

## 🧰 Tech Stack

- **Language:** Python 3.x  
- **Database:** MongoDB  
- **API:** FilterLists Directory API  
- **Libraries:**  
  - `requests` – API data fetching  
  - `pymongo` – MongoDB interaction  
  - `python-dotenv` – Environment variable management  
  - `time`, `json`, `logging` – Utility modules  

---

## ⚙️ Environment Setup

Create a file named **`ENV_TEMPLATE`** in your project root.  
This file defines all environment variables required by the ETL pipeline.

### Example `ENV_TEMPLATE`
```
# FilterLists Directory API
FILTERLISTS_BASE_URL=https://api.filterlists.com

# MongoDB configuration
MONGODB_URI=your_mongodb_uri
DATABASE_NAME=your_database_name
COLLECTION_PREFIX=your_collection_prefix

# Request & retry settings
REQUEST_TIMEOUT_SECONDS=30
MAX_RETRIES=3
RETRY_BACKOFF_FACTOR=1.5
```

> ⚠️ Copy this file to `.env` and fill in your actual values before running the script.

---

## 🪜 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/filterlists-etl.git
   cd filterlists-etl
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate    # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp ENV_TEMPLATE .env
   # Edit .env with your MongoDB URI and database name
   ```

---

## 🚀 Running the ETL

Run the main ETL script to fetch and store data:

```bash
python etl_main.py
```

This will:
- Fetch all available FilterLists API datasets  
- Store them in MongoDB collections named like:  
  - `filterlists_lists_raw`
  - `filterlists_licenses_raw`
  - `filterlists_languages_raw`
  - etc.  

Each document includes an `ingested_at` timestamp.

---

## 🧩 Example MongoDB Document

```json
{
  "_id": { "$oid": "6520abc123..." },
  "id": 12,
  "name": "AdGuard Base filter",
  "description": "Removes ads and trackers",
  "license": "MIT",
  "syntax": "adblock",
  "homeUrl": "https://adguard.com/filter/base",
  "ingested_at": "2025-10-05T10:30:00Z"
}
```

---

## 🪄 Notes

- Each dataset is inserted using `insertMany()` for individual records (not nested arrays).
- Retry logic and timeout handling ensure resilience for failed API calls.
- MongoDB connection and collection naming are dynamically controlled via environment variables.

---

## 👩‍💻 Author

**Rithekha K**  
**CSE B**  
**Roll No:** 3122225001106  
Department of Computer Science and Engineering  
**Sri Sivasubramaniya Nadar College of Engineering**
