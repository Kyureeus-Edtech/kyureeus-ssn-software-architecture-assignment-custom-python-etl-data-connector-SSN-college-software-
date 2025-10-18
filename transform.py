# transform.py
from datetime import datetime

def transform_vulnerabilities(data):
    """Clean and reformat vulnerability JSON for MongoDB."""
    if not data:
        return []

    transformed = []
    for item in data:
        record = {
            "id": item.get("id") or item.get("cve"),
            "summary": item.get("summary"),
            "cvss": item.get("cvss"),
            "cvss3": item.get("cvss3"),
            "published": item.get("Published"),
            "modified": item.get("Modified"),
            "references": item.get("references"),
            "vendor": item.get("vendor"),
            "product": item.get("product"),
            "ingested_at": datetime.utcnow()
        }
        transformed.append(record)
    return transformed
