import requests
import time
import json

BASE_URL = "https://api.ssllabs.com/api/v3"

def debug_info():
    """Test the info endpoint"""
    print("=" * 60)
    print("1️⃣ Testing /info endpoint")
    print("=" * 60)
    try:
        res = requests.get(f"{BASE_URL}/info", timeout=10)
        print(f"Status Code: {res.status_code}")
        print(f"Headers: {dict(res.headers)}")
        print(f"Response: {json.dumps(res.json(), indent=2)}")
        return res.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def debug_analyze(host="google.com"):
    """Test the analyze endpoint"""
    print("\n" + "=" * 60)
    print(f"2️⃣ Testing /analyze endpoint for {host}")
    print("=" * 60)
    try:
        url = f"{BASE_URL}/analyze"
        params = {"host": host, "fromCache": "on", "all": "done"}
        print(f"URL: {url}")
        print(f"Params: {params}")
        
        res = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {res.status_code}")
        print(f"Response Length: {len(res.text)} characters")
        
        data = res.json()
        print(f"\nHost: {data.get('host')}")
        print(f"Status: {data.get('status')}")
        print(f"Endpoints found: {len(data.get('endpoints', []))}")
        
        for i, ep in enumerate(data.get('endpoints', []), 1):
            print(f"\n  Endpoint {i}:")
            print(f"    IP: {ep.get('ipAddress')}")
            print(f"    Grade: {ep.get('grade')}")
            print(f"    Status: {ep.get('statusMessage')}")
            print(f"    Progress: {ep.get('progress')}%")
        
        return data
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def debug_endpoint(host, ip):
    """Test the getEndpointData endpoint with detailed debugging"""
    print("\n" + "=" * 60)
    print(f"3️⃣ Testing /getEndpointData for {host} ({ip})")
    print("=" * 60)
    
    for attempt in range(5):
        try:
            url = f"{BASE_URL}/getEndpointData"
            params = {"host": host, "s": ip, "fromCache": "on"}  # Use 's' parameter instead of 'ip'
            
            print(f"\nAttempt {attempt + 1}/5")
            print(f"URL: {url}")
            print(f"Params: {params}")
            
            start_time = time.time()
            res = requests.get(url, params=params, timeout=20)
            elapsed = time.time() - start_time
            
            print(f"Status Code: {res.status_code}")
            print(f"Response Time: {elapsed:.2f}s")
            print(f"Response Length: {len(res.text)} characters")
            
            if res.status_code == 441:
                print(f"⚠️ Status 441: Assessment in progress")
                print(f"Response body: {res.text[:200]}...")
                print(f"Waiting 15 seconds before retry...")
                time.sleep(15)
                continue
            
            if res.status_code == 200:
                data = res.json()
                print(f"✅ Success!")
                print(f"Status Message: {data.get('statusMessage')}")
                print(f"Server Name: {data.get('serverName')}")
                print(f"Has Details: {bool(data.get('details'))}")
                if data.get('details'):
                    print(f"Details Keys: {list(data.get('details', {}).keys())[:10]}")
                return data
            
            print(f"Unexpected status code: {res.status_code}")
            print(f"Response: {res.text[:500]}")
            
        except requests.exceptions.Timeout:
            print(f"⏳ Request timed out after 20 seconds")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        if attempt < 4:
            print(f"Retrying in 15 seconds...")
            time.sleep(15)
    
    print(f"\n🚫 Failed after 5 attempts")
    return None

def test_with_fresh_scan(host="example.com"):
    """Start a fresh scan and track it"""
    print("\n" + "=" * 60)
    print(f"4️⃣ Testing FRESH scan for {host}")
    print("=" * 60)
    
    try:
        # Start new scan
        res = requests.get(
            f"{BASE_URL}/analyze",
            params={"host": host, "startNew": "on"},
            timeout=10
        )
        data = res.json()
        print(f"Scan started. Status: {data.get('status')}")
        
        # Poll until ready
        max_polls = 30  # 5 minutes max
        for i in range(max_polls):
            time.sleep(10)
            res = requests.get(
                f"{BASE_URL}/analyze",
                params={"host": host},
                timeout=10
            )
            data = res.json()
            status = data.get('status')
            print(f"Poll {i+1}/{max_polls}: Status = {status}")
            
            if status == "READY":
                print(f"✅ Scan complete!")
                endpoints = data.get('endpoints', [])
                if endpoints:
                    ip = endpoints[0].get('ipAddress')
                    print(f"First endpoint IP: {ip}")
                    # Now try to get endpoint data
                    return debug_endpoint(host, ip)
                break
            elif status == "ERROR":
                print(f"❌ Scan failed: {data.get('statusMessage')}")
                break
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🔍 SSL Labs API Debugging Tool")
    print("=" * 60)
    
    # Test 1: Info
    info = debug_info()
    time.sleep(2)
    
    # Test 2: Analyze
    analysis = debug_analyze("google.com")
    time.sleep(2)
    
    # Test 3: Endpoint data
    if analysis:
        endpoints = analysis.get('endpoints', [])
        
        # Try IPv4 first
        ipv4 = None
        ipv6 = None
        
        for ep in endpoints:
            ip = ep.get('ipAddress')
            if ip and ':' not in ip:
                ipv4 = ip
                break
            elif ip:
                ipv6 = ip
        
        test_ip = ipv4 or ipv6
        
        if test_ip:
            ip_type = "IPv4" if ':' not in test_ip else "IPv6"
            print(f"\n🎯 Testing with {ip_type} address: {test_ip}")
            debug_endpoint("google.com", test_ip)
    
    # Test 4: Fresh scan (optional - uncomment to test)
    # print("\n" + "=" * 60)
    # print("Would you like to test a fresh scan? (takes 2-3 minutes)")
    # response = input("Type 'yes' to continue: ")
    # if response.lower() == 'yes':
    #     test_with_fresh_scan("example.com")
    
    print("\n" + "=" * 60)
    print("✅ Debugging complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()