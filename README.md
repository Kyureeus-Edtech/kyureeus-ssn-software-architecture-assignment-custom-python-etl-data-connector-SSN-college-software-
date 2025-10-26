Abuse.ch ETL Data Connector

Student Name: Rithick R Rahul
Roll No: 3122225001107
Course: Software Architecture (Kyureeus EdTech, SSN CSE)

Project Overview

This project implements an ETL (Extract, Transform, Load) pipeline that connects to abuse.ch’s threat intelligence APIs — specifically URLhaus and MalwareBazaar — to retrieve, process, and store cyber threat intelligence data into a MongoDB database.

The script automatically:

Extracts recent threat data from two APIs.

Transforms it into a consistent schema (adding tags, timestamps, and classifications).

Loads the results into MongoDB collections with upsert operations to prevent duplicates.

Features

Connects to URLhaus and MalwareBazaar APIs.

Transforms and standardizes extracted data.

Stores results in MongoDB collections:

urlhaus_iocs

malwarebazaar_iocs

Supports upsert operations (avoids duplicate entries).

Logs all ETL steps for transparency and debugging.

Supports optional API key authentication via environment variables.

Tech Stack
Component	Description
Python 3.10+	Core programming language
Requests	API communication
PyMongo	MongoDB driver for Python
python-dotenv	Environment variable management
MongoDB Community Edition	Database for storing threat intelligence data
Requirements

List of dependencies in requirements.txt:

requests>=2.31.0
pymongo>=4.5.0
python-dotenv>=1.0.0

Output Summary

After successful execution:

Transformed threat data will be stored in MongoDB collections:

urlhaus_iocs

malwarebazaar_iocs

A console summary will display total records and a sample IOC from each source.

Logs will indicate successful connections, API extractions, transformations, and MongoDB insertions.

Logging

All operations are logged in a structured format:

2025-10-27 00:15:10 - INFO - Starting abuse.ch ETL Pipeline
2025-10-27 00:15:11 - INFO - Extracting recent URLs from URLhaus...
2025-10-27 00:15:14 - INFO - Upserted 100 records into 'urlhaus_iocs'

Troubleshooting
Issue	Possible Cause	Solution
Could not connect to MongoDB	MongoDB not running	Start MongoDB service using brew services start mongodb-community
Failed to fetch data	API endpoint unreachable or rate-limited	Check internet connection or use API key
OperationFailure in MongoDB	Invalid URI or insufficient permissions	Verify MONGO_URI in .env
Example MongoDB Document

Collection: urlhaus_iocs

{
  "_id": "1234567",
  "source": "URLhaus",
  "ioc_type": "url",
  "ioc_value": "http://malicious-site.com",
  "threat_type": "malware_download",
  "tags": ["exe", "trojan"],
  "threat_level": "high",
  "date_added": "2025-10-26 10:30:00",
  "url_status": "online",
  "ingested_at": "2025-10-27T00:30:00Z"
}

License

This project is developed as part of Assignment 2 for 3122225001107 (Rithick R Rahul).
For academic and educational purposes only.

Summary

This ETL connector efficiently integrates open threat intelligence data into a MongoDB-based storage pipeline. It demonstrates key ETL concepts—data extraction, transformation, and database integration—relevant to cybersecurity and data engineering domains.