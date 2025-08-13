import os
from dotenv import load_dotenv

load_dotenv()

ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

BASE_URL_CHECK = "https://api.abuseipdb.com/api/v2/check"
BASE_URL_BLACKLIST = "https://api.abuseipdb.com/api/v2/blacklist"
