from dotenv import load_dotenv
import os

load_dotenv()

HIBP_API_KEY = os.getenv('HIBP_API_KEY')
MONGODB_URI = os.getenv('MONGODB_URI')
DATABASE_NAME = os.getenv('DATABASE_NAME')
