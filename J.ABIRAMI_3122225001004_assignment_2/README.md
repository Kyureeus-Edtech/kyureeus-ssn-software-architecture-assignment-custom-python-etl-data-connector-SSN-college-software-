# Assignment 2 — SSL Labs ETL Connector

## What this does
This folder contains a Python ETL connector that:
- Calls SSL Labs API endpoints (`info`, `analyze`, `getEndpointData`, `getRootCertsRaw`)
- Normalizes results and loads them into MongoDB

## Files
- `sarch_assign_2.py` — main ETL script
- `domains.txt` — sample domains list (one domain per line)
- `.env.example` — example environment variables (do not commit actual .env with secrets)

## Requirements
```bash
pip install requests pymongo python-dotenv
