# AlienVault OTX ETL Connector

## Overview

This Python ETL connector extracts subscribed threat intelligence pulses from the AlienVault Open Threat Exchange (OTX) API and loads them into a MongoDB collection. The pipeline handles API authentication securely, paginates through results, transforms pulse data for MongoDB, and avoids duplicates by enforcing a unique index.

---

## API Endpoint Details

- **Base URL:** `https://otx.alienvault.com/api/v1`
- **Endpoint:** `/pulses/subscribed`
- **HTTP Method:** `GET`
- **Authentication:** API key required via `X-OTX-API-KEY` header
- **Pagination:** Supports `page` and `limit` query parameters
- **Rate Limiting:** The API returns HTTP 429 with `Retry-After` header; the ETL respects this by waiting and retrying

### Example Request

GET https://otx.alienvault.com/api/v1/pulses/subscribed?page=1&limit=50
Headers:
X-OTX-API-KEY: your_api_key_here

---

## API Usage in ETL Script

- The script loads the API key from a local `.env` file using the `dotenv` library.
- It sends authenticated requests with the required header.
- Pagination is handled by iterating over pages until the API returns no next page.
- Rate limits are handled by checking HTTP 429 responses and pausing before retrying.

---

## Running the ETL Pipeline

1. Create a `.env` file with:
   OTX_API_KEY=your_actual_api_key
   MONGO_URI=mongodb://localhost:27017
2. Install dependencies:
   pip install -r requirements.txt
3. Run the ETL:

python etl_connector.py

Logs will show progress per page including how many records received and inserted.

---

## MongoDB Example Output

Documents stored in the `otx_pulses_raw` collection have fields like:

{
"pulse_id": "689dfd7bcdd65dfb01307de4",
"name": "PhantomCard: New NFC-driven Android malware emerging in Brazil",
"description": "A new Android Trojan called PhantomCard is targeting banking customers in Brazil...",
"created": "2025-08-14T15:15:07.747000",
"modified": "2025-08-14T15:27:09.947000",
"indicator_count": 10,
"subscriber_count": 150,
"tags": ["malware", "android", "phishing"],
"tlp": "white",
"public": 1,
"adversary": "Go1ano developer",
"industries": ["financial-services"],
"targeted_countries": ["BR"],
"references": ["https://example.com/security-report"],
"ingested_at": "2025-08-14T15:30:00Z"
}

---

## Project Structure

/custom-python-etl-data-connector-Harish/
├── etl_connector.py # Main ETL script
├── .env # Environment variables (excluded from repo)
├── requirements.txt # Python dependencies list
├── README.md # This documentation file
└── (other configs/scripts as needed)

---

## Git and Submission Guidelines

- Do NOT commit your `.env` file.
- Include descriptive commit messages with your name and roll number.
- Push your branch and submit a Pull Request.
