import requests, json, time
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional

RDAP_BASE_URL = "https://rdap.org"

class RDAPExtractor:
    def __init__(self, base_url: str = RDAP_BASE_URL, output_dir: str = "./rdap_raw"):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'RDAP-ETL-Pipeline/1.0'})

    def extract_domain(self, domain: str) -> Optional[str]:
        return self._fetch_and_save('domain', domain)

    def extract_ip(self, ip_address: str) -> Optional[str]:
        return self._fetch_and_save('ip', ip_address)

    def extract_asn(self, asn: str) -> Optional[str]:
        return self._fetch_and_save('autnum', asn)

    def extract_batch(self, resources: List[Dict]) -> List[str]:
        files = []
        for r in resources:
            f = self._fetch_and_save(r['type'], r['identifier'])
            if f: files.append(f)
        return files

    def _fetch_and_save(self, rtype: str, identifier: str) -> Optional[str]:
        try:
            resp = self.session.get(f"{self.base_url}/{rtype}/{identifier}", timeout=10)
            if resp.status_code == 200:
                filepath = self.output_dir / f"{rtype}_{identifier.replace('/', '_')}_{self.timestamp}.json"
                with open(filepath, 'w') as f: json.dump(resp.json(), f, indent=2)
                return str(filepath)
        except: return None
