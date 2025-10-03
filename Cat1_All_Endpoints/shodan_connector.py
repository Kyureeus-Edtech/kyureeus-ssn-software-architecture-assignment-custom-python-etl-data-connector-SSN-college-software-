import os
import time
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
from typing import Any, Dict, Callable, Tuple

load_dotenv()

SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME_shodan", "shodan_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME_shodan", "shodan_results")
RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", "1.1"))
BASE = "https://api.shodan.io"

class ShodanClient:
    def __init__(self, api_key=None, rate_delay=RATE_LIMIT_DELAY):
        self.api_key = api_key or SHODAN_API_KEY
        if not self.api_key:
            raise ValueError("SHODAN_API_KEY required")
        self.rate_delay = rate_delay
        self.session = requests.Session()
        self.session.params = {"key": self.api_key}

    def _request(self, method: str, path: str, params: Dict = None, json_body: Dict = None, data: Dict = None):
        url = BASE + path
        r = self.session.request(method=method, url=url, params=params, json=json_body, data=data, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"{r.status_code} {r.text}")
        time.sleep(self.rate_delay)
        try:
            return r.json()
        except ValueError:
            return {"raw_text": r.text}

    def host(self, ip: str): return self._request("GET", f"/shodan/host/{ip}")
    def host_count(self, query: str): return self._request("GET", "/shodan/host/count", params={"query": query})
    def host_search(self, query: str, page: int = 1): return self._request("GET", "/shodan/host/search", params={"query": query, "page": page})
    def host_search_facets(self, query: str, facets: str): return self._request("GET", "/shodan/host/search/facets", params={"query": query, "facets": facets})
    def host_search_filters(self): return self._request("GET", "/shodan/host/search/filters")
    def host_search_tokens(self, query: str): return self._request("GET", "/shodan/host/search/tokens", params={"query": query})
    def ports(self): return self._request("GET", "/shodan/ports")
    def protocols(self): return self._request("GET", "/shodan/protocols")
    def scan_list(self): return self._request("GET", "/shodan/scans")
    def scan_create(self, ips: list): return self._request("POST", "/shodan/scan", json_body={"ips": ",".join(ips)})
    def scan_get(self, scan_id: str): return self._request("GET", f"/shodan/scan/{scan_id}")
    def alert_create(self, name: str, query: str): return self._request("POST", "/shodan/alert", json_body={"name": name, "query": query})
    def alert_info(self): return self._request("GET", "/shodan/alert/info")
    def alert_id_info(self, alert_id: str): return self._request("GET", f"/shodan/alert/{alert_id}/info")
    def alert_triggers(self): return self._request("GET", "/shodan/alert/triggers")
    def alert_trigger_enable(self, alert_id: str, trigger: str): return self._request("PUT", f"/shodan/alert/{alert_id}/trigger/{trigger}")
    def alert_trigger_disable(self, alert_id: str, trigger: str): return self._request("DELETE", f"/shodan/alert/{alert_id}/trigger/{trigger}")
    def notifier_list(self): return self._request("GET", "/notifier")
    def notifier_providers(self): return self._request("GET", "/notifier/provider")
    def query_list(self): return self._request("GET", "/shodan/query")
    def query_search(self, query: str): return self._request("GET", "/shodan/query/search", params={"query": query})
    def query_tags(self): return self._request("GET", "/shodan/query/tags")
    def data_list(self): return self._request("GET", "/shodan/data")
    def dns_domain(self, domain: str): return self._request("GET", f"/dns/domain/{domain}")
    def tools_httpheaders(self, host: str): return self._request("GET", "/tools/httpheaders", params={"host": host})
    def tools_myip(self): return self._request("GET", "/tools/myip")
    def api_info(self): return self._request("GET", "/api-info")
    def account_profile(self): return self._request("GET", "/account/profile")

MAX_INT64 = 2**63 - 1
MIN_INT64 = -2**63

def sanitize_value(v: Any) -> Any:
    if isinstance(v, int):
        if v > MAX_INT64 or v < MIN_INT64:
            return str(v)
        return v
    if isinstance(v, dict):
        return {k: sanitize_value(val) for k, val in v.items()}
    if isinstance(v, list):
        return [sanitize_value(i) for i in v]
    return v

def sanitize_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    return {k: sanitize_value(v) for k, v in doc.items()}

def store_result(collection, endpoint_name: str, params: Dict[str, Any], result: Any):
    doc = {
        "endpoint": endpoint_name,
        "params": params,
        "result": sanitize_value(result),
        "fetched_at": datetime.utcnow()
    }
    collection.insert_one(doc)

def main():
    client = ShodanClient()
    mongo = MongoClient(MONGO_URI)
    coll = mongo[DB_NAME][COLLECTION_NAME]

    state = {}

    endpoints: Tuple[Tuple[str, Callable[[], Any], Dict[str, Any]], ...] = (
        ("host", lambda: client.host("8.8.8.8"), {"ip": "8.8.8.8"}),
        ("host_count", lambda: client.host_count("apache"), {"query": "apache"}),
        ("host_search_facets", lambda: client.host_search_facets("apache", "org,product"), {"query": "apache", "facets": "org,product"}),
        ("host_search_filters", lambda: client.host_search_filters(), {}),
        ("host_search_tokens", lambda: client.host_search_tokens("apache"), {"query": "apache"}),
        ("ports", lambda: client.ports(), {}),
        ("protocols", lambda: client.protocols(), {}),
        ("scans", lambda: client.scan_list(), {}),
        ("scan_get", lambda: (client.scan_get(state.get("first_scan_id")) if state.get("first_scan_id") else {"note": "no_scan_id_available"}), {"scan_id": "derived from scans"}),
        ("scan_create", lambda: client.scan_create(["8.8.8.8"]) , {"ips": ["8.8.8.8"]}),
        ("alert_info", lambda: client.alert_info(), {}),
        ("alert_triggers", lambda: client.alert_triggers(), {}),
        ("notifier_list", lambda: client.notifier_list(), {}),
        ("notifier_providers", lambda: client.notifier_providers(), {}),
        ("query_list", lambda: client.query_list(), {}),
        ("query_search", lambda: client.query_search("nginx"), {"query": "nginx"}),
        ("query_tags", lambda: client.query_tags(), {}),
        ("dns_domain", lambda: client.dns_domain("example.com"), {"domain": "example.com"}),
        ("tools_httpheaders", lambda: client.tools_httpheaders("example.com"), {"host": "example.com"}),
        ("tools_myip", lambda: client.tools_myip(), {}),
        ("api_info", lambda: client.api_info(), {}),
        ("account_profile", lambda: client.account_profile(), {})
    )

    for name, func, params in endpoints:
        try:
            res = func()
            if name == "scans" and isinstance(res, dict):
                items = res.get("scans") or res.get("matches") or res.get("data") or res.get("results") or []
                if items and isinstance(items, list):
                    first = items[0]
                    scan_id = first.get("id") or first.get("scan_id") or first.get("query") or None
                    if scan_id:
                        state["first_scan_id"] = scan_id
            if name == "scan_create" and isinstance(res, dict):
                created = res.get("id") or res.get("scan_id") or res.get("query")
                if created:
                    state["last_created_scan_id"] = created
            store_result(coll, name, params, res)
            print(f"{name} done (mongodb stored)")
        except Exception as e:
            err_doc = {"endpoint": name, "params": params, "error": str(e), "fetched_at": datetime.utcnow()}
            coll.insert_one(sanitize_doc(err_doc))
            print(f"{name} failed ({e})")

    mongo.close()

if __name__ == "__main__":
    main()
