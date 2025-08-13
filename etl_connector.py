import requests
import csv
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime
from requests.exceptions import RequestException

# Load environment variables
load_dotenv()

# MongoDB Connection
try:
    client = MongoClient(os.getenv("MONGO_CONNECTION_URL"))
    db = client[os.getenv("DB_NAME")]
    collection = db["malware_urls"]
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    exit(1)

# Function to process and insert data
def process_data(headers, rows):
    inserted_count = 0
    for row in rows:
        if not row :
            print(f"Skipping malformed row: {row}")
            continue

        doc = dict(zip(headers, row))
        doc["ingested_at"] = datetime.now()

        try:
            collection.insert_one(doc)
            inserted_count += 1
        except Exception as e:
            print(f"Failed to insert document: {e}")
    
    print(f"Successfully inserted {inserted_count} documents.")

# Iterative API fetch & validation
try:
    response = requests.get(os.getenv("API"), timeout=10)

    if response.status_code == 200:
        # Validate payload
        if not response.text.strip():
            print("Empty API response, nothing to process.")
        else:
            data_lines = response.text[467:].split("\n")
            if len(data_lines) <= 1:
                print("No data rows found after header.")
            else:
                headers = data_lines[0].split(",")
                rows = []

                with open("response.csv", "w", newline="") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(headers)

                    for i in data_lines[1:]:
                        if not i.strip():  # Skip empty lines
                            continue
                        row = i.split('","')
                        row[-1]=row[-1].rstrip()
                        row[-1]=row[-1].rstrip('"')
                        row[0]=row[0].lstrip()
                        row[0]=row[0].lstrip('"')
                        writer.writerow(row)
                        rows.append(row)

                process_data(headers, rows)

    elif response.status_code == 429:
        print("Error: Rate limit reached. Try again later.")
    elif response.status_code == 404:
        print("Error: Page not found.")
    else:
        print(f"Unexpected HTTP status: {response.status_code}")

except RequestException as e:
    print(f"Network/Connection error: {e}")
