# Custom Python ETL Data Connectors — Software Architecture Assignment

**Student:** Micheal Berdinanth M  
**Roll No:** 3122225001071  
**Class:** CSE-B  

---

## Project Overview
This project is part of the **Software Architecture** course assignment, where I implemented **two custom ETL (Extract, Transform, Load) connectors** in Python.  
The goal was to connect to public data sources, fetch data, transform it into a required structure, and load it securely into a MongoDB Atlas database while following secure coding and best practices.

---

## Data Sources Used

### 1. CISA KEV (Known Exploited Vulnerabilities)
- **URL:** [CISA KEV JSON Feed](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json)  
- **Format:** JSON  
- **Description:** List of vulnerabilities exploited in the wild, with CVE IDs, vendors, products, and due dates.

### 2. Spamhaus DROP (Don't Route Or Peer)
- **URL:** [Spamhaus DROP TXT Feed](https://www.spamhaus.org/drop/drop.txt)  
- **Format:** TXT  
- **Description:** Malicious IP address ranges with ASN and provider information.

---

## How I Built It

### 1. Environment Setup
- Created a Python virtual environment and installed dependencies:
  ```bash
  pip install requests python-dotenv pymongo urllib3
  ```
- Added a `.gitignore` file to prevent committing sensitive files like `.env`.

### 2. Secure API and DB Credentials
- Created a `.env` file to store MongoDB connection URI and configuration variables:
  ```env
  MONGO_URI=mongodb+srv://<username>:<password>@<cluster-url>/?retryWrites=true&w=majority
  MONGO_DB=ssn_arch
  PROVIDER=cisa_kev
  CONNECTOR_NAME=cisa_kev
  DRY_RUN=false
  ```
- Used `python-dotenv` to securely load environment variables in the script.

### 3. ETL Pipeline Design
- **Extract:**
  - **CISA KEV:** Made a GET request to the JSON feed.
  - **Spamhaus DROP:** Fetched the TXT list and parsed lines into structured records.
- **Transform:**
  - Normalized the data into a consistent dictionary format.
  - Added `source_id` for unique identification.
  - Appended `ingested_at` timestamps.
  - Preserved the full original record in `_raw` for audits.
- **Load:**
  - Connected to MongoDB Atlas using `pymongo`.
  - Created a **unique index** on `source_id` to avoid duplicates.
  - Performed **bulk upserts** for efficient inserts/updates.

### 4. Insights & Validation
After loading, the script prints:
- Total records fetched and inserted/updated.
- Sample documents (excluding `_raw`).
- **CISA KEV:** Top vendors by vulnerability count, recent additions, common due dates.
- **Spamhaus DROP:** Total malicious prefixes, top ASNs, and example prefixes.

---

## Project Structure
```
etl_connector.py
.env                  # not committed
requirements.txt
.gitignore
README.md
```

---

## How to Run

### Install Requirements
```bash
pip install -r requirements.txt
```

### Run for CISA KEV
```bash
# In .env
PROVIDER=cisa_kev
CONNECTOR_NAME=cisa_kev

python etl_connector.py
```

### Run for Spamhaus DROP
```bash
# In .env
PROVIDER=spamhaus_drop
CONNECTOR_NAME=spamhaus_drop

python etl_connector.py
```


---

