# Software Architecture - Assignment 1

**Rohan R – 3122225001108 – CSE B**

## GreyNoise IP ETL Connector

This project is a **Python ETL (Extract, Transform, Load) pipeline** that retrieves IP intelligence data from the **GreyNoise API**, transforms it into a MongoDB-friendly format, and stores it in a specified MongoDB collection.

---

## Features

- Fetches data for one or more IP addresses from GreyNoise.
- Cleans and structures the response JSON for MongoDB.
- Inserts processed records with timestamps for auditing.
- Handles API rate limits and retry logic using **exponential backoff**.
- Supports **dry-run mode** for testing without inserting into MongoDB.
- Allows batch processing from environment variables or an input file.

---

## API Endpoint Details

- **Base URL:** `https://api.greynoise.io`
- **Endpoint:** `/v3/ip/{ip_address}`
- **Method:** `GET`

### Headers Required

- **Query Parameters:** None (IP is part of the URL)
- **Example Request URL:** `https://api.greynoise.io/v3/ip/8.8.8.8`

---

## Authentication

- A valid **GreyNoise API key** is required.
- Store the key in a `.env` file (never commit this to Git).
- Credentials are loaded using the `python-dotenv` package.

---

## Project Structure

```
custom-python-etl-data-connector-rohanraja7/
├── etl_connector.py       # Main ETL script
├── ENV_TEMPLATE           # Template for environment variables
├── .gitignore             # Ignore .env and unnecessary files
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

---

## Environment Variables (.env)

```
GN_API_KEY=your_greynoise_api_key
GN_BASE_URL=https://api.greynoise.io
TARGET_IPS=8.8.8.8,1.1.1.1,1.2.3.4
INPUT_IPS_FILE=./ips.txt
MONGO_URI=mongodb://localhost:27017
MONGO_DB=greynoise_sa
CONNECTOR_NAME=greynoise_sa_riot
MONGO_COLLECTION_SUFFIX=_raw
REQUEST_TIMEOUT_SECONDS=10
MAX_RETRIES=5
INITIAL_BACKOFF_SECONDS=1.0
LOG_LEVEL=INFO
```

---

## Installation & Setup

1. **Clone your branch from the main repository:**

    ```bash
    git checkout main
    git pull origin main
    git checkout -b RohanR_3122225001108_B
    ```

2. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Create a `.env` file** with the required environment variables (never commit this file).

---

## Running the Connector

- **Run with default IPs from `.env`:**

    ```bash
    python etl_connector.py
    ```

- **Run in dry-run mode** (prints results without inserting into MongoDB):

    ```bash
    python etl_connector.py --dry-run
    ```

- **Override IP list from the command line:**

    ```bash
    python etl_connector.py --ips 8.8.8.8 1.1.1.1 1.2.3.4
    ```

---

## MongoDB Storage

- **Database:** `MONGO_DB`
- **Collection Name:** `{CONNECTOR_NAME}{MONGO_COLLECTION_SUFFIX}` (e.g., `greynoise_sa_riot_raw`)

Each document contains:

- Extracted and transformed fields from the API response
- Full raw payload (`raw`)
- `fetched_at` and `ingested_at` timestamps
- `_source.endpoint` to track the API URL

---

## Example Output (Dry-Run Mode)

```json
{
  "connector": "greynoise",
  "ip": "8.8.8.8",
  "business_service": null,
  "internet_scanner_summary": {
    "seen": true,
    "classification": "benign",
    "first_seen": "2024-07-01",
    "last_seen": "2024-08-10",
    "found": true,
    "actor": null,
    "bot": false,
    "vpn": false,
    "tags": ["public-dns"],
    "metadata": {}
  },
  "request_metadata": {
    "country": "US",
    "asn": "AS15169",
    "organization": "Google LLC"
  },
  "raw": { ... full API response ... },
  "fetched_at": "2025-08-13T12:34:56+00:00",
  "ingested_at": "2025-08-13T12:34:56+00:00",
  "_source": {
    "endpoint": "https://api.greynoise.io/v3/ip/8.8.8.8"
  }
```

## Output Screenshots 
![Sample Output]("C:\Users\rohan\Downloads\WhatsApp Image 2025-08-13 at 22.54.10.jpeg")

