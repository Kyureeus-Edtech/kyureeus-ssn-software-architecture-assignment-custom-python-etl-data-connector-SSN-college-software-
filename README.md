## ETL Connector for MongoDB

## Overview
This project implements an ETL (Extract, Transform, Load) pipeline in Python that reads data from an existing MongoDB collection, processes it by adding metadata, and loads it into a different target collection within the same database.
It is designed for scenarios where you already have a populated source collection and want to transform and store a modified version of the data without fetching from an external source.

## Features
•	Connects to MongoDB using credentials stored in a .env file
•	Extracts documents from a source collection
•	Transforms documents by adding a processed_at timestamp
•	Loads the transformed documents into a target collection in the same database
•	Easily configurable via environment variables
•	Minimal, reusable structure for other ETL workflows

## Requirements
Before running the ETL pipeline, ensure you have the following installed:
pymongo
python-dotenv

## Directory Structure
project/
│
├── etl_connector.py       # Main ETL script
├── requirements.txt       # Dependencies
├── .env                   	  # Environment variables
└── README.md           # Documentation

## Environment Variables
Create a .env file in the root directory with the following keys:
MONGO_URI=mongodb://localhost:27017
MONGO_DB
SOURCE_COLLECTION
TARGET_COLLECTION

## Descriptions of Environment Variables
•	MONGO_URI: MongoDB connection URI
•	MONGO_DB: Name of the database
•	SOURCE_COLLECTION: Name of the source collection to read from
•	TARGET_COLLECTION: Name of the target collection to write into

## Working
1.	Extract – Reads all documents from the source collection.
2.	Transform – Adds a processed_at field containing the current UTC timestamp to each document.
3.	Load – Inserts the transformed documents into the target collection in the same database.

## Running the ETL Pipeline
To run:
python etl_connector.py
Expected output example:
Inserted 38242 documents into exploitdb.exploits_target

## Troubleshooting
•	No data to load: Check that your source collection contains documents.
•	MongoDB connection errors: Confirm that MONGO_URI is correct and MongoDB is running.
•	Module Recognition Failure: Ensure that all required modules have been installed

## License
This project is licensed under the MIT License.


