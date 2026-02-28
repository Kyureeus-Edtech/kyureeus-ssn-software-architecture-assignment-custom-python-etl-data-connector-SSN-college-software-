"""
Generate Sample CERT.at Threat Intelligence CSV Files
Creates realistic sample data for testing the CSV pipeline
"""

import csv
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

# CERT.at CSV Format Fields
CSV_HEADERS = [
    'time.source', 'source.ip', 'protocol.transport', 'source.port',
    'protocol.application', 'source.fqdn', 'source.local_hostname',
    'source.local_ip', 'source.url', 'source.asn', 'source.geolocation.cc',
    'source.geolocation.city', 'classification.taxonomy', 'classification.type',
    'classification.identifier', 'destination.ip', 'destination.port',
    'destination.fqdn', 'destination.url', 'malware.name', 'malware.hash.md5',
    'malware.hash.sha256', 'event_description.url', 'event_description.text',
    'feed.name', 'feed.accuracy', 'feed.provider', 'feed.documentation'
]


def random_ip():
    """Generate random IP address"""
    return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"


def random_timestamp():
    """Generate random timestamp in last 7 days"""
    now = datetime.utcnow()
    days_ago = random.randint(0, 7)
    timestamp = now - timedelta(days=days_ago, hours=random.randint(0, 23))
    return timestamp.strftime('%Y-%m-%dT%H:%M:%S+00:00')


def random_hash(length=32):
    """Generate random hex hash"""
    return ''.join(random.choices('0123456789abcdef', k=length))


def generate_malware_infections(output_dir: Path, count: int = 30):
    """Generate malware infections feed"""
    print(f"Generating malware infections feed ({count} records)...")
    
    malware_families = [
        'Emotet', 'TrickBot', 'Dridex', 'Qakbot', 'IcedID', 
        'BazarLoader', 'Cobalt Strike', 'Ryuk', 'LockBit', 'BlackCat'
    ]
    countries = ['AT', 'DE', 'CH', 'US', 'GB', 'FR', 'NL', 'IT', 'ES', 'PL']
    cities = [
        'Vienna', 'Berlin', 'Zurich', 'London', 'Paris', 
        'Amsterdam', 'Rome', 'Madrid', 'Warsaw', 'New York'
    ]
    
    records = []
    for i in range(count):
        malware = random.choice(malware_families)
        records.append({
            'time.source': random_timestamp(),
            'source.ip': random_ip(),
            'protocol.transport': 'tcp',
            'source.port': str(random.randint(49152, 65535)),
            'protocol.application': random.choice(['http', 'https', 'smtp']),
            'source.fqdn': f"host{i}.example{random.randint(1,5)}.com",
            'source.local_hostname': '',
            'source.local_ip': '',
            'source.url': '',
            'source.asn': str(random.randint(1000, 65000)),
            'source.geolocation.cc': random.choice(countries),
            'source.geolocation.city': random.choice(cities),
            'classification.taxonomy': 'malicious-code',
            'classification.type': random.choice(['infected-system', 'c2-server']),
            'classification.identifier': f'{malware.lower()}-infection',
            'destination.ip': random_ip(),
            'destination.port': random.choice(['80', '443', '8080']),
            'destination.fqdn': f"c2-{random.randint(1,100)}.malicious{random.randint(1,3)}.com",
            'destination.url': '',
            'malware.name': malware,
            'malware.hash.md5': random_hash(32),
            'malware.hash.sha256': random_hash(64),
            'event_description.url': 'https://www.cert.at/malware',
            'event_description.text': f'{malware} infection detected on system',
            'feed.name': 'CERT.at Malware Feed',
            'feed.accuracy': str(random.randint(90, 99)),
            'feed.provider': 'CERT.at',
            'feed.documentation': 'https://www.cert.at/en/services/data/'
        })
    
    filename = output_dir / 'certat_malware_infections.csv'
    write_csv(filename, records)
    print(f"✓ Created {filename} with {len(records)} records")


def generate_vulnerable_systems(output_dir: Path, count: int = 25):
    """Generate vulnerable systems feed"""
    print(f"Generating vulnerable systems feed ({count} records)...")
    
    vulnerabilities = [
        ('Exposed RDP', 'rdp', 3389),
        ('Vulnerable SSH', 'ssh', 22),
        ('Open MongoDB', 'mongodb', 27017),
        ('Weak SMB', 'smb', 445),
        ('Unpatched Apache', 'http', 80),
        ('Exposed MySQL', 'mysql', 3306),
        ('Vulnerable IIS', 'http', 8080),
        ('Open Elasticsearch', 'elasticsearch', 9200),
        ('Exposed Redis', 'redis', 6379),
        ('Vulnerable Tomcat', 'http', 8080)
    ]
    
    records = []
    for i in range(count):
        vuln_name, service, port = random.choice(vulnerabilities)
        records.append({
            'time.source': random_timestamp(),
            'source.ip': random_ip(),
            'protocol.transport': 'tcp',
            'source.port': str(port),
            'protocol.application': service,
            'source.fqdn': f"server{i}.company{random.randint(1,5)}.com",
            'source.local_hostname': '',
            'source.local_ip': '',
            'source.url': '',
            'source.asn': str(random.randint(1000, 65000)),
            'source.geolocation.cc': random.choice(['AT', 'DE', 'CH', 'NL']),
            'source.geolocation.city': random.choice(['Vienna', 'Berlin', 'Zurich', 'Amsterdam']),
            'classification.taxonomy': 'vulnerable',
            'classification.type': 'vulnerable-service',
            'classification.identifier': f'vulnerable-{service}',
            'destination.ip': '',
            'destination.port': '',
            'destination.fqdn': '',
            'destination.url': '',
            'malware.name': '',
            'malware.hash.md5': '',
            'malware.hash.sha256': '',
            'event_description.url': 'https://www.cert.at/vulnerable',
            'event_description.text': vuln_name,
            'feed.name': 'CERT.at Vulnerable Systems',
            'feed.accuracy': str(random.randint(95, 99)),
            'feed.provider': 'CERT.at',
            'feed.documentation': 'https://www.cert.at/en/services/data/'
        })
    
    filename = output_dir / 'certat_vulnerable_systems.csv'
    write_csv(filename, records)
    print(f"✓ Created {filename} with {len(records)} records")


def generate_brute_force_attacks(output_dir: Path, count: int = 20):
    """Generate brute force attacks feed"""
    print(f"Generating brute force attacks feed ({count} records)...")
    
    services = [
        ('ssh', 22),
        ('rdp', 3389),
        ('ftp', 21),
        ('smtp', 25),
        ('http', 80),
        ('https', 443)
    ]
    attacker_countries = ['CN', 'RU', 'KP', 'IR', 'BR', 'VN', 'IN']
    attacker_cities = ['Beijing', 'Moscow', 'Tehran', 'Mumbai', 'São Paulo', 'Hanoi']
    
    records = []
    for i in range(count):
        service, port = random.choice(services)
        records.append({
            'time.source': random_timestamp(),
            'source.ip': random_ip(),
            'protocol.transport': 'tcp',
            'source.port': str(random.randint(49152, 65535)),
            'protocol.application': service,
            'source.fqdn': '',
            'source.local_hostname': '',
            'source.local_ip': '',
            'source.url': '',
            'source.asn': str(random.randint(1000, 65000)),
            'source.geolocation.cc': random.choice(attacker_countries),
            'source.geolocation.city': random.choice(attacker_cities),
            'classification.taxonomy': 'intrusion-attempts',
            'classification.type': 'brute-force',
            'classification.identifier': f'brute-force-{service}',
            'destination.ip': random_ip(),
            'destination.port': str(port),
            'destination.fqdn': f"target{i}.example{random.randint(1,3)}.com",
            'destination.url': '',
            'malware.name': '',
            'malware.hash.md5': '',
            'malware.hash.sha256': '',
            'event_description.url': 'https://www.cert.at/brute-force',
            'event_description.text': f'Brute force attack on {service}',
            'feed.name': 'CERT.at Brute Force Feed',
            'feed.accuracy': str(random.randint(88, 96)),
            'feed.provider': 'CERT.at',
            'feed.documentation': 'https://www.cert.at/en/services/data/'
        })
    
    filename = output_dir / 'certat_brute_force_attacks.csv'
    write_csv(filename, records)
    print(f"✓ Created {filename} with {len(records)} records")


def write_csv(filename: Path, records: list):
    """Write records to CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(records)


def main():
    """Main function"""
    print("=" * 70)
    print("CERT.at Threat Intelligence Sample Data Generator")
    print("=" * 70)
    print()
    
    # Create data directory
    output_dir = Path('data')
    output_dir.mkdir(exist_ok=True)
    print(f"Output directory: {output_dir.absolute()}\n")
    
    # Generate feeds
    generate_malware_infections(output_dir, count=30)
    generate_vulnerable_systems(output_dir, count=25)
    generate_brute_force_attacks(output_dir, count=20)
    
    print()
    print("=" * 70)
    print("✓ Sample data generation complete!")
    print()
    print("Generated files:")
    print("  1. certat_malware_infections.csv (30 records)")
    print("  2. certat_vulnerable_systems.csv (25 records)")
    print("  3. certat_brute_force_attacks.csv (20 records)")
    print()
    print("Total: 75 threat intelligence records")
    print()
    print("Next steps:")
    print("  1. Review the generated CSV files in the 'data/' directory")
    print("  2. Configure your .env file with MongoDB settings")
    print("  3. Run the ETL pipeline: python threat_intel_pipeline/etl_orchestrator.py")
    print("=" * 70)


if __name__ == "__main__":
    main()