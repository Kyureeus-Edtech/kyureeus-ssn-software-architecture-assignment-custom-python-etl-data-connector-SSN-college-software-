from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
try:
    client.admin.command('ping')
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print("❌ Connection failed:", e)
