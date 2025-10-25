# n.py
import os
import requests
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

SONAR_BASE_URL = os.getenv("SONAR_API_BASE")  # e.g., http://localhost:9000/api
SONAR_TOKEN = os.getenv("SONAR_TOKEN")       # Your token
PROJECT_KEY = os.getenv("SONAR_PROJECT_KEY") # e.g., VIGS
MONGODB_URI = os.getenv("DB_URI")            # MongoDB URI

# Headers for authentication
HEADERS = {
    "Authorization": f"Bearer {SONAR_TOKEN}"
}

# Metrics to fetch
METRICS = "bugs,vulnerabilities,code_smells,coverage,duplicated_lines_density"

def fetch_sonar_metrics():
    """Fetch project metrics from SonarQube API."""
    url = f"{SONAR_BASE_URL}/measures/component"
    params = {
        "component": PROJECT_KEY,
        "metricKeys": METRICS
    }
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        data = response.json()
        print("Fetched SonarQube project data:")
        return data
    else:
        print(f"Failed to fetch data: Status code {response.status_code}")
        print(response.text)
        return None

def transform(data):
    """Transform API response to a clean dictionary."""
    if not data or "component" not in data:
        return {}

    component = data["component"]
    measures = component.get("measures", [])

    transformed = {
        "project_key": PROJECT_KEY,
        "timestamp": datetime.utcnow(),
    }

    for measure in measures:
        metric = measure.get("metric")
        value = measure.get("value")
        transformed[metric] = value

    print(f"Transformed data: {transformed}")
    return transformed

def insert_into_mongo(data):
    """Insert the transformed data into MongoDB."""
    if not data:
        print("No data to insert")
        return

    client = MongoClient(MONGODB_URI)
    db = client.get_database()
    collection = db['sonar_metrics']  # Collection name

    result = collection.insert_one(data)
    print(f"Inserted 1 document into MongoDB with id: {result.inserted_id}")

def main():
    data = fetch_sonar_metrics()
    clean_data = transform(data)
    insert_into_mongo(clean_data)

if __name__ == "__main__":
    main()
