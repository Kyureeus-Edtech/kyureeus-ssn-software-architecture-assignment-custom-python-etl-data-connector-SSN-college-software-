import os
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def get_mongo_uri():
    return os.getenv("MONGO_URI", "mongodb://localhost:27017/")

def timestamp():
    return datetime.utcnow().isoformat()
