from datetime import datetime
import ipaddress
import logging

logger = logging.getLogger(__name__)

def transform_ip_data(raw_data: dict) -> dict | None:
    """
    Transforms raw IP SUBNET data from the /ip/ endpoint.
    """
    # 1. Get the original data
    subnet_info = raw_data.get('address', {})
    
    # 2. VALIDATION
    ip_address_str = subnet_info.get('network_address')
    if not ip_address_str:
        # Try 'ip_address' as a fallback
        ip_address_str = subnet_info.get('ip_address')
        if not ip_address_str:
            logger.warning(f"Skipping record. Raw data missing 'address.network_address' key. Data: {raw_data}")
            return None # Skip this bad record

    # 3. Create a "transformed" record
    transformed_record = {
        "ip_address": ip_address_str, # The base IP of the network
        "cidr_notation": subnet_info.get('cidr_notation'),
        "subnet_mask": subnet_info.get('subnet_mask'),
        "wildcard_mask": subnet_info.get('wildcard_mask'),
        "broadcast_address": subnet_info.get('broadcast_address'),
        "assignable_hosts": subnet_info.get('assignable_hosts'),
        "first_assignable_host": subnet_info.get('first_assignable_host'),
        "last_assignable_host": subnet_info.get('last_assignable_host'),
        "is_private": ipaddress.ip_address(ip_address_str).is_private,
        "last_processed_utc": datetime.utcnow()
    }
    return transformed_record