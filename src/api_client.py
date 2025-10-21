import requests
from config import API_BASE_URL
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_ip_info(ip_address: str) -> dict | None:
    """
    Fetches IP subnet information from the /ip/ endpoint.
    This is the only working endpoint found.
    """
    url = f"{API_BASE_URL}/ip/{ip_address}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        logger.info(f"Successfully fetched data for IP: {ip_address}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data for IP {ip_address}: {e}")
        return None