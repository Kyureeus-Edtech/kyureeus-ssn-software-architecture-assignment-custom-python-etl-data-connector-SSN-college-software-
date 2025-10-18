import os
import requests
import pymongo
import dns.resolver
import dns.exception
from dotenv import load_dotenv
from datetime import datetime
from time import sleep

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# MongoDB setup
client = pymongo.MongoClient(MONGO_URI)
db = client["doh_etl"]
collection = db["dns_records_raw"]

# DNS-over-HTTPS providers (will try these first)
DOH_PROVIDERS = [
    {
        "name": "Google-DoH",
        "url": "https://dns.google/resolve",
        "headers": {"accept": "application/dns-json"}
    },
    {
        "name": "Cloudflare-DoH",
        "url": "https://cloudflare-dns.com/dns-query",
        "headers": {"accept": "application/dns-json"}
    }
]

# Traditional DNS servers (fallback if DoH doesn't work)
DNS_SERVERS = ["8.8.8.8", "1.1.1.1", "9.9.9.9"]

# Record types
RECORD_TYPES = ["A", "MX", "TXT"]
MAX_RETRIES = 2
RETRY_DELAY = 1

# Load domains
try:
    with open("domains.txt") as f:
        domains = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    print(f"📁 Loaded {len(domains)} domains\n")
except FileNotFoundError:
    print("❌ domains.txt not found!")
    exit(1)

# Test which method works
def test_connectivity():
    """Test if DoH is available or if we need to use regular DNS"""
    print("🔍 Testing DNS connectivity methods...")
    
    # Test DoH
    for provider in DOH_PROVIDERS:
        try:
            response = requests.get(
                provider["url"],
                params={"name": "google.com", "type": "A"},
                headers=provider["headers"],
                timeout=10
            )
            if response.status_code == 200:
                print(f"   ✅ {provider['name']} is working!")
                return "doh", provider
        except:
            continue
    
    # Test regular DNS
    print("   ⚠️ DoH not available, trying regular DNS...")
    resolver = dns.resolver.Resolver()
    for server in DNS_SERVERS:
        try:
            resolver.nameservers = [server]
            resolver.resolve("google.com", "A")
            print(f"   ✅ Traditional DNS working (using {server})")
            return "dns", server
        except:
            continue
    
    print("   ❌ No DNS method is working!")
    return None, None

# Fetch using DoH
def fetch_via_doh(domain, rtype, provider):
    try:
        params = {"name": domain, "type": rtype}
        response = requests.get(
            provider["url"],
            params=params,
            headers=provider["headers"],
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "domain": domain,
                "record_type": rtype,
                "dns_response": data,
                "method": "DoH",
                "provider": provider["name"],
                "status": data.get("Status", -1),
                "has_answer": "Answer" in data and len(data.get("Answer", [])) > 0,
                "answer_count": len(data.get("Answer", [])),
                "ingested_at": datetime.utcnow()
            }
    except:
        pass
    return None

# Fetch using traditional DNS
def fetch_via_dns(domain, rtype, dns_server):
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [dns_server]
        resolver.timeout = 10
        resolver.lifetime = 10
        
        answers = resolver.resolve(domain, rtype)
        
        # Convert to DoH-like format
        answer_list = []
        for rdata in answers:
            if rtype == "A" or rtype == "AAAA":
                answer_list.append({"data": str(rdata)})
            elif rtype == "MX":
                answer_list.append({"data": f"{rdata.preference} {rdata.exchange}"})
            elif rtype == "TXT":
                answer_list.append({"data": " ".join([s.decode() if isinstance(s, bytes) else s for s in rdata.strings])})
            else:
                answer_list.append({"data": str(rdata)})
        
        return {
            "domain": domain,
            "record_type": rtype,
            "dns_response": {
                "Status": 0,
                "Answer": answer_list
            },
            "method": "Traditional-DNS",
            "provider": f"DNS-{dns_server}",
            "status": 0,
            "has_answer": len(answer_list) > 0,
            "answer_count": len(answer_list),
            "ingested_at": datetime.utcnow()
        }
    except dns.exception.Timeout:
        return None
    except dns.resolver.NXDOMAIN:
        return {
            "domain": domain,
            "record_type": rtype,
            "dns_response": {"Status": 3},  # NXDOMAIN
            "method": "Traditional-DNS",
            "provider": f"DNS-{dns_server}",
            "status": 3,
            "has_answer": False,
            "answer_count": 0,
            "ingested_at": datetime.utcnow()
        }
    except dns.resolver.NoAnswer:
        return {
            "domain": domain,
            "record_type": rtype,
            "dns_response": {"Status": 0},
            "method": "Traditional-DNS",
            "provider": f"DNS-{dns_server}",
            "status": 0,
            "has_answer": False,
            "answer_count": 0,
            "ingested_at": datetime.utcnow()
        }
    except:
        return None

def fetch_dns(domain, rtype, method, provider_info):
    """Unified fetch function"""
    for attempt in range(1, MAX_RETRIES + 1):
        if method == "doh":
            result = fetch_via_doh(domain, rtype, provider_info)
        else:
            result = fetch_via_dns(domain, rtype, provider_info)
        
        if result:
            collection.insert_one(result)
            print(f"   ✅ [{result['provider']}] {domain} {rtype} → {result['answer_count']} answers")
            return True
        
        if attempt < MAX_RETRIES:
            sleep(RETRY_DELAY)
    
    print(f"   ❌ {domain} {rtype} failed")
    return False

def main():
    print("="*60)
    print("🚀 DNS ETL Pipeline with Network Auto-Detection")
    print("="*60)
    
    # Auto-detect working method
    method, provider_info = test_connectivity()
    
    if not method:
        print("\n❌ Cannot connect to any DNS service!")
        print("Please check your internet connection and firewall settings.")
        return
    
    print(f"\n✅ Using method: {method.upper()}")
    print("="*60)
    
    success = 0
    failed = 0
    start = datetime.utcnow()
    
    for i, domain in enumerate(domains, 1):
        print(f"\n[{i}/{len(domains)}] {domain}")
        for rtype in RECORD_TYPES:
            if fetch_dns(domain, rtype, method, provider_info):
                success += 1
            else:
                failed += 1
            sleep(0.2)
    
    duration = (datetime.utcnow() - start).total_seconds()
    
    print("\n" + "="*60)
    print("🎯 ETL COMPLETED!")
    print("="*60)
    print(f"✅ Success: {success}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(success/(success+failed)*100):.1f}%")
    print(f"⏱️ Duration: {duration:.1f}s")
    print("="*60)

if __name__ == "__main__":
    main()