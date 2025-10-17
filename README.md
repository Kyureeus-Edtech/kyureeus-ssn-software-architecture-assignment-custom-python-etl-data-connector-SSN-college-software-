# RDAP ETL Connectors — SSN Software Architecture Assignment

This package contains an ETL connector script that extracts RDAP (Registration Data Access Protocol)
data from **three** providers (ARIN, RIPE, APNIC), transforms it for auditing and compatibility,
and loads the results into MongoDB collections.

## Files
- `etl_connector.py` — Main ETL script. Supports connectors: `arin`, `ripe`, `apnic`, or `all`.
- `requirements.txt` — Python dependencies
- `.gitignore` — ignore `.env` and other artifacts
- `.env.sample` — sample environment variables file

## Setup (local)
1. Create and activate a Python venv (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # on Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Prepare `.env` file (do **not** commit):
   ```text
   MONGO_URI=mongodb://localhost:27017
   MONGO_DB=rdap_etl_db
   ```
   Save it as `.env` in same folder.

3. Run the script:
   ```bash
   # query two IPs from ARIN
   python etl_connector.py --connector arin --ips 8.8.8.8,1.1.1.1

   # query from file
   python etl_connector.py --connector all --ips-file ips.txt
   ```

Output collections in MongoDB (database from `.env`):
- `rdap_arin_raw`
- `rdap_ripe_raw`
- `rdap_apnic_raw`
