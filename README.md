# CISA Known Exploited Vulnerabilities ETL Connector

## Submitted by
- Name: Sundaresh Karthic Ganesan 
- Reg. Number: 3122225001143 
- College: SSN College of Engineering  
- Course: Software Architecture (Kyureeus EdTech)

## Overview

This ETL (Extract, Transform, Load) pipeline connects to the CISA Known Exploited Vulnerabilities (KEV) catalog API, processes the data, and loads it into a MongoDB collection. The connector is built using Python with secure coding practices and modular design.

## Data Source

- API Provider: CISA (Cybersecurity and Infrastructure Security Agency)
- Endpoint:  
  https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json
- Authentication: Not required (public API)

## ETL Pipeline Phases

### 1. Extract
- Fetches KEV vulnerability data using a GET request.
- Handles connection issues, request timeouts, and invalid responses.

### 2. Transform
- Enhances each vulnerability record with:
  - Processing timestamps
  - Record index
  - Catalog metadata
  - Parsed date fields (`dateAdded`, `dueDate`)

### 3. Load
- Connects to MongoDB using credentials stored in environment variables.
- Inserts data into the `cisa_vulnerabilities_raw` collection.
- Drops existing records for a clean load.
- Creates indexes for optimized queries.

## MongoDB Details

- Database: Defined by `DB_NAME` in the `.env` file (default: `security_intelligence`)
- Collection: `cisa_vulnerabilities_raw`
- Indexes:
  - `cveID` (unique)
  - `vendorProject`
  - `record_processed_at`

## Environment Variables

Create a `.env` file in the project directory with the following:
- MONGO_URI=mongodb+srv://<username>:<password>@<cluster-url>/<dbname>?retryWrites=true&w=majority
- DB_NAME=security_intelligence

## Testing and Validation

- Handles:
  - Timeout errors
  - Invalid responses
  - Empty payloads
- Validated MongoDB inserts and index creation

## Learnings

This project demonstrates how to:
- Design a full ETL pipeline in Python
- Handle real-world API data with robust error checking
- Store structured data into MongoDB with indexing
- Securely manage credentials and configurations

## References

- CISA KEV Catalog: https://www.cisa.gov/known-exploited-vulnerabilities-catalog  
- Requests Library: https://docs.python-requests.org/  
- PyMongo Documentation: https://pymongo.readthedocs.io/  
- Dotenv for Python: https://saurabh-kumar.com/python-dotenv/