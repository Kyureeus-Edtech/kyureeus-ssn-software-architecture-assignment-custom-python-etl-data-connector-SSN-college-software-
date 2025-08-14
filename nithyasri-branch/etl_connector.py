import requests
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client["weather_db"]
collection = db["weather_raw"]

def extract(city="Chennai"):
    """Extract weather data from OpenWeather API"""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code}")
    return response.json()

def transform(data):
    """Transform raw API data into MongoDB format"""
    return {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "weather": data["weather"][0]["description"],
        "timestamp": datetime.utcnow()
    }

def load(data):
    """Load transformed data into MongoDB"""
    collection.insert_one(data)
    print("Data inserted into MongoDB:", data)

if __name__ == "__main__":
    try:
        raw_data = extract("Chennai")
        transformed_data = transform(raw_data)
        load(transformed_data)
    except Exception as e:
        print("Error:", e)
