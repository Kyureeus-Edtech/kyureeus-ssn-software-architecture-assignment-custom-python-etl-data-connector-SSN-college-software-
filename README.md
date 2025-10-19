# GreyNoise Custom ETL Connector

**Name:** Vidisha Desai

**Section**: CSE - C

**Roll Number:** 3122225001154


## Overview
This Python ETL pipeline securely connects to the GreyNoise API and extracts malware and network threat intelligence from three critical endpoints:
1. **IP Lookup** (`/v3/ip/{ip}`) — retrieves metadata, ASN, reverse DNS, actors, tags, and recent activity about a given IP address.
2. **CVE Information** (`/v1/cve/{cve_id}`) — fetches detailed information about specific Common Vulnerabilities and Exposures (CVEs).
3. **Community IP Lookup** (`/v3/community/{ip}`) — returns community-level insight on IP addresses from GreyNoise’s freely accessible dataset.

The pipeline follows a standard **Extract → Transform → Load** pattern, loading data into **MongoDB collections** with **timestamps** for auditing. Each endpoint’s data is stored in its dedicated MongoDB collection to maintain data organization and clarity.

---

## Features
- Secure API authentication using environment variables
- Robust error handling for connection failures, rate limits, invalid responses, and empty results
- Separate MongoDB collections for each endpoint’s raw data storage
- Detailed logging of raw data, transformed data, and insertion results for traceability
- Easy extendability for adding new endpoints or integrations

---

## Prerequisites

- Python 3.7 or above
- MongoDB instance (local or cloud)
- GreyNoise API key with v1 and v3 access

---

## Installation

1. Clone this repository and navigate to your branch.
2. Create a `.env` file in the root directory and add:
`GREYNOISE_API_KEY=your_actual_api_key`
`MONGO_URI=mongodb://localhost:27017/`
3. Install dependencies: `pip install -r requirements.txt`

---

## Usage

Run the ETL pipeline: `python etl_connector.py`


The script will:
- Extract data from the three GreyNoise endpoints (IP Lookup, CVE, Community)
- Transform the data into a uniform JSON structure with ingestion timestamps
- Load each dataset into separate MongoDB collections:
  - `greynoise_ip_lookup_raw`
  - `greynoise_cve_lookup_raw`
  - `greynoise_community_lookup_raw`

---

## MongoDB Document Structure

Each document inserted into MongoDB will have this format:

{
"source": "ip_lookup", // Endpoint name

"data": { ... }, // Raw JSON data from API

"ingested_at": "2025-10-19T18:00:00Z" // UTC timestamp of ingestion
}


This structure supports audits, data updates, and querying by source.

---

## Error Handling & Validation

- Detects HTTP errors and prints meaningful messages including rate-limit errors (HTTP 429)
- Warns on empty payloads or partial data responses
- Handles network/connectivity exceptions gracefully
- Skips loading data into MongoDB if data is invalid or missing
- Logs inserted document IDs and total number of successful inserts for verification

---










