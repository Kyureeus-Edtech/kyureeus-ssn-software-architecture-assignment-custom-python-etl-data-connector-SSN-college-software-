# IP-API ETL Data Connector

## Overview

This project is a **modular ETL (Extract, Transform, Load) pipeline** that fetches geolocation and network data using the [IP-API](https://ip-api.com/docs) service.

The connector supports **three API call types**:

1. **Single IP Query** (`/json/{query}`)
2. **Batch IP Query** (`/batch`)
3. **Pro Endpoint with fields filtering** (using `fields` and `lang` query params)

All extracted data is cleaned, transformed for MongoDB compatibility, and stored in the collection `ipapi`.

---


## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/ckritk/kyureeus-ssn-software-architecture-assignment-custom-python-etl-data-connector-SSN-college-software-/edit/3122225001066_Krithika_C_CSE_B_Assignment_2/
cd ipapi_connector
```

### 2. Create and Configure `.env` using the provided ENV_TEMPLATE

> Never commit `.env` files to Git.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run MongoDB (if not already running)

Make sure your MongoDB instance is active locally or in the cloud.

### 5. Execute the ETL Pipeline

```bash
python etl_connector.py
```

---

## How It Works

### **Extract**

* Fetches data from IP-API using:

  * Single query (`https://ip-api.com/json/{ip}`)
  * Batch query (`https://ip-api.com/batch`)
  * Pro query with specific fields and language (`https://pro.ip-api.com/json/{ip}`)
* Handles rate limits, empty responses, and API errors.

### **Transform**

* Converts nested structures to MongoDB-compatible documents.
* Adds ingestion timestamp for auditing.
* Normalizes field names and ensures consistent schema.

### **Load**

* Inserts records into `ipapi_raw` collection.
* Ensures no duplicate inserts for the same IP/timestamp.

---

## Testing & Validation

* Handles invalid IPs and empty payloads.
* Logs API failures and retry attempts.
* Validates MongoDB insertions.

---
## Example Output (MongoDB Document)

```json
{
  "query": "8.8.8.8",
  "country": "United States",
  "regionName": "California",
  "city": "Mountain View",
  "zip": "94043",
  "lat": 37.4056,
  "lon": -122.0775,
  "timezone": "America/Los_Angeles",
  "isp": "Google LLC",
  "org": "Google Public DNS",
  "as": "AS15169 Google LLC",
  "timestamp": "2025-10-17T10:42:00Z"
}
```
---
