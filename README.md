GreyNoise RIOT ETL Connector
Overview
This project is a simple Extract → Transform → Load (ETL) pipeline that fetches IP intelligence data from the GreyNoise API and stores it into MongoDB for further analysis.
The connector uses the GreyNoise Community API to retrieve information on whether a given IP address is part of RIOT (benign infrastructure like public DNS, content delivery networks, etc.).

Features
Extracts structured JSON data from the GreyNoise API.

Transforms (pass-through) and loads data directly into MongoDB.

Adds ETL metadata (timestamp, source, version) to each stored record.

Uses environment variables from .env file for configuration.

Implements logging for easier debugging and monitoring.

Requirements
Python 3.7+

MongoDB instance running locally or remotely.

GreyNoise API key (Community API or Enterprise API).

Installation
Clone this repository:

bash
Copy
Edit
git clone https://github.com/your-username/greynoise-riot-etl.git
cd greynoise-riot-etl
Create a virtual environment (optional but recommended):

bash
Copy
Edit
python -m venv venv
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate        # Windows
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Example requirements.txt:

nginx
Copy
Edit
requests
python-dotenv
pymongo
Create a .env file in the project directory:

ini
Copy
Edit
GREYNOISE_API_KEY=your_api_key_here
MONGO_URI=mongodb://localhost:27017
MONGO_DB=threat_intel
COLLECTION_NAME=greynoise_riot_raw
Usage
Run the ETL connector:

bash
Copy
Edit
python etl_connector.py
How It Works
Extract
Sends an HTTP GET request to:

bash
Copy
Edit
https://api.greynoise.io/v3/community/8.8.8.8
with your API key to retrieve IP intelligence data.

Transform
No major transformation is performed; data is passed through as-is.

Load
Inserts the result into MongoDB with additional ETL metadata:

json
Copy
Edit
{
  "ip": "8.8.8.8",
  "riot": true,
  "classification": "benign",
  "name": "Google Public DNS",
  "etl": {
    "source": "greynoise_riot",
    "ingested_at": "2025-08-14T00:00:00Z",
    "version": 1
  }
}
Example Output in MongoDB
json
Copy
Edit
{
  "_id": ObjectId("64d9c0f23e45f12ab8c3e4b5"),
  "ip": "8.8.8.8",
  "noise": false,
  "riot": true,
  "classification": "benign",
  "name": "Google Public DNS",
  "link": "https://viz.greynoise.io/riot/8.8.8.8",
  "last_seen": "2025-08-14",
  "http": {
    "status_code": 200,
    "fetched_at": "2025-08-14T00:00:00Z"
  },
  "etl": {
    "source": "greynoise_riot",
    "ingested_at": "2025-08-14T00:00:01Z",
    "version": 1
  }
}
Notes
The script is currently hardcoded to fetch data for 8.8.8.8 (Google DNS). You can modify the BASE_URL to accept dynamic IP addresses or loop through a list.

The Community API has request limits (about 50 requests/day). For higher limits and additional fields, use the Enterprise API.