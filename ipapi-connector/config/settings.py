import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Config
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "ip_data")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "ipapi_raw")

# API Config
BASE_URL = "http://ip-api.com/json/"
BATCH_URL = "http://ip-api.com/batch"
TIMEOUT = 5
