import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Union

@dataclass
class NormalizedDomain:
    handle: str; name: str; registrar_name: Optional[str]
    creation_date: Optional[str]; expiration_date: Optional[str]; last_update_date: Optional[str]
    status: List[str]; nameservers: List[str]; registrant_name: Optional[str]

@dataclass
class NormalizedIP:
    handle: str; start_address: str; end_address: str; cidr_prefix: Optional[int]
    registration_type: str; country: Optional[str]; creation_date: Optional[str]
    last_update_date: Optional[str]; status: List[str]; organization: Optional[str]

@dataclass
class NormalizedASN:
    handle: str; asn: str; name: Optional[str]; organization: Optional[str]
    country: Optional[str]; creation_date: Optional[str]; last_update_date: Optional[str]; status: List[str]

class RDAPTransformer:
    def __init__(self, output_dir: str = "./rdap_transformed"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def transform_domain_file(self, filepath: str) -> Optional[NormalizedDomain]:
        return self._transform_domain(self._load_json(filepath), filepath)

    def transform_ip_file(self, filepath: str) -> Optional[NormalizedIP]:
        return self._transform_ip(self._load_json(filepath), filepath)

    def transform_asn_file(self, filepath: str) -> Optional[NormalizedASN]:
        return self._transform_asn(self._load_json(filepath), filepath)

    def transform_batch(self, filepaths: List[str]) -> List[Union[NormalizedDomain, NormalizedIP, NormalizedASN]]:
        results = []
        for f in filepaths:
            data = self._load_json(f)
            if not data: continue
            name = Path(f).name
            if 'domain_' in name: results.append(self._transform_domain(data, f))
            elif 'ip_' in name: results.append(self._transform_ip(data, f))
            elif 'autnum_' in name: results.append(self._transform_asn(data, f))
        return [r for r in results if r]

    def _load_json(self, filepath: str) -> Optional[Dict]:
        try: 
            with open(filepath) as f: return json.load(f)
        except: return None

    def _transform_domain(self, data: Dict, _: str) -> NormalizedDomain:
        return NormalizedDomain(
            handle=data.get('handle',''),
            name=data.get('ldhName', data.get('unicodeName','')),
            registrar_name=self._extract_registrar(data),
            creation_date=self._extract_event_date(data,'registration'),
            expiration_date=self._extract_event_date(data,'expiration'),
            last_update_date=self._extract_event_date(data,'last changed'),
            status=[s if isinstance(s,str) else s.get('description','') for s in data.get('status',[])],
            nameservers=[ns.get('ldhName') for ns in data.get('nameservers',[]) if ns.get('ldhName')],
            registrant_name=self._extract_entity_name(data,'registrant')
        )

    def _transform_ip(self, data: Dict, _: str) -> NormalizedIP:
        return NormalizedIP(
            handle=data.get('handle',''),
            start_address=data.get('startAddress',''),
            end_address=data.get('endAddress',''),
            cidr_prefix=int(data.get('cidrPrefix')) if data.get('cidrPrefix') else None,
            registration_type=data.get('type','unknown'),
            country=data.get('country'),
            creation_date=self._extract_event_date(data,'registration'),
            last_update_date=self._extract_event_date(data,'last changed'),
            status=[s if isinstance(s,str) else s.get('description','') for s in data.get('status',[])],
            organization=self._extract_entity_name(data)
        )

    def _transform_asn(self, data: Dict, _: str) -> NormalizedASN:
        return NormalizedASN(
            handle=data.get('handle',''),
            asn=data.get('asn',''),
            name=data.get('name'),
            organization=self._extract_entity_name(data),
            country=data.get('country'),
            creation_date=self._extract_event_date(data,'registration'),
            last_update_date=self._extract_event_date(data,'last changed'),
            status=[s if isinstance(s,str) else s.get('description','') for s in data.get('status',[])]
        )

    def _extract_event_date(self,data,event): 
        for e in data.get('events',[]): 
            if event.lower() in e.get('eventAction','').lower(): return e.get('eventDate')
        return None

    def _extract_registrar(self,data):
        for e in data.get('entities',[]):
            if 'registrar' in e.get('roles',[]):
                return self._parse_vcard_name(e.get('vcardArray',[]))
        return None

    def _extract_entity_name(self,data,role=None):
        for e in data.get('entities',[]):
            if not role or role in e.get('roles',[]):
                return self._parse_vcard_name(e.get('vcardArray',[]))
        return None

    def _parse_vcard_name(self,vcard):
        if not vcard or len(vcard)<2: return None
        for item in vcard:
            if isinstance(item,list) and len(item)>=4 and item[0]=='fn': return item[3]
        return None
