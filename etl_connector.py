import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone
import time
import logging
from collections import defaultdict
import hashlib

# Configuration
TEST_MODE = True
NUM_TO_TEST = 10

# Setup
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# API Configuration
IPSTACK_BASE_URL = "http://api.ipstack.com"
IPSTACK_API_KEY = os.getenv("IPSTACK_API_KEY")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "geolocation_db")
MONGO_COLLECTION_NAME = "transformed_geo_data"

SAMPLE_IPS = [
    "8.8.8.8", # USA - Google DNS (Low risk)
    "142.250.191.206", # USA - Google (Low risk)
    "186.227.156.10", # Brazil (Medium risk)
    "190.216.231.10", # Venezuela (High risk - economic crisis)
    "5.44.168.210", # Germany (Low risk)
    "95.142.107.181", # Russia (Medium-High risk - geopolitical)
    "87.120.37.50", # Bulgaria (Medium risk)
    "150.129.28.64", # India (Medium risk)
    "14.1.44.138", # Japan (Low risk)
    "122.10.127.50", # Hong Kong (Medium risk)
    "196.3.132.10", # South Africa (Medium risk)
    "197.155.237.10" # Egypt (Medium-High risk)
]

def calculate_geographic_risk_profile(geo_data):
    risk_factors = {}
    continent_risk = {
        "North America": 3, "Europe": 4, "Asia": 6, 
        "South America": 7, "Africa": 8, "Oceania": 4, "Antarctica": 2
    }
    developed_countries = ["United States", "Canada", "Germany", "United Kingdom", "Japan", 
                          "Australia", "France", "South Korea", "Singapore", "Switzerland",
                          "Netherlands", "New Zealand", "Sweden", "Norway", "Denmark",
                          "Finland", "Austria", "Belgium", "Ireland", "Luxembourg"]
    developing_countries = ["China", "India", "Brazil", "Russia", "Mexico", "Indonesia", 
                           "South Africa", "Thailand", "Vietnam", "Philippines", "Egypt",
                           "Nigeria", "Pakistan", "Bangladesh", "Turkey"]
    high_risk_countries = ["Venezuela", "Ukraine", "Syria", "Yemen", "Afghanistan", 
                          "Somalia", "North Korea", "Myanmar", "Sudan", "Libya"]
    continent = geo_data.get('continent_name', 'Unknown')
    country = geo_data.get('country_name', 'Unknown')
    risk_factors['continent_risk_score'] = continent_risk.get(continent, 6)
    
    # economic development factor with differentiation
    if country in high_risk_countries:
        risk_factors['development_tier'] = "High Risk"
        risk_factors['economic_factor'] = risk_factors['continent_risk_score'] * 1.8
    elif country in developed_countries:
        risk_factors['development_tier'] = "Developed"
        risk_factors['economic_factor'] = risk_factors['continent_risk_score'] * 0.6
    elif country in developing_countries:
        risk_factors['development_tier'] = "Developing"
        risk_factors['economic_factor'] = risk_factors['continent_risk_score'] * 1.4
    else:
        risk_factors['development_tier'] = "Unknown/Emerging"
        risk_factors['economic_factor'] = risk_factors['continent_risk_score'] * 1.2
    
    # timezone calculation 
    timezone_data = geo_data.get('time_zone', {})
    if isinstance(timezone_data, dict):
        utc_offset = timezone_data.get('utc_offset', '')
    else:
        utc_offset = geo_data.get('utc_offset', '')
    
    try:
        if utc_offset:
            if ':' in utc_offset:
                hours = int(utc_offset.split(':')[0].replace('+', '').replace('-', ''))
            else:
                hours = int(utc_offset.replace('+', '').replace('-', ''))
            risk_factors['timezone_alignment'] = abs(hours) / 12.0  
        else:
            risk_factors['timezone_alignment'] = 0.6
    except:
        risk_factors['timezone_alignment'] = 0.6
    
    # regional stability score
    stability_map = {
        "North America": 0.9, "Europe": 0.8, "Asia": 0.6,
        "South America": 0.4, "Africa": 0.3, "Oceania": 0.9
    }
    risk_factors['regional_stability'] = stability_map.get(continent, 0.5)
    
    overall_risk = (
        risk_factors['economic_factor'] * 0.5 +      
        (1 - risk_factors['regional_stability']) * 0.4 +  
        risk_factors['timezone_alignment'] * 0.1     
    )
    
    # Scale to 0-10 range
    risk_factors['overall_risk_score'] = min(10, round(overall_risk * 1.5, 2))
    
    return risk_factors

def extract_geolocation_data(ip_list):
    """Extract geolocation data for multiple IPs from IPStack"""
    all_geo_data = []
    
    print(f"\nExtracting data for {len(ip_list)} IPs from IPStack...")
    print(f"API Key: {IPSTACK_API_KEY[:8]}...")
    
    for ip in ip_list:
        try:
            url = f"{IPSTACK_BASE_URL}/{ip}"
            params = {
                'access_key': IPSTACK_API_KEY,
                'output': 'json'
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                geo_data = response.json()
                
                if 'error' in geo_data:
                    error_info = geo_data['error'].get('info', 'Unknown API error')
                    print(f"API Error for {ip}: {error_info}")
                    all_geo_data.append({'_source_ip': ip, 'error': error_info})
                elif 'success' in geo_data and geo_data['success'] is False:
                    error_info = geo_data.get('error', {}).get('info', 'Unknown API error')
                    print(f"API Error for {ip}: {error_info}")
                    all_geo_data.append({'_source_ip': ip, 'error': error_info})
                else:
                    geo_data['_source_ip'] = ip
                    if 'time_zone' not in geo_data or not geo_data['time_zone']:
                        geo_data['time_zone'] = {
                            'id': 'Unknown',
                            'utc_offset': '+00:00'
                        }

                    if 'connection' not in geo_data or not geo_data['connection']:
                        geo_data['connection'] = {
                            'isp': 'Unknown ISP',
                            'asn': 'Unknown ASN', 
                            'organization': 'Unknown Organization'
                        }
                    
                    all_geo_data.append(geo_data)
                    country = geo_data.get('country_name', 'Unknown')
                    print(f"Success: {ip} -> {country}")
                    
            else:
                print(f"HTTP Error for {ip}: Status {response.status_code}")
                all_geo_data.append({'_source_ip': ip, 'error': f"HTTP {response.status_code}"})
            
            time.sleep(1.5)
            
        except requests.RequestException as e:
            print(f"Failed to extract data for {ip}: {e}")
            all_geo_data.append({'_source_ip': ip, 'error': str(e)})
            continue
    
    return all_geo_data


def create_network_intelligence_profile(geo_data):
    network_profile = {}
    connection_data = geo_data.get('connection', {})
    if isinstance(connection_data, dict):
        isp = connection_data.get('isp', 'Unknown ISP')
        org = connection_data.get('organization', 'Unknown Organization')
    else:
        isp = geo_data.get('isp', 'Unknown ISP')
        org = geo_data.get('org', 'Unknown Organization')
    
    isp = isp.lower() if isp and isp != 'Unknown ISP' else ''
    org = org.lower() if org and org != 'Unknown Organization' else ''
    
    # Combine ISP and organization for better classification
    combined_text = f"{isp} {org}"
    
    isp_types = {
        'tier1': ['level3', 'cogent', 'ntt', 'tata', 'centurylink', 'he', 'zayo'],
        'tier2': ['comcast', 'att', 'verizon', 'bt', 'deutsche telekom', 'telefonica', 'orange'],
        'hosting': ['digitalocean', 'aws', 'google cloud', 'azure', 'linode', 'ovh', 'google', 'amazon'],
        'mobile': ['vodafone', 't-mobile', 'sprint', 'orange', 'telefonica', 'verizon wireless'],
        'academic': ['university', 'college', 'research', 'edu'],
        'government': ['government', 'military', 'defense', 'state']
    }
    
    network_profile['isp_type'] = 'unknown'
    for isp_type, keywords in isp_types.items():
        if any(keyword in combined_text for keyword in keywords):
            network_profile['isp_type'] = isp_type
            break
    
    # traffic patterns with geographic variation
    country = geo_data.get('country_name', '').lower()
    continent = geo_data.get('continent_name', '').lower()
    
    # traffic patterns based on geography and ISP type
    traffic_patterns = {
        'tier1': {'peak_hours': [14, 22], 'traffic_volume': 'very_high', 'risk_modifier': 0.3},
        'tier2': {'peak_hours': [18, 23], 'traffic_volume': 'high', 'risk_modifier': 0.2},
        'hosting': {'peak_hours': [0, 24], 'traffic_volume': 'consistent', 'risk_modifier': 0.4},
        'mobile': {'peak_hours': [7, 9, 17, 21], 'traffic_volume': 'variable', 'risk_modifier': 0.1},
        'academic': {'peak_hours': [9, 17], 'traffic_volume': 'low', 'risk_modifier': -0.2},
        'government': {'peak_hours': [8, 18], 'traffic_volume': 'medium', 'risk_modifier': 0.5},
        'unknown': {'peak_hours': _get_geographic_peak_hours(country, continent), 'traffic_volume': 'medium', 'risk_modifier': 0.0}
    }
    
    network_profile.update(traffic_patterns[network_profile['isp_type']])
    
    # security posture assessment
    high_security_countries = ['Germany', 'Switzerland', 'Singapore', 'Japan', 'United Kingdom',
                              'Sweden', 'Norway', 'Finland', 'Canada', 'Australia']
    
    medium_security_countries = ['United States', 'France', 'Netherlands', 'South Korea', 'Spain']
    
    if country in high_security_countries:
        network_profile['security_posture'] = 'high'
    elif country in medium_security_countries:
        network_profile['security_posture'] = 'medium'
    elif network_profile['isp_type'] == 'hosting':
        network_profile['security_posture'] = 'enterprise'
    elif network_profile['isp_type'] == 'government':
        network_profile['security_posture'] = 'sensitive'
    else:
        network_profile['security_posture'] = 'standard'
    
    return network_profile


def _get_geographic_peak_hours(country, continent):
    country_peak_hours = {
        'united states': [9, 17, 20, 23], # Business + evening
        'brazil': [10, 13, 17, 22], # Late culture
        'germany': [8, 12, 16, 20], # Early business
        'russia': [10, 14, 18, 22], # Spread out
        'india': [10, 14, 19, 23], # Late peaks
        'japan': [7, 12, 18, 21], # Early start
        'china': [9, 12, 18, 22], # Standard with evening
        'australia': [8, 17, 19, 22], # Standard
    }
    
    continent_peak_hours = {
        'north america': [9, 17, 20, 23],
        'south america': [10, 13, 17, 22], 
        'europe': [8, 12, 16, 20],
        'asia': [9, 12, 18, 22],
        'africa': [9, 13, 17, 21],
        'oceania': [8, 17, 19, 22]
    }
    
    country_lower = country.lower()
    continent_lower = continent.lower()
    
    if country_lower in country_peak_hours:
        return country_peak_hours[country_lower]
    elif continent_lower in continent_peak_hours:
        return continent_peak_hours[continent_lower]
    else:
        return [9, 17]  


def transform_geolocation_data(raw_geo_data):
    transformed_documents = []
    
    print(f"TRANSFORM: Enriching {len(raw_geo_data)} IPs with Intelligence Profiles")
    
    for geo_data in raw_geo_data:
        if geo_data.get('error'):
            print(f"Skipping {geo_data.get('_source_ip')} due to API error: {geo_data.get('error')}")
            continue
            
        ip = geo_data.get('_source_ip', 'unknown')
        
        doc_id = hashlib.md5(f"{ip}_{datetime.now().timestamp()}".encode()).hexdigest()
        
        risk_profile = calculate_geographic_risk_profile(geo_data)
        network_profile = create_network_intelligence_profile(geo_data)
        
        # Clean up timezone data
        timezone_info = {}
        timezone_raw = geo_data.get('time_zone', {})
        if isinstance(timezone_raw, dict) and timezone_raw.get('id') not in [None, '', 'Unknown']:
            timezone_info = {
                'timezone': timezone_raw.get('id', ''),
                'utc_offset': timezone_raw.get('utc_offset', '')
            }
        
        # Clean up connection data 
        connection_info = {}
        connection_raw = geo_data.get('connection', {})
        if isinstance(connection_raw, dict):
            connection_info = {
                'isp': connection_raw.get('isp', ''),
                'asn': connection_raw.get('asn', ''),
                'organization': connection_raw.get('organization', '')
            }
        
        transformed_doc = {
            '_id': doc_id,
            'source_ip': ip,
            'basic_geo': {
                'country': geo_data.get('country_name'),
                'country_code': geo_data.get('country_code'),
                'region': geo_data.get('region_name'),
                'city': geo_data.get('city'),
                'zip_code': geo_data.get('zip'),
                'coordinates': {
                    'lat': geo_data.get('latitude'),
                    'lng': geo_data.get('longitude')
                },
                'continent': geo_data.get('continent_name')
            },
            'risk_intelligence': risk_profile,
            'network_intelligence': network_profile,
            'ingestion_timestamp': datetime.now(timezone.utc).isoformat(),
            'data_freshness': 'realtime'
        }
        
        # Only add timezone data if we have meaningful values
        if timezone_info.get('timezone') or timezone_info.get('utc_offset'):
            transformed_doc['timezone_data'] = timezone_info
        
        # Only add connection data if we have meaningful values  
        if (connection_info.get('isp') and connection_info.get('isp') != 'Unknown ISP' or
            connection_info.get('asn') and connection_info.get('asn') != 'Unknown ASN' or
            connection_info.get('organization') and connection_info.get('organization') != 'Unknown Organization'):
            transformed_doc['raw_connection_data'] = connection_info
        
        transformed_documents.append(transformed_doc)
        
        print(f"\nIP: {ip} -> {geo_data.get('country_name', 'Unknown')}")
        print("  Risk Intelligence:")
        print(f"    Risk Score: {risk_profile['overall_risk_score']}/10")
        print(f"    Development: {risk_profile['development_tier']}")
        print(f"    Stability: {risk_profile['regional_stability']}")
        print(f"    Timezone Alignment: {risk_profile['timezone_alignment']:.2f}")
        
        print("  Network Intelligence:")
        print(f"    ISP Type: {network_profile['isp_type']}")
        print(f"    Traffic: {network_profile['traffic_volume']}")
        print(f"    Peak Hours: {network_profile['peak_hours']}")
        print(f"    Security: {network_profile['security_posture']}")
    
    return transformed_documents

def create_global_relationships(transformed_data):
    if not transformed_data:
        return transformed_data
    
    print("BUILDING GLOBAL RELATIONSHIP NETWORK")
    
    country_clusters = defaultdict(list)
    risk_clusters = defaultdict(list)
    
    for doc in transformed_data:
        country = doc['basic_geo']['country']
        risk_level = "high_risk" if doc['risk_intelligence']['overall_risk_score'] > 6 else "medium_risk" if doc['risk_intelligence']['overall_risk_score'] > 3 else "low_risk"
        
        if country:
            country_clusters[country].append(doc['source_ip'])
        risk_clusters[risk_level].append(doc['source_ip'])
    
    for doc in transformed_data:
        country = doc['basic_geo']['country']
        risk_level = "high_risk" if doc['risk_intelligence']['overall_risk_score'] > 6 else "medium_risk" if doc['risk_intelligence']['overall_risk_score'] > 3 else "low_risk"
        
        doc['global_relationships'] = {
            'country_cluster': {
                'country': country,
                'cluster_members': len(country_clusters[country]) if country else 0,
                'member_ips': country_clusters[country] if country else []
            },
            'risk_cluster': {
                'level': risk_level,
                'cluster_members': len(risk_clusters[risk_level]),
                'similar_risk_ips': risk_clusters[risk_level]
            },
            'regional_partners': list(country_clusters.keys())[:3] if country_clusters else []
        }
        
        country_mates = doc['global_relationships']['country_cluster']['cluster_members']
        risk_peers = doc['global_relationships']['risk_cluster']['cluster_members']
        print(f"IP {doc['source_ip']}: {country_mates} country mates, {risk_peers} {risk_level} peers")
    
    return transformed_data


def load_to_mongodb(transformed_data):
    if not transformed_data:
        return 0, 0
    
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]
    
    inserted, updated = 0, 0
    for doc in transformed_data:
        try:
            result = collection.update_one(
                {'source_ip': doc['source_ip']}, 
                {'$set': doc}, 
                upsert=True
            )
            if result.upserted_id:
                inserted += 1
            elif result.modified_count > 0:
                updated += 1
        except Exception as e:
            print(f"Failed to load document for {doc['source_ip']}: {e}")
    
    client.close()
    return inserted, updated


if __name__ == "__main__":
    print("STARTING IPSTACK GEOLOCATION INTELLIGENCE ETL PIPELINE")
    
    if not IPSTACK_API_KEY:
        print("ERROR: CHECK API KEY")
        exit(1)
    
    target_ips = SAMPLE_IPS
    
    if TEST_MODE:
        target_ips = target_ips[:NUM_TO_TEST]
    
    print("\n" + "_"*80 + "\n")
    print(f"\nStep 1: Extracting geolocation data for {len(target_ips)} IPs")
    raw_geo_data = extract_geolocation_data(target_ips)
    
    if raw_geo_data:
        successful_extractions = len([d for d in raw_geo_data if not d.get('error')])
        print(f"Extract successful. Processed {successful_extractions} IPs.")
        
        if successful_extractions > 0:
            print("\n" + "_"*80 + "\n")
            print(f"\nStep 2: Creating intelligence profiles\n")
            transformed_data = transform_geolocation_data(raw_geo_data)
            print("\n" + "_"*80 + "\n")
            print(f"\nStep 3: Building global network\n")
            final_data = create_global_relationships(transformed_data)
            print("\n" + "_"*80 + "\n")
            print(f"\nStep 4: Storing {len(final_data)} intelligence documents in MongoDB")
            inserted, updated = load_to_mongodb(final_data)
            print("\n" + "_"*80 + "\n")
            print("TABULATION\n")
            print(f"IPs Processed       : {len(final_data)}")
            print(f"New Documents       : {inserted}")
            print(f"Updated Documents   : {updated}")
            countries = list(set(d['basic_geo']['country'] for d in final_data if d['basic_geo']['country']))
            print(f"Countries Covered   : {len(countries)}")
            print(f"Risk Distribution   : High: {len([d for d in final_data if d['risk_intelligence']['overall_risk_score'] > 6])}, "
                  f"Medium: {len([d for d in final_data if 3 < d['risk_intelligence']['overall_risk_score'] <= 6])}, "
                  f"Low: {len([d for d in final_data if d['risk_intelligence']['overall_risk_score'] <= 3])}")
            print("\nIPStack Geolocation Intelligence Pipeline Complete!")
            print("_"*80 + "\n")
        else:
            print("Pipeline failed: No successful data extractions")
    else:
        print("Pipeline failed: No data extracted")