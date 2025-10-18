import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

mongoConfig = {
    "URI": os.getenv('MONGO_URI', 'mongodb://localhost:27017/'),
    "DB": 'malshare_db',
    "COLLECTION": 'malshare_raw'
}