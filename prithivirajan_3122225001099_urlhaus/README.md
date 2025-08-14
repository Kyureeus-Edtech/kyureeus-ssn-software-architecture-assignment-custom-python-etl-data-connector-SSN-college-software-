URLhaus ETL Data Connector
Overview

This ETL connector extracts malicious URL data from the URLhaus API (by abuse.ch) and loads it into MongoDB.
It downloads the latest dataset in CSV format, cleans and transforms it, and stores it for further analysis.

API Details

Provider: URLhaus

Base URL: https://urlhaus.abuse.ch

Endpoint: /downloads/csv_online/

Authentication: None (Public API)

Data Format: CSV

Rate Limit: No strict limit (but avoid excessive requests)

Setup Instructions
1. Clone Repository
git clone <your-repo-link>
cd <your-folder-name>

2. Configure Environment Variables

Create a .env file in the same folder with the following contents:

API_URL=https://urlhaus.abuse.ch/downloads/csv_online/
MONGO_URI=mongodb://localhost:27017
DB_NAME=etl_database
COLLECTION_NAME=urlhaus_raw

3. Install Dependencies
pip install -r requirements.txt

4. Run ETL
python etl_connector.py

Usage Example

Command:

python etl_connector.py


Expected Output:

✅ Connected to MongoDB successfully!
📡 Fetching data from https://urlhaus.abuse.ch/downloads/csv_online/ ...
📂 Data downloaded successfully.
🔄 Transforming data...
📊 Prepared 11507 records for insertion.
✅ Inserted 11507 records into MongoDB collection 'urlhaus_raw'.
🎉 ETL process completed successfully!

Sample CSV Data (from API)
id,dateadded,url,url_status,threat,tags,urlhaus_link,reporter
1,2025-08-14,http://malicious-site.com,online,malware,phishing,https://urlhaus.abuse.ch/url/1/,reporter1
2,2025-08-14,http://example-bad.com,offline,phishing,,https://urlhaus.abuse.ch/url/2/,reporter2

Author

Prithivirajan — Roll No: 3122225001099