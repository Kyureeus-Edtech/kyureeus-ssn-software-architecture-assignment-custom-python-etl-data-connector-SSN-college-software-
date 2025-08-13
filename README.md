AlienVault OTX ETL Pipeline
Overview
---------

This script connects to the AlienVault Open Threat Exchange (OTX) API.
It fetches subscribed threat pulses using your OTX API key.
Transforms the pulse data into a structured format.
Loads or updates the records in a MongoDB collection.
Reads all settings from a .env file for security.
Limit the total number of pulses fetched (default 50).
_____________________________________________________

Requirements
----
Python 3.8 or later
MongoDB installed locally or accessible remotely
An AlienVault OTX API key
pip to install dependencies - requests, python-dotenv, pymongo 

_____________________________________________________

Environment Variables (.env)
-----

API_KEY – Required to authenticate with the AlienVault OTX API.
MONGO_URI – The MongoDB connection string.
DB_NAME – The name of the MongoDB database where the pulses will be stored.
COLLECTION_NAME – The name of the MongoDB collection where the pulses will be inserted or updated.
MAX_PULSES – The maximum number of pulses the script should fetch and process in a single run.

The script retrieves pulses in pages from the /api/v1/pulses/subscribed endpoint.
Once the total count of fetched pulses reaches this value, the script stops processing further pages, even if more pulses are available.
This limit is useful for testing or partial data ingestion to avoid pulling the entire dataset.

Example: Setting MAX_PULSES=50 will stop execution after exactly 50 pulses have been processed.

_____________________________________________________