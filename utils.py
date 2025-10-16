# utils.py
import socket
import ipaddress
from dateutil import tz, parser
from datetime import datetime
import dns.resolver

def is_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except Exception:
        return False

def now_utc_iso():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def parse_time_to_utc_iso(timestr: str):
    try:
        dt = parser.parse(timestr)
        return dt.astimezone(tz.tzutc()).replace(microsecond=0).isoformat()
    except Exception:
        return None

def resolve_domain(domain: str, prefer_ipv6=False, timeout=3):
    answers = []
    try:
        resolver = dns.resolver.Resolver()
        resolver.lifetime = timeout
        for rtype in (["AAAA", "A"] if prefer_ipv6 else ["A", "AAAA"]):
            try:
                resp = resolver.resolve(domain, rtype)
                answers += [str(r.address) for r in resp]
            except Exception:
                continue
    except Exception:
        return []
    return answers
