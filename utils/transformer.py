from datetime import datetime, timezone

def transform_ip_data(ip_data):
    """
    Transform AbuseIPDB IP data for MongoDB storage.
    Adds ingestion timestamp and ensures timezone-aware datetime.
    """
    if not ip_data:
        return None
    return {
        **ip_data,
        "ingested_at": datetime.now(timezone.utc)
    }
