from etl.extract import get_info, analyze_host, get_endpoint_data
from etl.transform import transform_info, transform_analysis, transform_endpoint
from etl.load import load_to_mongo

def run_etl():
    host = "google.com"
    print("🚀 Starting ETL process...\n")

    # 1️⃣ Extract
    info_raw = get_info()
    analysis_raw = analyze_host(host)
    
    endpoints = analysis_raw.get("endpoints", [])
    
    # Prefer IPv4 endpoints (they're usually faster and more reliable)
    ip = None
    ipv4_endpoint = None
    ipv6_endpoint = None
    
    for ep in endpoints:
        ep_ip = ep.get("ipAddress")
        if ep_ip:
            if ":" not in ep_ip:  # IPv4 address (no colons)
                ipv4_endpoint = ep_ip
                break
            else:  # IPv6 address
                if not ipv6_endpoint:
                    ipv6_endpoint = ep_ip
    
    # Use IPv4 if available, otherwise fall back to IPv6
    ip = ipv4_endpoint or ipv6_endpoint
    
    if not ip:
        print("⚠️ No IP found for host. Skipping endpoint data.")
        endpoint_raw = {}
    else:
        ip_type = "IPv4" if ":" not in ip else "IPv6"
        print(f"🎯 Selected {ip_type} endpoint: {ip}")
        endpoint_raw = get_endpoint_data(host, ip)

    # 2️⃣ Transform
    print("\n🔄 Transforming data...")
    info_clean = transform_info(info_raw)
    analysis_clean = transform_analysis(analysis_raw)
    endpoint_clean = transform_endpoint(endpoint_raw)

    # 3️⃣ Load
    print("\n💾 Loading data into MongoDB...")
    load_to_mongo("info_raw", info_clean)
    load_to_mongo("analysis_raw", analysis_clean)
    load_to_mongo("endpoint_raw", endpoint_clean)

    print("\n✅ ETL process completed successfully!")

if __name__ == "__main__":
    run_etl()