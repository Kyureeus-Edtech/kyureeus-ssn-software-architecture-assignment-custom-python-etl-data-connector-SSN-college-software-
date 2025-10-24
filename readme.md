@@ -1,135 +1,102 @@
# SSN-college-software-architecture-Assignments-
Assignment repository for building custom Python ETL data connectors (Kyureeus EdTech, SSN CSE). Students: Submit your ETL scripts here. Make sure your commit message includes your name and roll number.
# Software Architecture Assignment: Custom Python ETL Data Connector
# AbuseCH ETL Connector

Welcome to the official repository for submitting your Software Architecture assignment on building custom data connectors (ETL pipelines) in Python. This assignment is part of the Kyureeus EdTech program for SSN CSE students.
Python ETL pipeline to fetch threat intelligence feeds from URLHaus and FeodoTracker and store them into MongoDB.  
Developed by *Srivathsan Sundarrajan* (Roll No: XXXX) for SSN CSE Software Architecture Assignment.

---
Guideline: Building and Managing Custom Data Connectors (ETL Pipeline) in Python

1. Setting Up the Connector Environment
a. Choose Your API Provider: Identify a data provider and understand its Base URL, Endpoints, and Authentication.
b. Understand the API Documentation: Focus on headers, query params, pagination, rate limits, and response structure.
## 📌 Overview

This project demonstrates building custom Python ETL connectors for security-related data.  
The ETL pipeline extracts data from public threat feeds, transforms it for MongoDB compatibility, and loads it into separate collections with ingestion timestamps.

2. Secure API Authentication Using Environment Variables
a. Create a .env File Locally: Store API keys and secrets as KEY=VALUE pairs.
b. Load Environment Variables in Code: Use libraries like dotenv to securely load environment variables.


3. Design the ETL Pipeline
Extract: Connect to the API, pass tokens/headers, and collect JSON data.
Transform: Clean or reformat the data for MongoDB compatibility.
Load: Store the transformed data into a MongoDB collection.


4. MongoDB Collection Strategy
Use one collection per connector, e.g., connector_name_raw.
Store ingestion timestamps to support audits or updates.


5. Iterative Testing & Validation
Test for invalid responses, empty payloads, rate limits, and connectivity errors.
Ensure consistent insertion into MongoDB.

---

6. Git and Project Structure Guidelines
a. Use a Central Git Repository: Clone the shared repo and create a new branch for your connector.
b. Ignore Secrets: Add .env to .gitignore before the first commit.
c. Push and Document: Write README.md with endpoint details, API usage, and example output.
## 🛠 Feeds / Endpoints Used

| Connector        | Feed URL                                               | Notes                         |
|-----------------|-------------------------------------------------------|-------------------------------|
| recent_urls    | https://urlhaus.abuse.ch/downloads/csv_recent/       | Latest malicious URLs         |
| online_urls    | https://urlhaus.abuse.ch/downloads/csv_online/       | Currently active URLs         |
| feodotracker   | https://feodotracker.abuse.ch/downloads/ipblocklist.csv | Malicious IP addresses        |

Final Checklist for Students
Understand API documentation
Secure credentials in .env
Build complete ETL script
Validate MongoDB inserts
Push code to your branch
Include descriptive README
Submit Pull Request
> These feeds are public and *do not require authentication*.
## 📋 Assignment Overview
---

*Goal:*  
Develop a Python script to connect with an API provider, extract data, transform it for compatibility, and load it into a MongoDB collection. Follow secure coding and project structure practices as outlined below.
## ⚙ ETL Pipeline Design

---
*1. Extract*  
- Fetch CSV feeds from URLHaus and FeodoTracker using requests.  

## ✅ Submission Checklist
*2. Transform*  
- Clean column names  
- Remove duplicates  
- Add _ingested_at timestamp for audit purposes  

- [ ] Choose a data provider (API) and understand its documentation
- [ ] Secure all API credentials using a .env file
- [ ] Build a complete ETL pipeline: Extract → Transform → Load (into MongoDB)
- [ ] Test and validate your pipeline (handle errors, invalid data, rate limits, etc.)
- [ ] Follow the provided Git project structure
- [ ] Write a clear and descriptive README.md in your folder with API details and usage instructions
- [ ] *Include your name and roll number in your commit messages*
- [ ] Push your code to your branch and submit a Pull Request
*3. Load*  
- Insert data into MongoDB collections:
  - recent_urls_raw  
  - online_urls_raw  
  - feodotracker_raw  

---

## 📦 Project Structure
## 📂 Project Structure

/your-branch-name/
├── etl_connector.py
├── .env
├── requirements.txt
├── README.md
└── (any additional scripts or configs)
/abuseCH_etl/
├── etl_connector.py # Main ETL script
├── requirements.txt # Python dependencies
├── README.md # This file
├── .gitignore # Ignore secrets and cache files
└── .env # MongoDB credentials (not committed)

🧪 Testing & Validation
-----------------------
Handles connectivity issues and retries 3 times on failure

- **.env*: Store sensitive credentials; do **not* commit this file.
- **etl_connector.py**: Your main ETL script.
- **requirements.txt**: List all Python dependencies.
- **README.md**: Instructions for your connector.
Checks for empty feeds before inserting

---
Logs number of records fetched and inserted into MongoDB

## 🛡 Secure Authentication
_ingested_at timestamp ensures traceability

- Store all API keys/secrets in a local .env file.
- Load credentials using the dotenv Python library.
- Add .env to .gitignore before committing.
💻 Dependencies
--------------
pandas

---
requests

## 🗃 MongoDB Guidelines
pymongo

- Use one MongoDB collection per connector (e.g., connectorname_raw).
- Store ingestion timestamps for audit and update purposes.
python-dotenv

---
Install all dependencies:

## 🧪 Testing & Validation
pip install -r requirements.txt

- Check for invalid responses, empty payloads, rate limits, and connectivity issues.
- Ensure data is correctly inserted into MongoDB.
🚀 How to Run
---------------
Clone the repository and switch to your branch

---
Create .env with MongoDB credentials

## 📝 Git & Submission Guidelines
Install dependencies

1. *Clone the repository* and create your own branch.
2. *Add your code and documentation* in your folder/branch.
3. *Do not commit* your .env or secrets.
4. *Write clear commit messages* (include your name and roll number).
5. *Submit a Pull Request* when done.
Run ETL:

---

## 💡 Additional Resources
python etl_connector.py

- [python-dotenv Documentation](https://saurabh-kumar.com/python-dotenv/)
- [MongoDB Python Driver (PyMongo)](https://pymongo.readthedocs.io/en/stable/)
- [API Documentation Example](https://restfulapi.net/)
📢 Notes
------------
Currently uses 3 feeds: URLHaus recent, URLHaus online, FeodoTracker IPs

---
Designed to be easily extended with additional connectors

## 📢 Need Help?
Logs everything in console for debugging

- Post your queries in the [KYUREEUS/SSN College - WhatsApp group](#) .
- Discuss issues, share progress, and help each other.

---

Happy coding! 🚀
Navaneetha Krishanan
Roll No: 3122225001306
SSN College of Engineering