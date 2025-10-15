"""
CSV Transformer Module
Transforms and enriches CERT.at threat intelligence data
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class CSVTransformer:
    """Transforms and normalizes CSV threat intelligence data"""
    
    # Severity mapping based on threat taxonomy
    SEVERITY_RULES = {
        'malicious-code': {
            'default': 'high',
            'infected-system': 'high',
            'ransomware': 'critical',
            'backdoor': 'critical',
            'c2-server': 'critical'
        },
        'intrusion-attempts': {
            'default': 'medium',
            'brute-force': 'medium',
            'exploit': 'high',
            'ids-alert': 'medium'
        },
        'vulnerable': {
            'default': 'low',
            'vulnerable-service': 'low',
            'vulnerable-system': 'low',
            'exposed-service': 'medium'
        },
        'information-content-security': {
            'default': 'medium',
            'dropzone': 'high',
            'unauthorised-use': 'medium'
        }
    }
    
    def __init__(self, max_records: int = 100):
        """
        Initialize transformer
        
        Args:
            max_records: Maximum number of records to process per feed
        """
        self.max_records = max_records
        logger.info(f"CSV Transformer initialized with max_records={max_records}")
    
    def _calculate_severity(self, record: Dict) -> str:
        """
        Calculate threat severity based on classification
        
        Args:
            record: Raw threat record
            
        Returns:
            Severity level (critical, high, medium, low)
        """
        taxonomy = (record.get('classification.taxonomy') or '').lower()
        threat_type = (record.get('classification.type') or '').lower()
        
        # Get severity rules for this taxonomy
        if taxonomy in self.SEVERITY_RULES:
            rules = self.SEVERITY_RULES[taxonomy]
            
            # Check for specific threat type
            for key, severity in rules.items():
                if key in threat_type:
                    return severity
            
            # Return default for taxonomy
            return rules['default']
        
        # Default severity
        return 'medium'
    
    def _generate_record_id(self, record: Dict) -> str:
        """
        Generate unique ID for threat record
        
        Args:
            record: Threat record
            
        Returns:
            Unique record identifier
        """
        # Create ID from key fields
        id_components = [
            record.get('time.source', ''),
            record.get('source.ip', ''),
            record.get('classification.identifier', ''),
            record.get('feed.name', '')
        ]
        
        id_string = '|'.join(str(c) for c in id_components)
        return hashlib.sha256(id_string.encode()).hexdigest()[:16]
    
    def _enrich_geolocation(self, record: Dict) -> Dict:
        """
        Enrich geolocation data
        
        Args:
            record: Record with geolocation data
            
        Returns:
            Enriched geolocation dictionary
        """
        return {
            'country_code': record.get('source.geolocation.cc'),
            'city': record.get('source.geolocation.city'),
            'asn': record.get('source.asn')
        }
    
    def _extract_malware_info(self, record: Dict) -> Optional[Dict]:
        """
        Extract malware information
        
        Args:
            record: Threat record
            
        Returns:
            Malware information dictionary or None
        """
        malware_name = record.get('malware.name')
        
        if not malware_name:
            return None
        
        return {
            'name': malware_name,
            'md5': record.get('malware.hash.md5'),
            'sha256': record.get('malware.hash.sha256')
        }
    
    def normalize_record(self, record: Dict, feed_name: str) -> Dict:
        """
        Normalize a single threat record
        
        Args:
            record: Raw CSV record
            feed_name: Name of the source feed
            
        Returns:
            Normalized and enriched record
        """
        # Generate unique ID
        record_id = self._generate_record_id(record)
        
        # Calculate severity
        severity = self._calculate_severity(record)
        
        # Normalize record
        normalized = {
            # Identifiers
            'record_id': record_id,
            'feed_source': feed_name,
            
            # Temporal information
            'timestamp': record.get('time.source'),
            
            # Source (infected/vulnerable host)
            'source': {
                'ip': record.get('source.ip'),
                'port': record.get('source.port'),
                'fqdn': record.get('source.fqdn'),
                'url': record.get('source.url'),
                'geolocation': self._enrich_geolocation(record)
            },
            
            # Destination (C2 server, target)
            'destination': {
                'ip': record.get('destination.ip'),
                'port': record.get('destination.port'),
                'fqdn': record.get('destination.fqdn'),
                'url': record.get('destination.url')
            },
            
            # Protocol information
            'protocol': {
                'transport': record.get('protocol.transport'),
                'application': record.get('protocol.application')
            },
            
            # Classification (ENISA Taxonomy)
            'classification': {
                'taxonomy': record.get('classification.taxonomy'),
                'type': record.get('classification.type'),
                'identifier': record.get('classification.identifier')
            },
            
            # Malware information
            'malware': self._extract_malware_info(record),
            
            # Threat assessment
            'severity': severity,
            
            # Event description
            'description': {
                'text': record.get('event_description.text'),
                'url': record.get('event_description.url')
            },
            
            # Feed metadata
            'feed_metadata': {
                'name': record.get('feed.name'),
                'provider': record.get('feed.provider', 'CERT.at'),
                'accuracy': record.get('feed.accuracy'),
                'documentation': record.get('feed.documentation')
            },
            
            # Processing metadata
            'processed_at': datetime.utcnow().isoformat(),
            'data_type': 'csv_feed'
        }
        
        return normalized
    
    def transform_feed(self, feed_data: Dict) -> Optional[Dict]:
        """
        Transform a single feed's data
        
        Args:
            feed_data: Extracted feed data
            
        Returns:
            Transformed feed data or None
        """
        if not feed_data or 'records' not in feed_data:
            logger.warning(f"No valid data to transform")
            return None
        
        feed_name = feed_data['feed_name']
        records = feed_data['records']
        
        # Limit records
        records = records[:self.max_records]
        
        logger.info(f"Transforming {len(records)} records from {feed_name}")
        
        transformed_records = []
        errors = 0
        
        for record in records:
            try:
                normalized = self.normalize_record(record, feed_name)
                transformed_records.append(normalized)
            except Exception as e:
                logger.error(f"Error transforming record: {e}")
                errors += 1
                continue
        
        logger.info(f"Successfully transformed {len(transformed_records)} records from {feed_name} ({errors} errors)")
        
        return {
            'feed_name': feed_name,
            'original_count': feed_data['record_count'],
            'transformed_count': len(transformed_records),
            'error_count': errors,
            'records': transformed_records,
            'transformed_at': datetime.utcnow().isoformat()
        }
    
    def transform_all_feeds(self, feeds_data: Dict[str, Optional[Dict]]) -> Dict[str, Optional[Dict]]:
        """
        Transform all feeds data
        
        Args:
            feeds_data: Dictionary of extracted feed data
            
        Returns:
            Dictionary of transformed feed data
        """
        logger.info("Starting transformation of all CSV feeds")
        results = {}
        
        for feed_name, feed_data in feeds_data.items():
            if feed_data is not None:
                results[feed_name] = self.transform_feed(feed_data)
            else:
                logger.warning(f"Skipping transformation for {feed_name} (no data)")
                results[feed_name] = None
        
        successful = sum(1 for v in results.values() if v is not None)
        total_records = sum(v['transformed_count'] for v in results.values() if v)
        
        logger.info(f"CSV transformation complete: {successful} feeds, {total_records} total records")
        
        return results
    
    def get_severity_stats(self, transformed_data: Dict) -> Dict[str, int]:
        """
        Get severity distribution statistics
        
        Args:
            transformed_data: Transformed feed data
            
        Returns:
            Dictionary with severity counts
        """
        stats = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for feed_data in transformed_data.values():
            if feed_data and 'records' in feed_data:
                for record in feed_data['records']:
                    severity = record.get('severity', 'medium')
                    stats[severity] = stats.get(severity, 0) + 1
        
        return stats