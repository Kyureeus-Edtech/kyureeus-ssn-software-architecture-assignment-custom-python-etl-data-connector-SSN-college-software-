# transformations/data_transformer.py
import logging
from datetime import datetime

def standardize_urlhaus_data(raw_data):
    """Transforms URLhaus data into a standard format."""
    if not raw_data or 'urls' not in raw_data:
        return []

    transformed = []
    for item in raw_data['urls']:
        # Example transformation: add a threat_level based on tags
        threat_level = 'high' if 'exe' in (item.get('tags') or []) else 'medium'

        doc = {
            '_id': item['id'], # Use a natural unique key as the MongoDB _id
            'source': 'URLhaus',
            'ioc_type': 'url',
            'ioc_value': item['url'],
            'threat_type': item.get('threat'),
            'tags': item.get('tags', []),
            'threat_level': threat_level,
            'first_seen': datetime.strptime(item['date_added'], "%Y-%m-%d %H:%M:%S %Z")
        }
        transformed.append(doc)
    logging.info(f"Transformed {len(transformed)} records from URLhaus.")
    return transformed

def standardize_malwarebazaar_data(raw_data):
    """Transforms MalwareBazaar data into a standard format."""
    if not raw_data or 'data' not in raw_data:
        return []

    transformed = []
    for item in raw_data['data']:
        # Example transformation: Classify file type
        file_class = 'document' if item.get('file_type') in ['docx', 'pdf'] else 'executable'

        # --- REPLACE THE 'first_seen' LOGIC WITH THIS BLOCK ---
        first_seen_val = item.get('first_seen')
        first_seen_dt = None # Default to None if parsing fails
        if first_seen_val:
            # Check if the string is a number (Unix timestamp)
            if first_seen_val.isdigit():
                first_seen_dt = datetime.fromtimestamp(int(first_seen_val))
            # Otherwise, try to parse it as a date string
            else:
                try:
                    first_seen_dt = datetime.strptime(first_seen_val, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    logging.warning(f"Could not parse date: {first_seen_val}")

        doc = {
            '_id': item['sha256_hash'],
            'source': 'MalwareBazaar',
            'ioc_type': 'hash_sha256',
            'ioc_value': item['sha256_hash'],
            'signature': item.get('signature'),
            'tags': item.get('tags', []),
            'file_class': file_class,
            'first_seen': first_seen_dt # Use the parsed datetime object
        }
        transformed.append(doc)
    logging.info(f"Transformed {len(transformed)} records from MalwareBazaar.")
    return transformed