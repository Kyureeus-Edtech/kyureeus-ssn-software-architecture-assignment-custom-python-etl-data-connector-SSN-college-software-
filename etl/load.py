import json
from pathlib import Path
from dataclasses import asdict
from typing import List, Union, Dict
from pymongo import MongoClient
from datetime import datetime, timezone

class RDAPLoader:
    def __init__(self, output_dir: str = "./rdap_loaded", mongo_uri: str = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.mongo = MongoClient(mongo_uri).rdap if mongo_uri else None

    def load_to_json(self, data: Union[Dict,List], filename: str):
        if hasattr(data,'__dataclass_fields__'): data = asdict(data)
        elif isinstance(data,list) and data and hasattr(data[0],'__dataclass_fields__'):
            data = [asdict(d) for d in data]
        with open(self.output_dir/filename,'w') as f: json.dump(data,f,indent=2)

    def load_to_mongo(self, data: List[Dict], collection: str):
        if not self.mongo: return
        if data and hasattr(data[0],'__dataclass_fields__'): data = [asdict(d) for d in data]
        self.mongo[collection].insert_many(data)

class RDAPPipeline:
    def __init__(self, load_dir:str="./rdap_loaded"):
        self.loader = RDAPLoader(load_dir)

    def run(self, transformed_data: List, format:str='json'):
        domains = [d for d in transformed_data if hasattr(d,'nameservers')]
        ips = [d for d in transformed_data if hasattr(d,'cidr_prefix') and not hasattr(d,'asn')]
        asns = [d for d in transformed_data if hasattr(d,'asn')]

        ts = self.loader.timestamp
        if domains: self.loader.load_to_json(domains,f"domains_{ts}.json")
        if ips: self.loader.load_to_json(ips,f"ips_{ts}.json")
        if asns: self.loader.load_to_json(asns,f"asns_{ts}.json")
