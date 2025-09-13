import requests
import time

def fetch_breached_accounts(email, api_key):
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
    headers = {
        'hibp-api-key': api_key,
        'User-Agent': 'SSN-ETL-Assignment'
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return []  # No breach found
        elif response.status_code == 429:
            print("Rate limit hit, sleeping for 2 seconds...")
            time.sleep(2)
            return fetch_breached_accounts(email, api_key)
        else:
            print(f"Unexpected status code {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

