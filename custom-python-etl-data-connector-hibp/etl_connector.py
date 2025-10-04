from hibp_client import list_breaches, breach_by_name, data_classes, pwned_password_range
from db import insert_data

def run_etl():
    print("🚀 Starting HIBP ETL (no-key)...")

    # 1. All breaches
    breaches = list_breaches()
    insert_data("breaches_raw", breaches)

    # 2. Single breach example
    adobe = breach_by_name("Adobe")
    insert_data("breach_adobe_raw", [adobe] if adobe else [])

    # 3. Data classes
    dataclasses = data_classes()
    insert_data("dataclasses_raw", dataclasses)

    # 4. Password range example
    pw_range = pwned_password_range("21BD1")
    if pw_range:
        insert_data("password_range_raw", [{"range": "21BD1", "data": pw_range}])

    print("✅ HIBP ETL Finished")

if __name__ == "__main__":
    run_etl()
