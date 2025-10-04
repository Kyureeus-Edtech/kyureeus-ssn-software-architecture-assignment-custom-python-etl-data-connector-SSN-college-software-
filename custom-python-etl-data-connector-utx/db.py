import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB", "otx_connector")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
