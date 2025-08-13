# Software Architecture Assignment

## Overview
This Python ETL connector retrieves IP intelligence data from the **GreyNoise API**, selects fields mentioned below, and stores the results in a MongoDB collection.
---

## Features
- **Extract**: Pull IP data from the GreyNoise `/v3/ip` API with `quick=false` for full details.
- **Transform**: Keep only key fields:
  - IP address
  - Classification
  - Service name and category
  - ASN and organization
  - Country, city
  - Last seen date
  - Ingestion timestamp
- **Load**: Save cleaned data into MongoDB for easy queries.

---

## Project Structure
```
/your-branch-name/
├── etl_connector.py      # Main ETL script
├── requirements.txt      # Python dependencies
├── .env                  # API key and MongoDB URI (not committed)
├── README.md             # Documentation (this file)
└── .gitignore            # Ignore .env, cache files, etc.
```

---

## Requirements
Your `requirements.txt` should contain:
```
requests
pymongo
python-dotenv
```

---

## Environment Variables
Create a `.env` file in the same directory as `etl_connector.py`:

```
GREYNOISE_API_KEY=your_api_key_here
MONGODB_URI=mongodb://localhost:27017

```
---

## How to Run

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the ETL:
   ```
   python etl_connector.py
   ```

3. The script will:
   - Call GreyNoise for the `test_ip` value.
   - Extract and simplify the data.
   - Insert the record into the `Greynoise` database, `IP_Data` collection in MongoDB.

---

## MongoDB Output Example
For IP `172.69.188.196`, a sample inserted document looks like:

```
{
  "ip": "172.69.188.196",
  "classification": "unknown",
  "service_name": "Cloudflare CDN",
  "service_category": "cdn",
  "asn": "AS13335",
  "organization": "Cloudflare, Inc.",
  "country": "Lithuania",
  "city": "Vilnius",
  "last_seen": "2025-08-12",
  "ingested_at": { "$date": "2025-08-12T18:30:00Z" }
}
```