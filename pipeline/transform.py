import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def ensure_dict_list(lst, source_name):
    """
    Ensure all items in the list are dicts.
    Wrap strings or other types into a dict with a 'value' field.
    """
    transformed = []
    for i in lst:
        if isinstance(i, dict):
            transformed.append(i)
        else:
            transformed.append({"value": i})
    if not transformed:
        logging.warning(f"No records found for {source_name}.")
    return transformed

def transform_data(raw_data):
    """
    Transform raw Abuse.ch data into MongoDB-ready dictionaries.
    
    raw_data: {
        "urlhaus": {...},
        "malwarebazaar": {...},
        "feodotracker": {...},
        "threatfox": {...}
    }
    """
    logging.info("--------PHASE 2: Starting transformation phase---------")
    transformed = {}

    for source, data in raw_data.items():
        if not data:
            transformed[source] = []
            continue

        if source == "malwarebazaar":
            # Extract relevant fields from MalwareBazaar samples (10+ attributes)
            transformed[source] = [
                {
                    "source": "malwarebazaar",
                    "sha256": s.get("sha256_hash"),
                    "sha3_384": s.get("sha3_384_hash"),
                    "sha1": s.get("sha1_hash"),
                    "md5": s.get("md5_hash"),
                    "file_name": s.get("file_name"),
                    "file_size": s.get("file_size"),
                    "file_type": s.get("file_type"),

                    "first_seen": s.get("first_seen"),
                    "last_seen": s.get("last_seen"),
                    "reporter": s.get("reporter"),
                    "origin_country": s.get("origin_country"),
                    "signature": s.get("signature"),
                    "intelligence": s.get("intelligence", {})
                }
                for s in data.get("data", [])
                if isinstance(s, dict)
            ]
            transformed[source] = ensure_dict_list(transformed[source], "malwarebazaar")

        elif source == "urlhaus":
            # Extract relevant fields from URLHaus URLs
            transformed[source] = [
                {
                    "source": "urlhaus",
                    "url_id": u.get("id"),
                    "urlhaus_reference": u.get("urlhaus_reference"),
                    "url": u.get("url"),
                    "url_status": u.get("url_status"),
                    "host": u.get("host"),
                    "date_added": u.get("date_added"),
                    "threat": u.get("threat"),
                    "blacklists": u.get("blacklists", {}),
                    "reporter": u.get("reporter"),
                    "larted": u.get("larted"),
                    "tags": u.get("tags", [])
                }
                for u in data.get("urls", [])
                if isinstance(u, dict)
            ]
            transformed[source] = ensure_dict_list(transformed[source], "urlhaus")

        elif source == "threatfox":
            # Extract relevant fields from ThreatFox IOCs
            transformed[source] = [
                {
                    "source": "threatfox",
                    "ioc_id": ioc.get("id"),
                    "ioc": ioc.get("ioc"),
                    "threat_type": ioc.get("threat_type"),
                    "threat_type_desc": ioc.get("threat_type_desc"),
                    "ioc_type": ioc.get("ioc_type"),
                    "ioc_type_desc": ioc.get("ioc_type_desc"),
                    "malware": ioc.get("malware"),
                    "malware_printable": ioc.get("malware_printable"),
                    "malware_alias": ioc.get("malware_alias"),
                    "confidence_level": ioc.get("confidence_level"),
                    "first_seen": ioc.get("first_seen"),
                    "last_seen": ioc.get("last_seen"),
                }
                for ioc in data.get("data", [])
                if isinstance(ioc, dict)
            ]
            transformed[source] = ensure_dict_list(transformed[source], "threatfox")


        else:
            # Fallback: ensure the list is dicts
            transformed[source] = ensure_dict_list(data, source)

    logging.info("Transformation phase completed successfully.")
    return transformed
