# PhishTank ETL Pipeline

**Author:** Pravin
**Branch / Roll Number:** B.E CSE / 3122225001097

---

## Overview

This project is a Python-based ETL (Extract, Transform, Load) pipeline that fetches phishing URL data from PhishTank, transforms it into a clean format, and loads it into a MongoDB collection. It is designed for efficient bulk ingestion and safe handling of CSV data.

## Features

* Downloads the latest PhishTank CSV dataset.
* Cleans and transforms data, including:

  * Stripping whitespace
  * Converting `verified` field to boolean
  * Parsing `submission_time` to `datetime`
  * Adding `ingested_at` timestamp
* Supports **row limit** for testing or partial loads.
* Performs **bulk upserts** to MongoDB for efficiency.
* Handles network retries and bulk write errors gracefully.

## Prerequisites

* Python 3.9+
* MongoDB instance (local or cloud)
* PhishTank account (for API key, optional)

### Required Python Packages

```bash
pip install -r requirements.txt
```

Example `requirements.txt`:

```
pymongo
requests
python-dotenv
```

## Setup

1. **Clone the repository:**

```bash
git clone https://github.com/Kyureeus-Edtech/custom-python-etl-data-connector-Pravin-byte.git
cd custom-python-etl-data-connector-Pravin-byte
git checkout etl-pravin-097
```

2. **Create a `.env` file** in the root directory:

```
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/etl_db
PHISHTANK_URL=https://data.phishtank.com/data/online-valid.csv
```

> ⚠️ Do not commit your `.env` file. Make sure `.gitignore` contains `.env`.

## Usage

Run the ETL script:

```bash
python etl/phishtank_etl.py
```

Optional parameters in the script:

* `limit` – number of rows to process (useful for testing)
* `batch_size` – number of rows per bulk write (default: 1000)

Example:

```python
extract_and_load(limit=500, batch_size=500)
```

## MongoDB Schema

**Collection:** `phishtank_raw`

| Field             | Type     | Description                          |
| ----------------- | -------- | ------------------------------------ |
| `phish_id`        | String   | Unique PhishTank ID                  |
| `url`             | String   | Phishing URL                         |
| `submission_time` | Datetime | Time of submission                   |
| `verified`        | Boolean  | Whether URL is confirmed phishing    |
| `ingested_at`     | Datetime | UTC timestamp when data was ingested |

## Notes

* Verified URLs (`verified: true`) are considered confirmed phishing URLs.
* HTTPS does not imply safety; treat all `verified` URLs as malicious.
* For large datasets, consider downloading the CSV locally to avoid hitting API rate limits.

