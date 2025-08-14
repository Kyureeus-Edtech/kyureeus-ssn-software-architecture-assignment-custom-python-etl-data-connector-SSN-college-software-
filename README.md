# SSN-college-software-architecture-Assignments — Custom Python ETL (AlienVault OTX)

**Student:** Nikilesh Jayaguptha (Roll No:3122225001081)  
**Connector:** AlienVault OTX — Subscribed Pulses 

## 📌 Overview
This ETL connects to the AlienVault OTX API (`/api/v1/pulses/subscribed`), extracts subscribed threat intelligence pulses, transforms them into a MongoDB-friendly structure, and loads them into a single collection (`alienvault_raw` by default). It follows the assignment guidelines on secure credentials, pagination, validation, and Git hygiene.

A **pulse** in OTX is a collection of related threat indicators (IP addresses, domains, file hashes, etc.) shared by security researchers.  
The pipeline:
1. **Extracts** pulses you are subscribed to.
2. **Transforms** them into a MongoDB-friendly structure.
3. **Loads** them into a specified MongoDB collection.

## 🌐 API Information

**Base URL:**  
https://otx.alienvault.com/api/v1


**Endpoint Used:**  
/pulses/subscribed


- **Method:** GET  
- **Auth:** Requires API key in request header:  


## 🧰 Tech Stack
- Python 3.10+  
- `requests`, `python-dotenv`, `pymongo`  
- MongoDB Atlas or local MongoDB

## 🔐 Setup & Configuration

1. **Clone and create your branch**
   ```bash
   git clone <shared-repo-url>
   cd SSN-college-software-architecture-Assignments
   git checkout -b <your-branch-name>

2.**Install dependencies**
```bash
pip install -r requirements.txt
```
3.**edit .env**
Edit .env with your actual values:

OTX_API_KEY=your_alienvault_otx_api_key
MONGO_URI=mongo uri
DB_NAME=etl_database

4.**Running the connector**
```bash
python etl_connector.py
```



**MongoDB Output**

**Database**: DB_NAME (default: etl_database)

**Collection**: COLLECTION_NAME (default: alienvault_raw)

Sample Document:
```json
{
  "id": "12345",
  "name": "Suspicious IP Activity",
  "description": "Indicators related to a phishing campaign",
  "author_name": "Cyber Researcher",
  "tags": ["phishing", "malware"],
  "created": "2025-08-01T10:00:00",
  "modified": "2025-08-02T12:00:00",
  "indicators": [ ... ],
  "extracted_at": "2025-08-14T18:30:00+00:00",
  "_source": "alienvault_otx_pulses_subscribed",
  "_page": 1
}
```