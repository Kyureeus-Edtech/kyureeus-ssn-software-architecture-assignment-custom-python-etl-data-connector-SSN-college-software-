Custom Python ETL Data Connector
This project is a Python-based ETL (Extract, Transform, Load) data connector designed to interact with an API, retrieve data, process it, and store the results in MongoDB.

Features
Accepts API key and input URL from the command line.

Sends HTTP requests to an API endpoint.

Parses and logs responses.

Stores results in MongoDB.

Handles errors and logging gracefully.

Requirements
Python 3.8+

MongoDB running locally or remotely

Dependencies listed in requirements.txt

Installation
Clone the repository:

git clone <repository-url>
cd custom-python-etl-data-connector
Create and activate a virtual environment:

python3 -m venv venv
source venv/bin/activate
Install dependencies:

pip install -r requirements.txt
Usage
Run the script as follows:

python3 submit_url.py <API_KEY> <TARGET_URL>
Example:

python3 connector.py <API_KEY>  http://example.com/malware.exe
Configuration
The MongoDB connection details can be configured in connector.py:

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "etl_data"
COLLECTION_NAME = "api_responses"
Output
The API response is printed to the console.

The data is stored in MongoDB with a timestamp.

Error Handling
Handles network errors, invalid API keys, and database insertion errors.

Logs informative messages for debugging.