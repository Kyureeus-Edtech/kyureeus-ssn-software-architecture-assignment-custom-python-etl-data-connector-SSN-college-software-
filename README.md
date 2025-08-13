## Name: Ram Prasath P
## Register Number: 3122 22 5001 103

# Custom ETL Data Connector: CISA Known Exploited Vulnerabilities (KEV)

This project contains a Python ETL (Extract, Transform, Load) script to fetch data from the CISA Known Exploited Vulnerabilities (KEV) catalog and load it into a MongoDB database.

The script enriches the raw data by converting date strings to datetime objects, calculating a remediation timeframe, and adding audit fields. This was created as part of the Software Architecture assignment for SSN College of Engineering.

---

## 📋 Connector Details

- **Data Source**: CISA KEV Catalog
- **Endpoint Used**: `https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json`
- **Data Format**: JSON
- **Authentication**: None required

---

## ⚙️ How to Run

1.  **Clone the Repository**:
    ```sh
    git clone <your-repo-url>
    cd your-branch-name
    ```

2.  **Install Dependencies**:
    Make sure you have Python and Pip installed.
    ```sh
    pip install -r requirements.txt
    ```

3.  **Set Up Environment Variables**:
    Create a `.env` file and add your MongoDB connection string to it:
    ```env
    MONGO_URI="your_mongodb_connection_string"
    ```

4.  **Execute the Script**:
    ```sh
    python etl_connector.py
    ```

---

## 📦 Database Schema

The script loads data into the `cisa_kev_raw` collection. Each document is enriched with new and converted fields to support advanced querying and analysis.

**Example Output Record:**
```json
{
  "_id": "...",
  "cveID": "CVE-2021-27104",
  "vendorProject": "Accellion",
  "product": "File Transfer Appliance (FTA)",
  "vulnerabilityName": "Accellion FTA OS Command Injection Vulnerability",
  "dateAdded": "2021-11-03T00:00:00.000Z",
  "dueDate": "2021-11-17T00:00:00.000Z",
  "daysToPatch": 14,
  "knownRansomwareCampaignUse": "Known",
  "isRansomwareAssociated": true,
  "notes": "...",
  "ingestionTimestamp": "2025-08-11T11:38:08.123Z"
}
```