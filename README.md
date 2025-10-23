ETL Connector – DShield to MongoDB
Overview
This project extracts data from the DShield API, transforms it, and loads it into MongoDB.

Requirements
Python 3.9+

MongoDB (local or cloud)

pip install -r requirements.txt

Setup
Create a .env file:

MONGO_URI= MongoDB connection string (local or Atlas)
DSHIELD_URL=API endpoint for DShield top IPs (JSON)
DB_NAME=Database Name

Install dependencies:

pip install -r requirements.txt


Run the ETL script:

python etl_connector.py


Verifying the Data
Open MongoDB Compass and connect to your database.
Check the dshield_data collection for newly inserted records.