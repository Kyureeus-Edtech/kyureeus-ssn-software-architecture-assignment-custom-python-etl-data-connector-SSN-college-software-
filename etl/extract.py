import requests
import time

BASE_URL = "https://api.ssllabs.com/api/v3"

def get_info():
    """Fetch general API system info."""
    print("📡 Fetching SSL Labs API info...")
    res = requests.get(f"{BASE_URL}/info")
    res.raise_for_status()
    return res.json()

def analyze_host(host):
    """Analyze a host and wait until results are ready (using cache for speed)."""
    print(f"🔍 Starting analysis for host: {host}")
    # use cached results if available to avoid long scans
    res = requests.get(f"{BASE_URL}/analyze", params={"host": host, "fromCache": "on", "all": "done"}).json()
    
    status = res.get("status")
    while status in ["IN_PROGRESS", "DNS"]:
        print(f"🕐 Analysis in progress... retrying in 10s (status: {status})")
        time.sleep(10)
        res = requests.get(f"{BASE_URL}/analyze", params={"host": host, "fromCache": "on", "all": "done"}).json()
        status = res.get("status")
    
    print(f"✅ Analysis complete for host: {host} (status: {status})")
    return res

def get_endpoint_data(host, ip):
    """Fetch detailed endpoint data for a host, with timeout + retry."""
    print(f"🌐 Fetching endpoint data for {host} ({ip})...")

    for attempt in range(12):  # Increased to 12 attempts (~3 minutes total)
        try:
            res = requests.get(
                f"{BASE_URL}/getEndpointData",
                params={"host": host, "s": ip, "fromCache": "on"},  # Changed 'ip' to 's'
                timeout=20  # Increased timeout to 20 seconds
            )
            if res.status_code == 441:
                wait_time = 15  # Increased wait time to 15 seconds
                print(f"⚠️ Attempt {attempt+1}/12: endpoint data not ready yet (441). Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue

            res.raise_for_status()
            data = res.json()

            if not data.get("statusMessage"):
                print(f"⚠️ Attempt {attempt+1}/12: incomplete data, retrying in 15s...")
                time.sleep(15)
                continue

            print(f"✅ Got endpoint data on attempt {attempt+1}")
            return data

        except requests.exceptions.Timeout:
            print(f"⏳ Attempt {attempt+1}/12: timed out, retrying in 15s...")
            time.sleep(15)
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching endpoint data (attempt {attempt+1}/12): {e}")
            time.sleep(15)

    print("🚫 Failed to fetch endpoint data after 12 attempts.")
    return {}