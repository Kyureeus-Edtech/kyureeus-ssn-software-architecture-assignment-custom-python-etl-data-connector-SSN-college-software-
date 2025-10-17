from datetime import datetime

def timestamp():
    return datetime.utcnow().isoformat()

def safe_get(record, key, default=None):
    return record.get(key, default) if isinstance(record, dict) else default
