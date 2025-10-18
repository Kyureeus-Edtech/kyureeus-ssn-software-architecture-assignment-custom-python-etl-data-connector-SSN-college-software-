# main.py
from extract import (
    get_last_vulnerabilities,
    get_recent_vulnerabilities,
    get_stats_most_commented,
    get_stats_most_sighted,
    get_vendors,
    get_products,
    get_sightings

)
from transform import transform_vulnerabilities
from load import insert_to_mongo
from datetime import datetime


def run_etl():
    print(f"\nStarting ETL Run — {datetime.utcnow()}")

    # 1️⃣ Extract vendors and their products
    print("\nExtracting vendors and sample products...")
    vendors = get_vendors()
    insert_to_mongo("vendors_raw", [{"vendor": v, "ingested_at": datetime.utcnow()} for v in vendors])

    for vendor in vendors[:3]:  # limit to 3 vendors for demonstration
        products = get_products(vendor)
        insert_to_mongo("products_raw", [{"vendor": vendor, "product": p, "ingested_at": datetime.utcnow()} for p in products])

    # 3️⃣ Get last 20 vulnerabilities
    print("\nExtracting last 20 vulnerabilities...")
    last_vulns = get_last_vulnerabilities(20)
    transformed_last = transform_vulnerabilities(last_vulns)
    insert_to_mongo("vulnerabilities_last_raw", transformed_last)

    # 4️⃣ Get most-commented vulnerabilities
    print("\nExtracting most-commented vulnerabilities...")
    commented = get_stats_most_commented()
    insert_to_mongo("vulnerabilities_most_commented", commented)

    # 5️⃣ Get most-sighted vulnerabilities
    print("\nExtracting most-sighted vulnerabilities...")
    sighted = get_stats_most_sighted()
    insert_to_mongo("vulnerabilities_most_sighted", sighted)

    print("\nETL Pipeline completed successfully!")


if __name__ == "__main__":
    run_etl()
