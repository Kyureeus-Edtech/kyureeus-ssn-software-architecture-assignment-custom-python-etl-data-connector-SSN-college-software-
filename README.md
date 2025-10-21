
# GreyNoise Community API ETL Connector

This repository contains a Python ETL (Extract, Transform, Load) pipeline developed to ingest basic IP intelligence from the **GreyNoise Community API** and store it securely into a **MongoDB** collection.

The project adheres to the secure coding, project structure, and validation guidelines provided for the assignment.

## 📌 Submission & Compliance Checklist

| Requirement | Status | Notes |
| :--- | :--- | :--- |
| Secure Credentials (`.env`) | ✅ | MongoDB credentials stored securely. API key usage **omitted** as permitted by Community API, simplifying local testing. |
| Complete ETL Pipeline | ✅ | Functions for `extract_data`, `transform_data`, and `load_data` are implemented. |
| MongoDB Strategy | ✅ | Uses collection naming: `greynoise_community_raw`. Includes `ingestion_timestamp` for audit. |
| Error Handling & Validation | ✅ | Pipeline successfully handles **Connectivity Errors** (RequestException) and **API Errors** (`404 Not Found`, `429 Rate Limit`). **4 records successfully loaded** in final test run (including audit records). |
| Git Structure | ✅ | Uses `.gitignore` to exclude `.env` and Python build files. |
| Descriptive README | ✅ | This document fulfills the requirement. |

-----

## ⚙️ Connector Details

| Feature | Value |
| :--- | :--- |
| **API Provider** | GreyNoise Intelligence |
| **Target API** | Community API (v3) |
| **Base URL** | `https://api.greynoise.io/v3/community/` |
| **Authentication** | **Unauthenticated** (Relies on public access with minimal rate limits). |
| **Data Source** | Hardcoded list of test IP addresses. |
| **MongoDB Collection** | `greynoise_community_raw` |

## 🚀 Usage Instructions

### 1\. Prerequisites

  * **Python 3.8+**
  * The required libraries must be installed (from `requirements.txt`).
  * A running MongoDB instance (Atlas or local) accessible via the URI.

### 2\. Setup and Execution

1.  **Clone the Repository** and ensure the file structure is correct.

2.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Credentials:** Ensure your **`.env`** file contains a valid `MONGO_URI`, `MONGO_DB_NAME`, and `MONGO_COLLECTION_NAME`.

    *Example `.env` structure:*

    ```env
    MONGO_URI="mongodb://localhost:27017"
    MONGO_DB_NAME="etl_db"
    MONGO_COLLECTION_NAME="greynoise_community_raw"
    ```

4.  **Run the ETL Script:**

    ```bash
    python greynoise_connector.py
    ```

-----

## 📊 Test Validation Results

The final test run demonstrated successful handling of both valid and non-existent IPs:

| IP Address | API Response Status | Transformation | MongoDB Result |
| :--- | :--- | :--- | :--- |
| **8.8.8.8** | Successful (HTTP 200) | Full data ingested (e.g., `riot: true`). | **1 successful data record.** |
| **1.2.3.4** | Not Found (HTTP 404) | Transformed into an Audit/Error record. | **1 audit record.** |
| **192.0.2.1** | Not Found (HTTP 404) | Transformed into an Audit/Error record. | **1 audit record.** |
| **195.72.230.190** | Not Found (HTTP 404) | Transformed into an Audit/Error record. | **1 audit record.** |
| **Total:** | | | **4 records successfully loaded.** |

### Example Audit Record (in MongoDB):

For IPs that returned 404, the MongoDB document structure confirms the error handling:

```json
{
  "_id": { "$oid": "..." },
  "ip": "1.2.3.4",
  "ingestion_timestamp": { "$date": "2025-10-21T..." },
  "status": "Extraction Failed",
  "error_details": "IP Not Found",
  "status_code": 404
}
```

## 🙋 Student Information

Please ensure your final commit message includes your name and roll number.

  * **Student Name:** Akshatha Anbalagan
  * **Roll Number:** akshatha11anbalagan
  * **Commit Example:** `feat(greynoise): Final ETL script with MongoDB validation. Student: Akshatha Anbalagan, Roll: akshatha11anbalagan`