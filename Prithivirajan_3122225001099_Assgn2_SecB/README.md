# Custom Python ETL Connector

## APIs Integrated
1. **URLhaus (CSV)** → `https://urlhaus.abuse.ch/downloads/csv_online/`
2. **SonarQube Community Edition** → REST API endpoints

## ETL Steps
- **Extract:** Download CSV/JSON from API.
- **Transform:** Clean and add timestamp for auditing.
- **Load:** Insert into MongoDB collections.

## Collections
- `urlhaus_raw`
- `sonarqube_projects_raw`
- (extend with other SonarQube endpoints as required)

## Setup
```bash
pip install -r requirements.txt
cp ENV_TEMPLATE .env
python etl_connector.py
