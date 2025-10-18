# connectors/abusech_api.py
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AbuseCHConnector:
    """Handles connections to abuse.ch project APIs."""
    def __init__(self, api_key: str):
        if not api_key or api_key == "YOUR_API_KEY_HERE":
            raise ValueError("API Key is missing. Please check your .env file.")
        self.headers = {'Auth-Key': api_key}

    def get_urlhaus_recent(self):
        """Fetches recent URL submissions from URLhaus."""
        try:
            logging.info("Extracting recent URLs from URLhaus...")
            # Note: API key is now sent in the headers for GET requests too
            response = requests.get("https://urlhaus-api.abuse.ch/v1/urls/recent/", headers=self.headers)
            response.raise_for_status()
            logging.info("Successfully extracted data from URLhaus.")
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Failed to fetch data from URLhaus: {e}")
            return None

    def get_malwarebazaar_recent(self):
        """Fetches recent malware samples from MalwareBazaar."""
        try:
            logging.info("Extracting recent samples from MalwareBazaar...")
            data = {'query': 'get_recent', 'selector': '100'}
            # The API key header is now included in this POST request
            response = requests.post("https://mb-api.abuse.ch/api/v1/", data=data, headers=self.headers)
            response.raise_for_status()
            logging.info("Successfully extracted data from MalwareBazaar.")
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Failed to fetch data from MalwareBazaar: {e}")
            return None