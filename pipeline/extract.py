from endpoints.malware_bazaar_endpoints import AbuseCHConnector
import logging

def extract_data():
    """Extract data from all four Abuse.ch sources."""
    logging.info("--------PHASE 1: Starting extraction phase--------")
    connector = AbuseCHConnector()
    return {
       "urlhaus": connector.get_urlhaus_recent(),
       "malwarebazaar": connector.get_malwarebazaar_recent(),
        "threatfox": connector.get_threatfox_recent(),
    }
