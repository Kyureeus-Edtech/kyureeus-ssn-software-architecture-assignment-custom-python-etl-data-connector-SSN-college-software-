# transformer.py
from utils import is_ip, resolve_domain, now_utc_iso
import ipaddress, re
from typing import Dict, Any, Optional

def normalize_ip_field(val: Optional[str]):
    if not val:
        return None
    try:
        return str(ipaddress.ip_address(val))
    except Exception:
        return None

def to_geojson(lat, lon):
    try:
        return {"type": "Point", "coordinates": [float(lon), float(lat)]}
    except Exception:
        return None

ASN_RE = re.compile(r"AS(\d+)\s+(.*)", re.IGNORECASE)
def parse_asn(as_str: Optional[str]):
    if not as_str:
        return {}
    m = ASN_RE.match(as_str)
    if m:
        return {"asn": int(m.group(1)), "asn_org": m.group(2).strip()}
    return {"asn_raw": as_str}

def transform_raw_ipapi(record: Dict[str, Any], query: Optional[str] = None) -> Dict[str, Any]:
    doc = {}
    fields = [
        "query", "status", "country", "countryCode", "region",
        "regionName", "city", "zip", "lat", "lon", "timezone",
        "isp", "org", "as", "reverse", "mobile", "proxy", "hosting", "message"
    ]
    for f in fields:
        if f in record:
            doc[f] = record[f]

    doc["ip"] = normalize_ip_field(record.get("query") or query)
    doc["query_original"] = query or record.get("query")
    doc["location"] = to_geojson(record.get("lat"), record.get("lon"))
    doc["asn_parsed"] = parse_asn(record.get("as"))

    try:
        if doc.get("ip"):
            ipobj = ipaddress.ip_address(doc["ip"])
            doc["is_private"] = any([
                ipobj.is_private, ipobj.is_reserved,
                ipobj.is_loopback, ipobj.is_link_local
            ])
    except Exception:
        doc["is_private"] = None

    if query and not is_ip(query):
        doc["resolved_ips"] = resolve_domain(query)

    doc["meta"] = {"source": "ip-api.com", "fetched_at": now_utc_iso()}
    return {k: v for k, v in doc.items() if v is not None}
