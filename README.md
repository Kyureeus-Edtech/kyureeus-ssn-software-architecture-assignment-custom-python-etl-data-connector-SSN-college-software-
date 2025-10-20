# NetworkCalc ETL Connector

This project implements an ETL (Extract–Transform–Load) connector for the NetworkCalc public APIs.  
It extracts network-related data, transforms it into a standard format, and loads it into MongoDB for storage and analysis.

---

## Project Structure

| File | Description |
|------|--------------|
| etl_connector.py | Main ETL pipeline script |
| requirements.txt | Python dependencies |
| .env.example | Example environment configuration |
| README.md | Documentation (this file) |

---

## Setup Instructions

### 1. Create and Activate a Virtual Environment

`python -m venv venv`

Activate the virtual environment:

- Windows (CMD):  
  `venv\Scripts\activate`

- PowerShell:  
  `.\venv\Scripts\Activate.ps1`

- macOS/Linux:  
  `source venv/bin/activate`

---

### 2. Install Dependencies

`pip install -r requirements.txt`

---

### 3. Configure Environment

Copy the example environment file and modify as needed:

`cp .env.example .env`

Edit .env to configure database and API settings:

MONGO_URI=mongodb://localhost:27017  
MONGO_DB=networkcalc_etl  
NETWORKCALC_BASE_URL=https://networkcalc.com/api

---

## Usage

You can run the connector in different modes to extract specific datasets.

### IP Subnet Lookup

`python etl_connector.py --mode ip --input "192.168.1.0/24"`

### Binary Conversion

Note: The /api/binary/{number} endpoint expects a binary string (for example, 11111111), not a decimal number.

`python etl_connector.py --mode binary --input "11111111"`

### TLS/SSL Certificate Lookup

`python etl_connector.py --mode certificate --input "example.com"`

---

## Running All Jobs Together

You can run all three connectors at once using the --mode all option.

Windows CMD or macOS/Linux:  
`python etl_connector.py --mode all --input '{"ip":"192.168.1.0/24","binary":"11111111","certificate":"example.com"}'`

PowerShell (requires escaped quotes):  
`python etl_connector.py --mode all --input '{\"ip\":\"192.168.1.0/24\",\"binary\":\"11111111\",\"certificate\":\"example.com\"}'`

---

## MongoDB Output

Data is stored in the following MongoDB collections:

| Collection | Description |
|-------------|-------------|
| networkcalc_ip_raw | Raw IP subnet lookup results |
| networkcalc_binary_raw | Binary conversion results |
| networkcalc_certificate_raw | SSL certificate lookup data |

Each record includes:
- source: API type (ip, binary, certificate)
- input: The query value
- fetched_at: UTC timestamp of retrieval
- raw: Full API response JSON

---

## Design Notes

- Built with requests and automatic retry/backoff for network stability.  
- Inserts raw API responses with metadata for traceability.  
- Public endpoints — no authentication required.  
- Easily extensible to support more NetworkCalc APIs or custom data transformations.

---

## Example Successful Run

`python etl_connector.py --mode all --input '{\"ip\":\"192.168.1.0/24\",\"binary\":\"11111111\",\"certificate\":\"example.com\"}'`

Expected output:

INFO     GET https://networkcalc.com/api/ip/192.168.1.0/24  
INFO     Inserted document id=... into networkcalc_etl.networkcalc_ip_raw  
INFO     GET https://networkcalc.com/api/binary/11111111  
INFO     Inserted document id=... into networkcalc_etl.networkcalc_binary_raw  
INFO     GET https://networkcalc.com/api/security/certificate/example.com  
INFO     Inserted document id=... into networkcalc_etl.networkcalc_certificate_raw  

---

## Commit and Submission Guidelines

- Do not commit .env (it contains sensitive information).  
- Add .env to your .gitignore file.  
- Commit messages should include your name and roll number, for example:  
  feat: add ETL connector implementation — John Doe (21CS123)

---

## Summary

This ETL connector:
- Fetches and stores data from NetworkCalc public APIs  
- Handles retries, validation, and structured storage  
- Demonstrates clean modular design for ETL systems