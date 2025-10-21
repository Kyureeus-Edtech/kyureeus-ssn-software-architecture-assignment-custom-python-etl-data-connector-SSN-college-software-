import os
from pymongo import MongoClient
from dotenv import load_dotenv
from etl_connector import run_pipeline, get_collection

load_dotenv()

# Test DB configuration
TEST_DB_NAME = "test_etl_db"
TEST_COLLECTION_NAME = "test_etl_collection"

# MongoDB client for assertions
client = MongoClient(os.getenv("MONGO_URI"))
collection = client[TEST_DB_NAME][TEST_COLLECTION_NAME]

def test_full_pipeline():
    # Clear before test
    collection.delete_many({})

    # Run pipeline with test DB/collection
    run_pipeline(db_name=TEST_DB_NAME, collection_name=TEST_COLLECTION_NAME)

    # Fetch records
    records = list(collection.find({}))

    # Assertions
    assert len(records) > 0, "No records were inserted"
    assert all("ingested_at" in rec for rec in records), "Missing timestamps"
    assert all(rec["type"] in ["ip", "cidr"] for rec in records), "Invalid type classification"
    assert len({rec["ip"] for rec in records}) == len(records), "Duplicates found"

    print("Integration test passed.")

if __name__ == "__main__":
    test_full_pipeline()
