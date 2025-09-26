import datetime
from db import db
import otx_client

def transform(data):
    """Clean + attach ingestion timestamp"""
    if not data:
        return None
    return {
        "data": data,
        "ingested_at": datetime.datetime.now(datetime.UTC)
    }

def load(collection_name, data):
    if not data:
        print(f"⚠️ Skipping load: No data for {collection_name}")
        return
    db[collection_name].insert_one(data)
    print(f"✅ Inserted into {collection_name}")

def run_etl():
    # 1. Subscribed Pulses
    data = otx_client.get_subscribed_pulses()
    load("pulses_subscribed_raw", transform(data))

    # 2. My Pulses
    data = otx_client.get_my_pulses()
    load("pulses_my_raw", transform(data))

    # 3. Pulse Activity
    data = otx_client.get_pulse_activity()
    load("pulses_activity_raw", transform(data))

    # 4. Indicators: IP
    data = otx_client.get_indicator_by_ip("8.8.8.8")
    load("indicators_ip_raw", transform(data))

    # 5. Indicators: Domain
    data = otx_client.get_indicator_by_domain("example.com")
    load("indicators_domain_raw", transform(data))

    # 6. Indicators: CVE
    data = otx_client.get_indicator_by_cve("CVE-2023-12345")
    load("indicators_cve_raw", transform(data))

if __name__ == "__main__":
    run_etl()
