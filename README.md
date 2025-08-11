# AlienVault OTX Pulses ETL Pipeline

##  Overview
This assignment implements an **ETL (Extract, Transform, Load)** pipeline to:
1. **Extract** threat intelligence data (pulses) from the [AlienVault OTX API](https://otx.alienvault.com/api).
2. **Transform** the raw JSON into a structured format for analysis.
3. **Load** the processed data into a MongoDB collection for storage and querying.

It also generates quick insights from the fetched data (e.g., top tags, author stats, threat level counts).

---

##  Features
- Connects to the AlienVault OTX API using your API key.
- Fetches subscribed pulses with pagination.
- Cleans, validates, and transforms the data for MongoDB compatibility.
- Inserts or updates pulses into MongoDB (`upsert` support).
- Prints analytical insights about fetched data.
- Stage-by-stage logging for easy debugging.

---

##  Project Structure
/your-branch-name/ ├── etl_connector.py  ├── config.py ├── .env ├── requirements.txt ├── README.md

.env: Store sensitive credentials; do not commit this file. <br>
etl_connector.py: Your main ETL script.<br>
config.py: Loads all configurations from the .env file into a single dictionary for easy access across the ETL script. <br>
requirements.txt: List all Python dependencies. <br>
README.md: Instructions for the connector. <br>

## Prerequisites
Before running this ETL pipeline, ensure you have:

- **Python 3.8+** installed  
- **MongoDB** (local or remote instance) running and accessible  
- **AlienVault OTX API key**  
  - Sign up for a free account at [https://otx.alienvault.com](https://otx.alienvault.com)  
  - Retrieve your API key from your account settings  
- **Git** (optional, for cloning the repository)  
- **pip** (Python package installer, included with Python)  

## Installation & Setup

1. Create a virtual environment (recommended): <br>
&nbsp; &nbsp;&nbsp;&nbsp;python -m venv venv

2. Activate the virtual environment: <br>
   &nbsp; &nbsp;&nbsp;&nbsp;Windows (PowerShell): .\venv\Scripts\Activate.ps1 <br>
    &nbsp; &nbsp;&nbsp;&nbsp;macOS/Linux: source venv/bin/activate

3. Install dependencies: <br>
    &nbsp; &nbsp;&nbsp;&nbsp;pip install -r requirements.txt

4. Set up the .env file: Create a file named .env in the project root with the following content: <br>
    &nbsp; &nbsp;&nbsp;&nbsp;API_KEY=your_alienvault_otx_api_key <br>
    &nbsp; &nbsp;&nbsp;&nbsp;BASE_URL=https://otx.alienvault.com/api/v1/ <br>
    &nbsp; &nbsp;&nbsp;&nbsp;PULSES_SUBSCRIBED_ENDPOINT=pulses/subscribed<br>
    &nbsp; &nbsp;&nbsp;&nbsp;MONGO_URI=your_mongo_url <br>
    &nbsp; &nbsp;&nbsp;&nbsp;MONGO_DB=your_mongo_db <br>
    &nbsp; &nbsp;&nbsp;&nbsp;PAGE_LIMIT=page_limit <br>

5. Run the ETL pipeline: <br>
    &nbsp; &nbsp;&nbsp;&nbsp;python etl_connector.py

