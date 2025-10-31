# GreyNoise RIOT ETL Connector

## Overview
This ETL pipeline connects to the **GreyNoise RIOT** API, extracts IP address intelligence, transforms it into a MongoDB-compatible format, and loads it into a dedicated MongoDB collection.  

The **RIOT** dataset contains IPs of benign services like search engine crawlers and content delivery networks (CDNs), helping analysts avoid false positives in threat detection.

---

## API Details
- **Source:** [GreyNoise RIOT](https://viz.greynoise.io/riot)
- **Authentication:** None required
- **Format:** JSON
- **Default Endpoint:** `https://viz.greynoise.io/riot`

---

## Project Structure
/your-branch-name/
├── etl_connector.py # Main ETL script
├── .env # Environment variables (not committed to git)
├── .env.example # Template for env variables
├── requirements.txt # Python dependencies
└── README.md # Project documentation