MalwareBazaar ETL Pipeline
Overview
___________________________________________________________
This script connects to the MalwareBazaar (Abuse.ch) API.
It fetches recent malware metadata and tag-specific samples using your MalwareBazaar API key.
Transforms the raw JSON into a clean, structured format.
Loads or updates the records in a MongoDB collection for analysis.
Reads all configuration values securely from a .env file.
Uses safe metadata-only endpoints (no malware binaries).
__________________________________________________________
Requirements

Python 3.8 or later

MongoDB installed locally or accessible remotely

A MalwareBazaar API key (required for authentication)

pip to install dependencies: requests, pymongo, python-dotenv
_____________________________________________________________
Environment Variables (.env)

MB_AUTH_KEY – Required to authenticate with the MalwareBazaar API.
MONGO_URI – The MongoDB connection string.
MB_DB – The MongoDB database name where metadata will be stored.
(Default: malwarebazaar)
_____________________________________________________________
ETL Process

The script queries multiple metadata-only API endpoints from
https://mb-api.abuse.ch/api/v1/, including:

get_recent – latest malware submissions

get_taginfo – samples by tag (e.g., TrickBot, Emotet, Ransomware)

get_yarainfo – samples matching a YARA rule

get_info – detailed lookup for a specific hash

get_certificate – metadata about file signing certificates

Each response is normalized and upserted into MongoDB collections (samples and certificates).
Existing entries are updated rather than duplicated.