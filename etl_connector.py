import os
from dotenv import load_dotenv # Used to load your credentials from .env
import requests                 # Used to make API calls to SonarQube
from pymongo import MongoClient # Used to connect and load data into MongoDB
from datetime import datetime   # Used for the ingestion timestamp

# 1. Load Environment Variables
# The script will look for the .env file in the current directory
load_dotenv() 

SONARQUBE_BASE_URL = os.getenv("SONARQUBE_BASE_URL")
SONARQUBE_TOKEN = os.getenv("SONARQUBE_TOKEN")
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")

# Define API headers for authentication
HEADERS = {
    "Authorization": f"Bearer {SONARQUBE_TOKEN}"
}

# Define the SonarQube Project Key (Replace with your actual project key if needed, or use a general endpoint)
PROJECT_KEY = "my_etl_test" 

# Define the MongoDB collection strategy
MONGODB_DATABASE_NAME = "sonarqube_assignment" 
MONGODB_COLLECTION_NAME = "sonarqube_raw" # Use one collection per connector

def extract_transform_load():
    # --- A. CONNECT TO MONGODB (LOAD PHASE SETUP) ---
    try:
        client = MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        collection = db[MONGODB_COLLECTION_NAME]
        print("Connected to MongoDB successfully.")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return

    # --- B. EXTRACT DATA FROM SONARQUBE ---
    # Example Endpoint: Get a list of components/files in the project
    endpoint = f"{SONARQUBE_BASE_URL}api/measures/component?component={PROJECT_KEY}&metricKeys=complexity,ncloc,violations"
    
    # You would typically loop through pages for large results, but we use one call for simplicity
    print(f"Extracting data from: {endpoint}")
    try:
        response = requests.get(endpoint, headers=HEADERS)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        raw_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error during API extraction: {e}")
        client.close()
        return

    # --- C. TRANSFORM DATA ---
    ingestion_timestamp = datetime.now()
    
    # The SonarQube response might contain the component data directly, but we transform it
    transformed_records = []
    
    if raw_data.get('component'):
        # Add ingestion timestamp to support audits
        raw_data['ingestion_timestamp'] = ingestion_timestamp
        transformed_records.append(raw_data)
        print(f"Transformed {len(transformed_records)} records.")
    else:
        print("No component data found in the response.")
        client.close()
        return

    # --- D. LOAD DATA INTO MONGODB ---
    if transformed_records:
        try:
            # Insert the transformed data into the MongoDB collection
            result = collection.insert_many(transformed_records)
            print(f"Successfully loaded {len(result.inserted_ids)} records into MongoDB.")
        except Exception as e:
            print(f"Error loading data into MongoDB: {e}")
    
    client.close()
    print("ETL process complete.")

if __name__ == "__main__":
    extract_transform_load()