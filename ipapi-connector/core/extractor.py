import requests
from config import settings
from utils.logger import logger

def extract_single(ip):
    """Fetch single IP data."""
    try:
        res = requests.get(f"{settings.BASE_URL}{ip}", timeout=settings.TIMEOUT)
        res.raise_for_status()
        logger.info(f"Extracted single IP data for {ip}")
        return res.json()
    except Exception as e:
        logger.error(f"Error extracting single IP: {e}")
        return None

def extract_batch(ip_list):
    """Fetch multiple IPs via batch API."""
    try:
        res = requests.post(settings.BATCH_URL, json=ip_list, timeout=settings.TIMEOUT)
        res.raise_for_status()
        logger.info(f"Extracted batch IP data for {len(ip_list)} IPs")
        return res.json()
    except Exception as e:
        logger.error(f"Error extracting batch: {e}")
        return []

def extract_custom(ip, fields="status,country,city,lat,lon,isp,query", lang="en"):
    """Fetch IP data with custom fields and language."""
    try:
        params = {"fields": fields, "lang": lang}
        res = requests.get(f"{settings.BASE_URL}{ip}", params=params, timeout=settings.TIMEOUT)
        res.raise_for_status()
        logger.info(f"Extracted custom IP data for {ip}")
        return res.json()
    except Exception as e:
        logger.error(f"Error extracting custom IP: {e}")
        return None
