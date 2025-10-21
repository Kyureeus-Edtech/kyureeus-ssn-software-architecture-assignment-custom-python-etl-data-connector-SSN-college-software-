# Assignment 2 – FreeGeoIP ETL Pipeline

**Student Name:** Ankitha Reddy A  

**Register Number:** 3122225001013 

**Digital ID:** 2210178

**Course:** UCS2703 - Software Architecture

**Batch:** 2022-2026 (SSN College of Engineering)

**Date:** 21/10/2025

---

## Overview

This assignment implements a complete ETL (Extract, Transform, Load) pipeline to extract geolocation data from the IPStack API, enrich it with analytical intelligence, and store the processed results in MongoDB. The pipeline integrates risk assessment, network profiling, and global relationship clustering, providing a structured intelligence framework for IP-based geospatial analysis.

---

## Key Features

1. **Data Extraction**
   - Retrieves geolocation details for sample IP addresses using IPStack API.
   - Handles missing fields and API errors gracefully.

2. **Data Transformation**
   - **Risk Profiling:** Computes a geographic risk score based on continent stability, economic classification, and timezone alignment.
   - **Network Intelligence:** Classifies ISP type, evaluates traffic patterns, and assesses security posture.
   - **Global Relationships:** Creates country and risk clusters for relationship analysis.

3. **Data Loading**
   - Stores enriched intelligence documents in a MongoDB collection (`transformed_geo_data`) using upsert logic.
   - Ensures data consistency and prevents duplication.

4. **Configurability**
   - Sensitive credentials such as API key and MongoDB URI are managed via a `.env` file.
   - `TEST_MODE` option allows limiting the number of IPs for debugging.

---

## Technology Stack

- **Language:** Python  
- **API:** IPStack Geolocation API  
- **Database:** MongoDB  
- **Libraries:** `requests`, `pymongo`, `python-dotenv`, `logging`, `hashlib`, `datetime`, `collections`

---

## How to Run

1. **Set Environment Variables:**  
   Create a `.env` file with:
`IPSTACK_API_KEY=your_api_key_here`
`MONGO_URI=mongodb://localhost:27017/`
`MONGO_DB_NAME=geolocation_db`

2. **Install Dependencies:**  
`pip install requests pymongo python-dotenv`

3. **Run the Script:**  
`python etl_connector.py`

4. **Output:**  
- Console logs for each pipeline step.
- Tabulated summary of processed IPs, inserted/updated records, countries covered, and risk distribution.

---

## MongoDB Output Structure

Each document stored in MongoDB follows this structure:

```
{
"_id": "unique_hash",
"source_ip": "8.8.8.8",
"basic_geo": {
 "country": "United States",
 "region": "California",
 "city": "Mountain View",
 "coordinates": {"lat": 37.388, "lng": -122.074},
 "continent": "North America"
},
"risk_intelligence": {
 "overall_risk_score": 1.5,
 "development_tier": "Developed",
 "regional_stability": 0.9,
 "timezone_alignment": 0.6
},
"network_intelligence": {
 "isp_type": "hosting",
 "traffic_volume": "consistent",
 "peak_hours": [0, 24],
 "security_posture": "enterprise"
},
"global_relationships": {
 "country_cluster": {
   "country": "United States",
   "cluster_members": 5,
   "member_ips": ["8.8.8.8", "142.250.191.206", "..."]
 },
 "risk_cluster": {
   "level": "low_risk",
   "cluster_members": 7,
   "similar_risk_ips": ["8.8.8.8", "14.1.44.138", "..."]
 },
 "regional_partners": ["Canada", "Mexico", "United Kingdom"]
},
"ingestion_timestamp": "2025-10-21T14:00:00Z",
"data_freshness": "realtime"
}
```

## Learning Outcomes
By completing this assignment, I have learnt to:

1. Design and implement an end-to-end ETL pipeline integrating API data extraction, transformation, and database loading.
2. Apply geospatial and network intelligence techniques for risk profiling and ISP classification.
3. Build global relationship models to identify country and risk clusters.
4. Use MongoDB for storing structured intelligence data with upsert operations.
5. Manage credentials securely and implement error handling for API calls and data ingestion.
6. Interpret and visualize geolocation intelligence metrics for analytical and decision-making purposes.