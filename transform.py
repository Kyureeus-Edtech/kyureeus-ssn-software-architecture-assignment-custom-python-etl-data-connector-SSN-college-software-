from datetime import datetime

def transform_data(ip, raw_data):
    if not raw_data:
        raise ValueError(f"No data returned for IP {ip}.")

    return {
        "ip": ip,
        "riot": raw_data.get("riot", False),
        "result": raw_data,
        "source": "GreyNoise Community API",
        "fetched_at": datetime.utcnow()
    }