from pymongo import MongoClient
from datetime import datetime
from config import HIBP_API_KEY, MONGODB_URI, DATABASE_NAME
from utils import fetch_breached_accounts

def main():
    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    collection = db['breached_accounts_raw']

    # Example list of emails to check
    emails = [
        "test@example.com",
        "someone@domain.com"
    ]

    for email in emails:
        print(f"Processing {email}...")
        data = fetch_breached_accounts(email, HIBP_API_KEY)
        
        if data:
            record = {
                "email": email,
                "breaches": data,
                "ingestion_timestamp": datetime.utcnow()
            }
            collection.insert_one(record)
            print(f"Inserted data for {email}")
        else:
            print(f"No breach data for {email}")

if __name__ == "__main__":
    main()
