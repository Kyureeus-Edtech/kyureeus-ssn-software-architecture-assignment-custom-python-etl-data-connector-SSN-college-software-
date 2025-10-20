
# Software Architecture Assignment: Custom Python ETL Data Connector

## NVD (National Vulnerability Database) ETL Connector (https://nvd.nist.gov/)
<br>Endpoint: https://services.nvd.nist.gov/rest/json
## 📋 Assignment Overview
This project is a Python-based ETL (Extract, Transform, Load) connector. It is designed to fetch vulnerability and product data from the National Vulnerability Database (NVD) 2.0 API, transform it for optimal storage, and load it into a MongoDB database.

This script is built to be flexible and secure, using command-line arguments for custom queries and a .env file for API key management.

**Goal:**  
Develop a Python script to connect with an API provider, extract data, transform it for compatibility, and load it into a MongoDB collection. Follow secure coding and project structure practices as outlined below.

## Features
<ul>
<li>Extracts from 3 different NVD API endpoints.</li>

<li>Transforms data by converting date strings to native MongoDB BSON date objects and setting unique _id fields.</li>

<li>Loads data into MongoDB using an idempotent "upsert" operation (replace_one) to prevent duplicates and allow for easy updates.</li>

<li>Flexible Runtime: Uses argparse to accept command-line arguments for dynamic queries (e.g., number of days, search keywords) without hardcoding.</li>

<li>Secure: Manages the NVD API key securely using a .env file.</li>

<li>Robust: Includes pagination handling to fetch all results from large queries.</li>
</ul>
---

## API Endpoints Used
This connector fetches data from the following three NVD 2.0 endpoints:
<ol>
<li>/cves/2.0: To get Common Vulnerabilities and Exposures (CVE) details.</li>

<li>/cpes/2.0: To get Common Platform Enumeration (CPE) product details.</li>

<li>/cpematch/2.0: To get CPE matching criteria for specific CVEs.</li>
</ol>
---

## ✅ Submission Checklist

- [✅ ] Choose a data provider (API) and understand its documentation
- [✅ ] Secure all API credentials using a `.env` file
- [✅] Build a complete ETL pipeline: Extract → Transform → Load (into MongoDB)
- [✅] Test and validate your pipeline (handle errors, invalid data, rate limits, etc.)
- [✅] Follow the provided Git project structure
- [✅] Write a clear and descriptive `README.md` in your folder with API details and usage instructions
- [✅] **Include your name and roll number in your commit messages**
- [✅] Push your code to your branch and submit a Pull Request

---

## 📦 Project Structure

/3122225001018_CSE_A_ETL2/
├── a2etlConnector.py
├── .env
├── requirements.txt
├── README.md
└── (any additional scripts or configs)


- **`.env`**: Store sensitive credentials; do **not** commit this file.
- **`etl_connector.py`**: Your main ETL script.
- **`requirements.txt`**: List all Python dependencies.
- **`README.md`**: Instructions for your connector.

---

## 🗃️ MongoDB Structure

- Database: `nvd_db`
- Collections: `matches, products and vulnerabilities`

---


