# NetworkCalc ETL Connector

A small ETL (Extract → Transform → Load) utility for querying NetworkCalc public APIs, normalizing responses, and storing raw results in MongoDB for later analysis.

Overview

- Extracts data from endpoints such as:
  - /api/ip/{subnet}
  - /api/binary/{number}
  - /api/security/certificate/{hostname}
- Stores raw API responses with metadata in MongoDB collections.
- Includes retry/backoff logic to improve network resilience.

Project layout

| File             | Purpose                           |
| ---------------- | --------------------------------- |
| etl_connector.py | Main ETL script                   |
| requirements.txt | Python package requirements       |
| .env.example     | Sample environment variables file |
| README.md        | Project documentation             |

Getting started

1. Create and activate a virtual environment

Windows (CMD):
venv\Scripts\activate

PowerShell:
.\venv\Scripts\Activate.ps1

macOS / Linux:
source venv/bin/activate

2. Install dependencies

pip install -r requirements.txt

3. Configure environment

Copy and edit the environment file:

cp .env.example .env

Example values to set in .env:

MONGO_URI=mongodb://localhost:27017  
MONGO_DB=networkcalc_etl  
NETWORKCALC_BASE_URL=https://networkcalc.com/api

Usage

Run a single connector:

IP subnet lookup:
python etl_connector.py --mode ip --input "192.168.1.0/24"

Binary conversion (note: endpoint expects a binary string like 11111111):
python etl_connector.py --mode binary --input "11111111"

TLS/SSL certificate lookup:
python etl_connector.py --mode certificate --input "example.com"

Run all jobs together

Provide a JSON map for --input when using --mode all.

Windows / macOS / Linux:
python etl_connector.py --mode all --input '{"ip":"192.168.1.0/24","binary":"11111111","certificate":"example.com"}'

PowerShell (escape quotes):
python etl_connector.py --mode all --input '{\"ip\":\"192.168.1.0/24\",\"binary\":\"11111111\",\"certificate\":\"example.com\"}'

MongoDB storage

Collections created/used:

| Collection                  | Description                  |
| --------------------------- | ---------------------------- |
| networkcalc_ip_raw          | Raw IP subnet lookup results |
| networkcalc_binary_raw      | Binary conversion results    |
| networkcalc_certificate_raw | Certificate lookup responses |

Each document includes:

- source: api type (ip, binary, certificate)
- input: the query value provided
- fetched_at: UTC timestamp when data was retrieved
- raw: the full API response (JSON)

Design notes

- Uses requests with automatic retry/backoff for robustness.
- Persists raw API responses together with metadata for auditability.
- Public endpoints; no authentication required.
- Simple to extend for additional NetworkCalc endpoints or custom transformations.

Example run output

python etl_connector.py --mode all --input '{\"ip\":\"192.168.1.0/24\",\"binary\":\"11111111\",\"certificate\":\"example.com\"}'

Expected logging:

INFO GET https://networkcalc.com/api/ip/192.168.1.0/24  
INFO Inserted document id=... into networkcalc_etl.networkcalc_ip_raw  
INFO GET https://networkcalc.com/api/binary/11111111  
INFO Inserted document id=... into networkcalc_etl.networkcalc_binary_raw  
INFO GET https://networkcalc.com/api/security/certificate/example.com  
INFO Inserted document id=... into networkcalc_etl.networkcalc_certificate_raw

Commit guidance

- Do not commit .env (contains secrets). Add .env to .gitignore.
- Include your name and roll number in commit messages, e.g.:
  feat: add ETL connector implementation — John Doe (21CS123)

Summary
This connector retrieves and stores NetworkCalc data, applies simple normalization metadata, and saves results in MongoDB with retry/backoff handling for network errors.
