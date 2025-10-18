import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Abuse.ch API endpoints
URLHAUS_API_URL = os.getenv("URLHAUS_API_URL")
MALWAREBAZAAR_API_URL = os.getenv("MALWAREBAZAAR_API_URL")
THREATFOX_API_URL = os.getenv("THREATFOX_API_URL")

# API Key
ABUSECH_API_KEY = os.getenv("ABUSECH_API_KEY")

# MongoDB Configuration
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")
