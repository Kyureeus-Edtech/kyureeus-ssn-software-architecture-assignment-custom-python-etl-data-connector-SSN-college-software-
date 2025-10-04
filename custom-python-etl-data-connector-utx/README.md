# OTX ETL Connector

This project is a Python-based ETL (Extract, Transform, Load) connector that pulls subscribed pulses from the **AlienVault OTX API** and stores them in **MongoDB**.

## 1. Prerequisites
- Python 3.9+
- MongoDB 
- OTX account & API key 


## 2. Installation
Clone the repository:
git clone <repo_url>
cd <repo_folder>

Create and activate a virtual environment:
python -m venv venv
venv\Scripts\activate     # Windows 

Install dependencies:
pip install -r requirements.txt

Create a .env file in the project root:
OTX_API_KEY=your_otx_api_key
OTX_BASE_URL=https://otx.alienvault.com
MONGO_URI=your_mongo_url
MONGO_DB=otx_connectors

Run the ETL:
python etl_connector.py
