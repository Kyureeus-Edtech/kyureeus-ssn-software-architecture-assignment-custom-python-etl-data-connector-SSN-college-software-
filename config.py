# config.py
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
# Update this line
ABUSECH_API_KEY = os.getenv("ABUSECH_API_KEY")