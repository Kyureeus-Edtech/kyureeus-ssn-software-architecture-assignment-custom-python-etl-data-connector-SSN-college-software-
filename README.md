ETL Connector – ICANN(CZDS) to MongoDB
Overview
This project extracts data from the ICANN API, transforms it, and loads it into MongoDB.

Requirements
Python 3.9+

MongoDB (local or cloud)

pip install -r requirements.txt

Setup
Create a .env file:

MONGO_URI= MongoDB connection string (local or Atlas)
ICANN_EMAIL=Your email id which has account in ICANN
ICANN_PASSWORD= Password for your account

Install dependencies:

pip install -r requirements.txt


Run the ETL script:

python etl_connector.py


Verifying the Data
Open MongoDB Compass and connect to your database.
Check the czds_db collection for newly inserted records.