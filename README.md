SSN College – Software Architecture Assignment
Software Architecture Assignment: Custom Python ETL Data Connector
CISA KEV ETL Connector

Overview
This ETL script fetches data from the CISA Known Exploited Vulnerabilities (KEV) Catalog, transforms it by sanitizing keys and adding an ingestion timestamp, and loads the data into a MongoDB collection.

Source URL: CISA KEV JSON Feed
Authentication Required: No

Guidelines: Building and Managing Custom Data Connectors (ETL Pipeline) in Python
1. Setting Up the Connector Environment
Choose Your API Provider: CISA KEV JSON feed.

Understand the API Documentation:

Base URL: https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json

Response Format: JSON

No authentication required.

2. Secure API Authentication Using Environment Variables
Create a .env file locally to store configuration variables:

text
CISA_KEV_URL=https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json
MONGO_URI=mongodb://localhost:27017
MONGO_DB=etl_db
MONGO_COLLECTION=cisa_kev
Install and use python-dotenv to load them in your script.

Add .env to .gitignore to avoid committing credentials/configs.

3. Design the ETL Pipeline
Extract: Fetch JSON data from the CISA KEV API.

Transform: Clean MongoDB-incompatible keys (e.g., . and $) and add an ingested_at UTC timestamp.

Load: Bulk insert into the MongoDB collection for better performance.

4. MongoDB Collection Strategy
Database: etl_db

Collection: cisa_kev

Store each vulnerability record with ingested_at timestamp for audit and tracking.

5. Iterative Testing & Validation
Test for:

Invalid responses

Empty payloads

Connection errors

Verify MongoDB insertion with:

bash
mongosh
use etl_db
db.cisa_kev.find().limit(3).pretty()
6. Project Structure
text
custom-python-etl-data-connector-captainsparrow73/
├── .env                 # Environment variables (not committed to Git)
├── .gitignore           # Ignore .env, venv, and cache files
├── requirements.txt     # Dependencies
├── etl_connector.py     # Main ETL script
└── README.md            # Project documentation
Setup and Run
1. Clone the repository:
bash
git clone https://github.com/Kyureeus-Edtech/custom-python-etl-data-connector-captainsparrow73.git
cd custom-python-etl-data-connector-captainsparrow73
2. Create and activate a virtual environment:
Windows PowerShell

bash
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
macOS/Linux

bash
python3 -m venv .venv
source .venv/bin/activate
3. Install dependencies:
bash
python -m pip install --upgrade pip
pip install -r requirements.txt
4. Run the ETL script:
bash
python etl_connector.py
Author
Name: Mohamed Imran Fareeth S
Roll No: 3122225001072 B

 Submission Checklist
 Chose API provider and understood documentation

 Stored configuration in .env and secured it in .gitignore

 Built complete ETL: Extract → Transform → Load

 Validated data in MongoDB

 Wrote descriptive README.md

 Included name + roll number in commit message

 Submitted Pull Request

Tech Stack
Python 3.x

requests

pymongo

python-dotenv

MongoDB (local or Atlas Cloud)

Notes
No authentication required for CISA KEV API.

Keys are sanitized for MongoDB compatibility.

Bulk inserts improve performance.