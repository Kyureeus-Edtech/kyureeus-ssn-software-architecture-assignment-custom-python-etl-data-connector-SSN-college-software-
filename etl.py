import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("MALSHARE_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client["malware_db"]
collection = db["malware_samples"]
# Extract
def extract_malware_list():
    url = f"https://malshare.com/api.php?api_key={API_KEY}&action=getlist"
    response = requests.get(url)
    response.raise_for_status()  # raise error if bad status
    return response.json()  # MalShare returns JSON

# Transform
def transform_data(data):
    transformed = []
    print(data[0].keys())
    for entry in data:
        transformed.append({
            "sha256": entry.get("sha256"),
            "sha1": entry.get("sha1"),
            "md5": entry.get("md5"),
            "source": "MalShare"
        })
    return transformed

# Load
def load_to_mongodb(data):
    if data:
        collection.insert_many(data)
        print(f"Inserted {len(data)} records into MongoDB")
    else:
        print("No data to insert.")

if __name__ == "__main__":
    raw_data = extract_malware_list()
    transformed_data = transform_data(raw_data)
    load_to_mongodb(transformed_data)
