import requests, os
from collections import Counter
from datetime import datetime
from pymongo import MongoClient


from config import load_config
config = load_config()


def connect_mongodb():
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    client = MongoClient(mongo_uri)
    db_name = os.getenv('MONGO_DB', 'alienvault_db')
    db = client[db_name]
    return db



def extract_pulses(config):
    url = f"{config['BASE_URL']}{config['PULSES_SUBSCRIBED_ENDPOINT']}"
    headers = {'X-OTX-API-KEY': config['API_KEY']}

    pulses = []
    params = {'page': 1}
    page_limit = config.get('PAGE_LIMIT', 0) # default - 0

    while True:
        if page_limit and params['page'] > page_limit:
            print(f"Reached page limit of {page_limit}, stopping fetch.")
            break

        print(f"Fetching page {params['page']}...")
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")

        data = response.json()
        page_pulses = data.get('results', [])
        pulses.extend(page_pulses)

        if not data.get('next'):
            break
        params['page'] += 1

    print(f"Total pulses fetched: {len(pulses)}")
    return pulses

def print_insights(pulses):
    print("\n--- Pulses Insights ---")
    print(f"Total pulses fetched: {len(pulses)}")

    if not pulses:
        print("No pulses to analyze.")
        return

    authors = [pulse.get('author_name') for pulse in pulses if pulse.get('author_name')]
    unique_authors = set(authors)
    print(f"Unique authors: {len(unique_authors)}")
    print(f"Unique author list: {unique_authors}")

    all_tags = []
    for pulse in pulses:
        tags = pulse.get('tags', [])
        all_tags.extend(tags)
    top_tags = Counter(all_tags).most_common(5)
    print("Top 5 tags:")
    for tag, count in top_tags:
        print(f"  {tag}: {count}")

    threat_levels = [pulse.get('threat_level') or pulse.get('tlp') for pulse in pulses if (pulse.get('threat_level') or pulse.get('tlp'))]
    threat_counts = Counter(threat_levels)
    print("Threat level counts:")
    if threat_counts:
        for level, count in threat_counts.items():
            print(f"  {level}: {count}")
    else:
        print("  No threat level data found.")

 
    created_dates = []
    for pulse in pulses:
        created = pulse.get('created')
        if created:
            try:
                dt = datetime.strptime(created, "%Y-%m-%dT%H:%M:%S.%f")
                created_dates.append(dt)
            except ValueError:
                pass

    if created_dates:
        print(f"Created date range: {min(created_dates)} to {max(created_dates)}")


def transform_data(raw_pulses):
    if not raw_pulses:
        print("No pulses to transform.")
        return []
    transformed = []
    
    ingest_time = datetime.now()

    for pulse in raw_pulses:
        try:
            if not pulse.get('id'):
                continue
                
            doc = {
            
                'pulse_id': pulse.get('id'),
                'name': pulse.get('name', ''),
                'description': pulse.get('description', ''),
                'author_name': pulse.get('author_name', ''),
       
                'created': parse_date(pulse.get('created')),
                'modified': parse_date(pulse.get('modified')),
       
                'tlp': pulse.get('tlp', 'white'),
                'public': pulse.get('public', True),
                'revision': pulse.get('revision', 1),
           
                'tags': pulse.get('tags', []),
                'references': pulse.get('references', []),
                'malware_families': pulse.get('malware_families', []),
                'attack_ids': pulse.get('attack_ids', []),
                'industries': pulse.get('industries', []),
                'targeted_countries': pulse.get('targeted_countries', []),
                
                'indicators': pulse.get('indicators', []),
   
                'ingested_at': ingest_time,
                'last_updated_at': ingest_time,

            }
            transformed.append(doc)
            
        except Exception as e:
            print(f"Error transforming pulse {pulse.get('id', 'unknown')}: {e}")
            continue
    
    return transformed

def parse_date(date_str):
    """Parse date string to datetime object."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        return None
    

def load_to_mongodb(db, documents):
    if not documents:
        print("No documents to insert.")
        return
    collection_name = 'alienvault_pulses'
    collection = db[collection_name]
    
    collection.create_index("pulse_id", unique=True)
    
    if not documents:
        print("No documents to insert.")
        return
    
    inserted = 0
    updated = 0
    errors = 0 
    
    for doc in documents:
        try:
            result = collection.replace_one(
                {'pulse_id': doc['pulse_id']}, 
                doc, 
                upsert=True
            )
            if result.upserted_id:
                inserted += 1
            elif result.modified_count > 0:
                updated += 1
        except Exception as e:
            errors += 1
            print(f"Error inserting pulse {doc.get('pulse_id')}: {e}")
    
    print(f"Inserted: {inserted}, Updated: {updated}, Errors: {errors} in '{collection_name}'.")



if __name__=='__main__':
    try:
        print("\n" + "="*30 + " [Stage 1] EXTRACT " + "="*30)
        result = extract_pulses(config)
        print(f"Extraction complete — {len(result)} pulses retrieved.")

        print("\n" + "="*30 + " [Stage 2] INSIGHTS " + "="*30)
        print_insights(result)
        print("Insights generation complete.")

        print("\n" + "="*30 + " [Stage 3] CONNECT TO MONGODB " + "="*30)
        db = connect_mongodb()
        print("MongoDB connection established.")

        print("\n" + "="*30 + " [Stage 4] TRANSFORM " + "="*30)
        transformed_data = transform_data(result)
        print(f"Transformation complete — {len(transformed_data)} documents ready.")

        print("\n" + "="*30 + " [Stage 5] LOAD TO MONGODB " + "="*30)
        load_to_mongodb(db, transformed_data)
        print("Data successfully loaded into MongoDB.")

        print("\n" + "="*30 + " [PIPELINE COMPLETED SUCCESSFULLY] " + "="*30)

    except Exception as e:
        print("\n" + "="*30 + " [PIPELINE FAILED] " + "="*30)
        print(f"Error: {e}")
