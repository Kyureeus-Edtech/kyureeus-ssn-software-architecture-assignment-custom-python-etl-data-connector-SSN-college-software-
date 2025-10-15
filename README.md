OSV ETL Connector (provided to Nandy)

Contents
- etlconnector.py : Main ETL script that fetches data from OSV endpoints and stores into MongoDB.
- .env (example) : Environment variables (keep secrets out of source control).
- env_template : Template for .env.
- requirements.txt : Python dependencies.
- .gitignore : Recommended ignores.

Endpoints used (hard-coded in script; can be overridden via OSV_BASE_URL):
- GET  https://api.osv.dev/v1/vulns/OSV-2020-111
- GET  https://api.osv.dev/v1experimental/importfindings/almalinux-alba
- POST https://api.osv.dev/v1experimental/determineversion
- POST https://api.osv.dev/v1/query
- POST https://api.osv.dev/v1/querybatch

Quick start
1. Create a Python venv and install requirements:
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

2. Copy env_template to .env and fill MONGO_URI (and optional payloads):
   cp env_template .env
   # edit .env

3. Run the ETL:
   python etlconnector.py

What the ETL does
- For GET endpoints: fetches the response and inserts into the "osv_gets" collection.
- For POST endpoints: sends a sample payload (either from .env or defaults), inserts responses into "osv_posts" collection.
- Each stored document contains the response under 'data' and an 'ingested_at' UTC timestamp.
- The script is intentionally limited in scope (no retries/backoff beyond basic error handling) to be simple and easy to adapt.

Notes
- The script expects a reachable MongoDB instance; set MONGO_URI in .env.
- Feel free to adapt payloads, add pagination, or apply stricter validation as needed.

If you want any changes (different collection names, extra logging, or to remove MongoDB and write to files instead), tell me and I’ll update it.
