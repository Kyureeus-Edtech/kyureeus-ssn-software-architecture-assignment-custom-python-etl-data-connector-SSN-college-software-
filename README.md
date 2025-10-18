# SSN-college-software-architecture-Assignments-
# Software Architecture Assignment: Custom Python ETL Data Connector

# ETL Connector for the CISA Known Exploited Vulnerabilities (KEV) Catalog && FreeGeoIP.app

This repository contains a complete Python-based ETL (Extract, Transform, Load) pipeline designed for the **Software Architecture Assignment**. The script connects to the CISA KEV data feed, processes the vulnerability data, and loads it into a MongoDB database for analysis and storage.

**Student:** `Tharunithi TJ`
**Roll Number:** `3122225001151`
**Section:** `CSE-C`
**Assignment:** `2`

---

## 1. Project Overview

The goal of this project is to build a robust and secure data connector that automates the process of fetching critical cybersecurity intelligence and geographic information. We use the **CISA Known Exploited Vulnerabilities (KEV) Catalog** and **FreeGeoIP.app**.

The ETL pipeline performs three main functions:
1.  **Extract:** It pulls the latest KEV catalog directly from the CISA JSON feed.
2.  **Transform:** It refines the raw data by selecting the relevant vulnerability list and enriching each record with an ingestion timestamp for auditing purposes.
3.  **Load:** It securely connects to a MongoDB instance and loads the transformed data into a dedicated collection, ensuring the database always contains the most up-to-date information.

---

## 2. Features

- **Multi-Source & Multi-Format:** Ingests data from various endpoints across different APIs, handling both JSON and XML formats automatically.  
- **Modular Configuration:** Endpoints are defined in a central list, making it simple to add, remove, or modify data sources without changing the core logic.  
- **Intelligent Data Handling:** Automatically processes both lists of items (like CISA feeds) and single JSON objects (like the FreeGeoIP API).  
- **Robust Error Handling:** Implements specific error catching for HTTP errors, connection issues, and timeouts during the extraction phase.  
- **Efficient Database Loading:** Uses MongoDB's `bulk_write` with an upsert strategy (`ReplaceOne`) to efficiently insert new records and update existing ones based on a unique key.  
- **Secure Credential Management:** Uses a `.env` file to securely manage the MongoDB connection string and other secrets, keeping them out of the main codebase.  

---

## 3. Data Sources

The pipeline is currently configured to pull data from two primary sources: **CISA.gov** and **FreeGeoIP.app**.

| API Source     | Endpoint              | Data Format | Target MongoDB Collection      |
|----------------|----------------------|--------------|--------------------------------|
| CISA.gov       | KEV Catalog          | JSON         | `cisa_kev_catalog_raw`         |
| CISA.gov       | Alerts & Advisories  | XML          | `cisa_alerts_raw`              |
| CISA.gov       | ICS Advisories       | XML          | `cisa_ics_advisories_raw`      |
| FreeGeoIP.app  | GeoIP for Google DNS | JSON         | `geoip_lookups_raw_endpoint_1` |
| FreeGeoIP.app  | GeoIP for Cloudflare DNS | JSON     | `geoip_lookups_raw_endpoint_2` |
| FreeGeoIP.app  | GeoIP for Self (runner IP) | JSON   | `geoip_lookups_raw_endpoint_3` |

---

## Technology Stack

* **Programming Language:** Python 3.9+
* **Core Libraries:**
    * `requests`: For making HTTP requests to the CISA API and FreeGeoIP.app API.
    * `pymongo`: The official Python driver for interacting with the MongoDB database.
    * `python-dotenv`: For managing environment variables from the `.env` file.
* **Database:** MongoDB
* **Version Control:** Git

---

## Project Structure

The project is organized with a clear and scalable structure, separating code, configuration, and documentation.

```
/your-branch-name/
│
├── .env                  # Stores all secrets and environment variables (NOT committed to Git)
├── .gitignore            # Specifies files and directories to be ignored by Git
├── etl_connector.py      # The main Python script containing the ETL logic
├── requirements.txt      # A list of all Python dependencies for the project
└── README.md             # This detailed documentation file
```

---

## Setup and Installation Guide

Follow these steps to set up and run the project on your local machine.

### 1. Prerequisites
* Python 3.9 or newer
* Git installed on your system
* A running instance of MongoDB (local or cloud-based)

### 2. Clone the Repository
Open your terminal and clone the repository, then navigate into your project directory.
```bash
# Clone the repository (use your specific repo URL)
git clone <your-repository-url>

# Navigate into your branch folder
cd <your-branch-name>/
```

### 3. Set Up a Virtual Environment
It is a best practice to use a virtual environment to manage project-specific dependencies.

```bash
# Create a virtual environment named 'venv'
python -m venv venv

# Activate the environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
.\venv\Scripts\activate
```

### 4. Install Dependencies
Install all the necessary Python libraries using the `requirements.txt` file.
```bash
pip install -r requirements.txt
```

### 5. Configure Your Environment
Create a `.env` file in the root of your project directory by copying the example below. This file will hold your MongoDB connection string.

---

## How to Run the ETL Script

Once the setup is complete, you can execute the ETL pipeline with a single command:

```bash
python etl_connector.py
```

The script will display its progress in the terminal, from extraction to loading.

---

## ETL Process Explained

The `etl_connector.py` script is divided into three logical functions:

### 1. Extract
The `extract_data()` function sends an HTTP GET request to the CISA KEV JSON URL and FreeGeoIP.app.
It includes error handling to catch network failures or bad responses (e.g., 404 Not Found, 500 Server Error) and returns the full JSON payload.

### 2. Transform
The `transform_data()` function receives the raw JSON data. Its main responsibilities are:
* Accessing the primary list of vulnerabilities, which is nested under the `"vulnerabilities"` key in the raw data.
* Iterating through each vulnerability record and adding a new field: `ingestion_timestamp`. This timestamp uses `datetime.utcnow()` to record when the data was processed, which is crucial for auditing.

### 3. Load
The `load_data()` function handles all database interactions:
* It establishes a connection to the MongoDB server using the `MONGO_URI` from your `.env` file.
* To ensure data freshness, it first runs `collection.delete_many({})`, which clears all existing documents from the target collection.
* It then uses `collection.insert_many()` to perform a bulk insert of all the transformed records. This is highly efficient for loading a large number of documents.
* Finally, it closes the database connection securely.

---

## MongoDB Output

The script stores the final, cleaned data in your MongoDB instance with the following details:

* **Database:** `security_intelligence_and_free_geoIP_app`
* **Collection:** `cisa_kev_catalog_raw`, `cisa_kev_catalog_raw`, `cisa_alerts_raw`, `cisa_ics_advisories_raw`, `geoip_lookups_raw_endpoint_1`,`geoip_lookups_raw_endpoint_2`,`geoip_lookups_raw_endpoint_3`

Each document in the collection represents a single known exploited vulnerability and conforms to the structure below.

### Example Document in MongoDB:
```json
{
  "_id": ObjectId("67aed3f4e1a3b8c7e2f4b9d0"),
  "cveID": "CVE-2023-34048",
  "vendorProject": "VMware",
  "product": "vCenter Server",
  "vulnerabilityName": "VMware vCenter Server Out-of-Bounds Write Vulnerability",
  "dateAdded": "2023-10-26",
  "shortDescription": "VMware vCenter Server contains an out-of-bounds write vulnerability in the implementation of the DCERPC protocol.",
  "requiredAction": "Apply updates per vendor instructions.",
  "dueDate": "2023-11-16",
  "notes": "[https://www.vmware.com/security/advisories/VMSA-2023-0023.html](https://www.vmware.com/security/advisories/VMSA-2023-0023.html)",
  "ingestion_timestamp": "2025-08-14T16:30:00.123456Z"
}
```