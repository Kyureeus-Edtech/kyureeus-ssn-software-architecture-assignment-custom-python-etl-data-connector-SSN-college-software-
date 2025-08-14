ThreatFox IOC ETL Pipeline This project implements an ETL (Extract → Transform → Load) pipeline in Python to fetch Indicators of Compromise (IOCs) from the ThreatFox API, transform them into a structured format, and load them into a MongoDB database for further analysis and threat intelligence processing.
The script uses environment variables to store API endpoints and MongoDB credentials securely. It is modular and can be extended to work with other threat intelligence feeds.

📌 Features Extract: Fetches a configurable number of IOCs from the ThreatFox API.

Transform: Normalizes and structures IOC data for MongoDB storage.

Load: Inserts cleaned IOC records into a MongoDB collection.

Secure: Uses a .env file to manage credentials and settings.

Configurable: Easily change the number of IOCs to fetch.

Error Handling: Handles API failures, empty responses, and database connection issues.

⚙️ How to Run Prerequisites:

Python 3.8+

MongoDB (local or Atlas)

ThreatFox API access (public API)

Clone & Install:

git clone cd pip install -r requirements.txt Set Up Environment Variables: Create a .env file in the project directory with the following content:

THREATFOX_API_URL="https://threatfox-api.abuse.ch/api/v1/" MONGO_URI="your-mongodb-uri" MONGO_DB="your-database-name" MONGO_COLLECTION="your-collection-name" IOC_LIMIT=50 Run the Script:

python etlconnector.py Verify Data in MongoDB: Connect to your MongoDB instance and check the inserted IOC documents.
