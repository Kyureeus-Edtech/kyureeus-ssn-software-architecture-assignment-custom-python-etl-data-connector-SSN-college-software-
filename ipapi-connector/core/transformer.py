from utils.helpers import timestamp, safe_get
from utils.logger import logger

# Define expected schema for validation
EXPECTED_SCHEMA = {
    "query": str,       # IP
    "country": str,
    "city": str,
    "lat": (float, int),
    "lon": (float, int),
    "isp": str,
    "regionName": str,
    "timezone": str,
    "as": str
}

# Default values for missing or invalid data
DEFAULTS = {
    "country": "Unknown",
    "city": "Unknown",
    "isp": "Unknown ISP",
    "regionName": "Unknown Region",
    "timezone": "N/A",
    "as": "N/A"
}

def validate_field(key, value, expected_type):
    """Check if the value matches expected type and sanity limits."""
    if value is None:
        return False
    if not isinstance(value, expected_type):
        return False

    # Additional sanity checks for numeric data
    if key in ("lat", "lon"):
        if not (-90 <= float(value) <= 90) if key == "lat" else not (-180 <= float(value) <= 180):
            return False
    return True

def clean_record(record):
    """Validate and clean a single IP record."""
    cleaned = {}
    for key, expected_type in EXPECTED_SCHEMA.items():
        raw_value = safe_get(record, key)
        if validate_field(key, raw_value, expected_type):
            cleaned[key] = raw_value
        else:
            # Fallback to default or None
            default_value = DEFAULTS.get(key, None)
            cleaned[key] = default_value
            logger.warning(f"⚠️ Invalid or missing field '{key}' for IP {record.get('query')}, using default '{default_value}'")

    return cleaned

def transform_record(record):
    """Transforms a single raw record into a validated Mongo-ready document."""
    if not record or record.get("status") != "success":
        logger.error(f"Invalid record skipped: {record}")
        return None

    cleaned = clean_record(record)

    transformed = {
        "ip": cleaned.get("query"),
        "country": cleaned.get("country"),
        "city": cleaned.get("city"),
        "lat": float(cleaned.get("lat")) if cleaned.get("lat") else None,
        "lon": float(cleaned.get("lon")) if cleaned.get("lon") else None,
        "isp": cleaned.get("isp"),
        "region": cleaned.get("regionName"),
        "timezone": cleaned.get("timezone"),
        "as": cleaned.get("as"),
        "ingested_at": timestamp(),
        "raw_status": record.get("status")
    }

    # Final sanity: ensure essential fields exist
    if not transformed["ip"]:
        logger.error("Skipped record: Missing IP field.")
        return None

    logger.info(f"Transformed record for IP {transformed['ip']}")
    return transformed

def transform_batch(records):
    """Transforms and validates multiple records."""
    if not records:
        logger.warning("⚠️ Empty batch received for transformation.")
        return []
    
    valid_records = []
    for rec in records:
        transformed = transform_record(rec)
        if transformed:
            valid_records.append(transformed)
    logger.info(f"{len(valid_records)} valid records out of {len(records)} transformed.")
    return valid_records
