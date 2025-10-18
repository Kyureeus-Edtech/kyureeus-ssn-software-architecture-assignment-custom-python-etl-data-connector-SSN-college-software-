# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base API URL
API_BASE = "https://cve.circl.lu/api"

# MongoDB credentials
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "cve_data")

# Optional authentication for endpoints that require it
USER_AUTH = os.getenv("USER_AUTH")
