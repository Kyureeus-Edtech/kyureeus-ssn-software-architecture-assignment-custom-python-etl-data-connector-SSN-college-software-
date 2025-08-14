# SSN-college-software-architecture-Assignments-
Assignment repository for building custom Python ETL data connectors (Kyureeus EdTech, SSN CSE). Students: Submit your ETL scripts here. Make sure your commit message includes your name and roll number.
# Software Architecture Assignment: Custom Python ETL Data Connector

# ETL Connector for the CISA Known Exploited Vulnerabilities (KEV) Catalog

This repository contains a complete Python-based ETL (Extract, Transform, Load) pipeline designed for the **Software Architecture Assignment**. The script connects to the CISA KEV data feed, processes the vulnerability data, and loads it into a MongoDB database for analysis and storage.

**Student:** `Tharunithi TJ`
**Roll Number:** `3122225001151`
**Section:** `CSE-C`

---

## 📖 Project Overview

The goal of this project is to build a robust and secure data connector that automates the process of fetching critical cybersecurity intelligence. We use the **CISA Known Exploited Vulnerabilities (KEV) Catalog**, a public list of vulnerabilities that are known to be actively exploited in the wild.

The ETL pipeline performs three main functions:
1.  **Extract:** It pulls the latest KEV catalog directly from the CISA JSON feed.
2.  **Transform:** It refines the raw data by selecting the relevant vulnerability list and enriching each record with an ingestion timestamp for auditing purposes.
3.  **Load:** It securely connects to a MongoDB instance and loads the transformed data into a dedicated collection, ensuring the database always contains the most up-to-date information.

---

## ✨ Key Features

* **Secure Configuration:** All sensitive information, such as the MongoDB connection string, is managed outside the codebase using a `.env` file for enhanced security.
* **Robust Error Handling:** The script includes checks for network issues, HTTP errors, and database connection problems.
* **Data Freshness:** Before loading new data, the script clears the existing collection to prevent duplicates and ensure the database reflects the latest version of the CISA catalog.
* **Structured Logging:** The application provides clear, timestamped logs for every stage of the ETL process, making it easy to monitor and debug.
* **Dependency Management:** All required Python libraries are listed in a `requirements.txt` file for easy and repeatable setup.

---

## 🛠️ Technology Stack

* **Programming Language:** Python 3.9+
* **Core Libraries:**
    * `requests`: For making HTTP requests to the CISA API.
    * `pymongo`: The official Python driver for interacting with the MongoDB database.
    * `python-dotenv`: For managing environment variables from the `.env` file.
* **Database:** MongoDB
* **Version Control:** Git

---

## 📂 Project Structure

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

## ⚙️ Setup and Installation Guide

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

**Important:** The `.gitignore` file is already configured to prevent this file from being committed. **Never commit your `.env` file.**

Create the `.env` file and add the following content:
```
# .env file

# API Credentials (not needed for CISA KEV, but here for good practice)
API_KEY=""

# MongoDB Connection Details
# Replace with your MongoDB connection string if it's not running locally
MONGO_URI="mongodb://localhost:27017/"
DB_NAME="cybersecurity_data"
```

---

## 🚀 How to Run the ETL Script

Once the setup is complete, you can execute the ETL pipeline with a single command:

```bash
python etl_connector.py
```

The script will display its progress in the terminal, from extraction to loading.



---

## 🔄 ETL Process Explained

The `etl_connector.py` script is divided into three logical functions:

### 1. Extract
The `extract_data()` function sends an HTTP GET request to the CISA KEV JSON URL:
`https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json`
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

## 🗃️ MongoDB Output

The script stores the final, cleaned data in your MongoDB instance with the following details:

* **Database:** `cybersecurity_data`
* **Collection:** `cisa_kev_catalog_raw`

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