
# CIRCL Vulnerability ETL Pipeline (Python → MongoDB)

---

## **Project Overview**

This project implements an ETL (Extract, Transform, Load) pipeline that integrates with the **CIRCL (Computer Incident Response Center Luxembourg) Vulnerability Lookup API**.(https://vulnerability.circl.lu/documentation/api-v1.html), structures the results into clean, standardized JSON documents, and stores them into **MongoDB** for downstream security analytics and visualization.


It automates the collection, transformation, and storage of software vulnerability data (CVEs) into a MongoDB database for further analytics or dashboard integration.

**The workflow:**

1. Extracts vulnerability data such as recent vulnerabilities, trending vulnerabilities, most commented or sighted vulnerabilities, and vendor–product relationships from the CIRCL API.

2. Transforms the extracted data into a structured format by standardizing fields (CVE ID, description, impact metrics, timestamps, vendor-product tags).

3. Loads the structured data into MongoDB collections for querying, reporting, and integration with security monitoring tools.
---

## **API Endpoint Details**

**Base URL:**

```
https://vulnerability.circl.lu/api/
```

**Authentication:**
Some endpoints require authentication with an API key.
Include your key in the request header:

```
Authorization: Bearer <YOUR_API_KEY>
```

---

### **Commonly Used Endpoints**

| Endpoint                     | Description                                           | Example                        |
| ---------------------------- | ----------------------------------------------------- | ------------------------------ |
| `/cve/<cve_id>`              | Retrieve full details for a specific CVE              | `/cve/CVE-2024-4567`           |
| `/search/<vendor>/<product>` | Get vulnerabilities for a specific vendor/product     | `/search/microsoft/windows_10` |
| `/last`                      | Fetch the latest CVEs published in NVD/CIRCL          | `/last`                        |
| `/vendor`                    | List all vendors in the database                      | `/vendor`                      |
| `/vendor/<vendor>`           | List all products for a vendor                        | `/vendor/microsoft`            |
| `/cvss/<cve_id>`             | Retrieve the CVSS score for a CVE                     | `/cvss/CVE-2024-12345`         |
| `/browse`                    | Get a hierarchical list of all vendors and products   | `/browse`                      |
| `/recent`                    | Fetch recently updated vulnerabilities                | `/recent`                      |
| `/trending`                  | Fetch top trending vulnerabilities in the last 7 days | `/trending`                    |

---

## **Transformation Fields**

Each vulnerability document is stored in MongoDB with structured attributes:

| Field                 | Description                                               |
| --------------------- | --------------------------------------------------------- |
| `id`                  | The CVE identifier (e.g., CVE-2024-4567)                  |
| `summary`             | A brief description of the vulnerability                  |
| `published`           | Date the CVE was first published                          |
| `last_modified`       | Most recent update time                                   |
| `cvss`                | Numerical CVSS v3.1 base score                            |
| `cvss_vector`         | Vector string (e.g., AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H) |
| `cwe`                 | Common Weakness Enumeration ID                            |
| `references`          | Array of URLs referencing the CVE                         |
| `vendor`              | Vendor associated with the product                        |
| `product`             | Affected product name(s)                                  |
| `source`              | Origin of the data (e.g., NVD, CIRCL)                     |
| `ingestion_timestamp` | UTC time when the record was fetched                      |

---
## **How the Interaction Happens**

The components interact in a modular ETL flow:

1. **extract.py** connects to the CIRCL API and retrieves JSON data for endpoints like /vulnerability/recent or /browse/vendor.

2. **transform.py** processes this raw JSON data, extracting key fields (CVE ID, summary, CVSS score, vendor, references, published date) and ensuring consistent schema.

3. **load.py** connects to MongoDB and inserts the processed data into specific collections such as vulnerabilities_recent_raw, vendors_raw, or vulnerabilities_most_commented.

4. **main.py** orchestrates the pipeline — calling extract, transform, and load sequentially, while also printing progress logs and timestamps.
---

## **Key Steps in main.py**

Each execution of main.py performs the following:
| Step | Action                                                                       | Example Function                              |
| ---- | ---------------------------------------------------------------------------- | --------------------------------------------- |
| 1️⃣  | Extract all vendors                                                          | `get_vendors()`                               |
| 2️⃣  | Extract recent vulnerabilities                                               | `get_recent_vulnerabilities()`                |
| 3️⃣  | Extract last 20 vulnerabilities                                              | `get_last_vulnerabilities(20)`                |
| 4️⃣  | Extract most-commented vulnerabilities                                       | `get_stats_most_commented()`                  |
| 5️⃣  | Extract most-sighted vulnerabilities                                         | `get_stats_most_sighted()`                    |
| 6️⃣  | Search vulnerabilities for a specific vendor-product pair                    | `search_vulnerabilities("microsoft", "edge")` |
| 7️⃣  | If results are found, fetch associated comments and insert them into MongoDB | `get_comments()`                              |
| ✅    | Insert all processed data into MongoDB collections                           | `insert_to_mongo(collection_name, data)`      |
---
## **Setup Instructions**

### 1. **Clone the Repository**

### 2. **Create a `.env` File**

```
MONGO_URI=your_mongo_connection_uri_here
DB_NAME=your_database_name_here
CIRCL_USERNAME=your_circl_username_here
CIRCL_PASSWORD=your_circl_password_here
```

### 3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 4. **Run MongoDB**

Ensure MongoDB is running locally or connected remotely.

### 5. **Execute the ETL Script**

```bash
python main.py
```

---

## **Testing and Validation**

✅ Uses `raise_for_status()` for API error handling (e.g., 404, 403, 429)
✅ Skips insertion if the API returns an empty dataset
✅ Uses `upsert=True` to avoid duplicate CVE records
✅ Adds timestamped logs for each extraction batch
✅ Supports multi-endpoint collection in one run (trending, recent, specific vendor/product)

---

## **Example MongoDB Document**

```json
{
  "_id": "CVE-2024-4567",
  "summary": "Buffer overflow in Windows 10 kernel allows remote code execution.",
  "published": "2024-07-12T10:32:00Z",
  "last_modified": "2025-01-10T14:15:20Z",
  "cvss": 9.8,
  "cvss_vector": "AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
  "cwe": "CWE-120",
  "vendor": "microsoft",
  "product": "windows_10",
  "references": [
    "https://nvd.nist.gov/vuln/detail/CVE-2024-4567",
    "https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2024-4567"
  ],
  "source": "CIRCL Vulnerability DB",
  "ingestion_timestamp": "2025-10-18T09:35:21Z"
}
```

---

## **Project Structure**

```
project-folder/
├── main.py                  # Entry point that calls extract, transform, and load functions
├── extract.py               # Handles API calls (fetches CVE, trending, vendor data)
├── transform.py             # Cleans and normalizes vulnerability records
├── load.py                  # Inserts/updates documents in MongoDB
├── utils.py                 # Helper functions (auth, logging, timestamp)
├── .env                     # Stores API key and DB config (not in git)
├── requirements.txt         # Dependency list
├── README.md                # This documentation
└── .gitignore               # Ensures .env and cache files are excluded
```

---

## **Summary**

This ETL pipeline connects securely to the **CIRCL Vulnerability Intelligence API**, retrieves multi-endpoint vulnerability data, and stores it in **MongoDB** after structuring and deduplication.

It is designed for **academic clarity and professional scalability**, supporting multiple use cases such as:

* Threat intelligence dashboards
* CVE analytics
* Correlation with local asset data
* Security research and reporting