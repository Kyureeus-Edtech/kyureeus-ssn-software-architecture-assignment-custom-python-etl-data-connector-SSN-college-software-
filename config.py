import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the variables
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
API_BASE_URL = "https://networkcalc.com/api"