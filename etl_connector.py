import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import time
import logging
from collections import defaultdict

# --- Developer Configuration ---
TEST_MODE = False
NUM_TO_TEST = 30 

# --- Configuration and Setup ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# NVD API & MongoDB Configuration (Unchanged)
NVD_API_KEY = os.getenv("NVD_API_KEY")
NVD_BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "cve_database")
MONGO_COLLECTION_NAME = "enriched_cves"

# --- Novelty 1: Full Risk Decomposer ---
def decompose_cvss_vector(vector_string):
    if not vector_string or not vector_string.startswith("CVSS:3"):
        return {"status": "unavailable", "reason": "No CVSS 3.x vector found."}
    attack_vector_map = {"N": "Network", "A": "Adjacent Network", "L": "Local", "P": "Physical"}
    attack_complexity_map = {"L": "Low", "H": "High"}
    privileges_required_map = {"N": "None", "L": "Low", "H": "High"}
    user_interaction_map = {"N": "None", "R": "Required"}
    scope_map = {"U": "Unchanged", "C": "Changed (Escalated Risk)"}
    impact_map = {"H": "High", "L": "Low", "N": "None"}
    breakdown = {}
    for metric in vector_string.split('/'):
        key, value = metric.split(':')
        if key == "AV": breakdown['attack_vector'] = attack_vector_map.get(value)
        elif key == "AC": breakdown['attack_complexity'] = attack_complexity_map.get(value)
        elif key == "PR": breakdown['privileges_required'] = privileges_required_map.get(value)
        elif key == "UI": breakdown['user_interaction'] = user_interaction_map.get(value)
        elif key == "S": breakdown['scope'] = scope_map.get(value)
        elif key == "C": breakdown['confidentiality_impact'] = impact_map.get(value)
        elif key == "I": breakdown['integrity_impact'] = impact_map.get(value)
        elif key == "A": breakdown['availability_impact'] = impact_map.get(value)
    return breakdown

# --- ETL Pipeline ---
def extract_cves(start_date, end_date):
    cves = []
    headers = {'apiKey': NVD_API_KEY} if NVD_API_KEY else {}
    params = {'pubStartDate': start_date.isoformat(), 'pubEndDate': end_date.isoformat(), 'resultsPerPage': 2000}
    try:
        logging.info("Fetching CVE data from NVD API...")
        response = requests.get(NVD_BASE_URL, headers=headers, params=params)
        cves.extend(response.json().get('vulnerabilities', []))
    except requests.RequestException: return []
    return cves

def transform_and_enrich_cves(cves_raw):
    # --- STAGE 1: Initial Transformation & Filtering ---
    base_cves = []
    print("\n" + "="*80 + f"\n🔬 Stage 1: Filtering and Decomposing Risk for {len(cves_raw)} CVEs...\n" + "="*80)
    for cve_raw in cves_raw:
        cve_info = cve_raw.get('cve', {})
        cve_id = cve_info.get('id')
        metrics = cve_info.get('metrics', {}).get('cvssMetricV31', [{}])[0]
        cvss_data = metrics.get('cvssData', {})
        vector_string = cvss_data.get('vectorString')

        if not vector_string or not vector_string.startswith("CVSS:3"):
            continue

        base_cves.append({
            "_id": cve_id, "cve_id": cve_id, "published_date": cve_info.get('published'),
            "description": next((d['value'] for d in cve_info.get('descriptions', []) if d['lang'] == 'en'), "N/A"),
            "base_score": cvss_data.get('baseScore'), "severity": cvss_data.get('baseSeverity'),
            "risk_breakdown": decompose_cvss_vector(vector_string),
            "references": [ref.get('url') for ref in cve_info.get('references', [])]
        })

    # --- STAGE 2: Genealogy Analysis ---
    print("\n" + "="*80 + "\n🌳 Stage 2: Building Vulnerability Genealogy Map...\n" + "="*80)
    
    # 1. Build the map of which CVEs share which reference URLs
    reference_map = defaultdict(list)
    for cve in base_cves:
        for ref in cve.get('references', []):
            reference_map[ref].append(cve['cve_id'])
    
    print("✅ Genealogy Map Complete. Assembling final documents...")
    
    # 2. Build the final list of documents, using the map to find relatives
    final_documents = []
    for cve in base_cves:
        related_cves = []
        shared_advisories = []
        for ref in cve.get('references', []):
            potential_relatives = reference_map.get(ref, [])
            if len(potential_relatives) > 1:
                # This advisory is shared, so it's a link
                if ref not in shared_advisories:
                    shared_advisories.append(ref)
                # Add all other CVEs from that link as relatives
                for relative in potential_relatives:
                    if relative != cve['cve_id'] and relative not in related_cves:
                        related_cves.append(relative)
        
        # Create the genealogy object
        cve['genealogy'] = {
            "status": "Has Relatives" if related_cves else "Isolated",
            "related_cves": sorted(related_cves), # Sort for consistent order
            "shared_advisories": shared_advisories
        }
        
        # Clean up the references list before saving, as it's redundant now
        del cve['references']
        cve['ingestion_timestamp'] = datetime.now(timezone.utc).isoformat()
        final_documents.append(cve)

    # --- STAGE 3: Final Print Review ---
    print("\n" + "="*80 + "\n📋 Final Enrichment Data Review...\n" + "="*80)
    for cve in final_documents:
        severity = cve.get('severity', 'N/A')
        print(f"\n--------------------------------------------------------------------------------")
        print(f"🔎 {cve['cve_id']}  |  Severity: {severity}")
        print(f"--------------------------------------------------------------------------------")

        rb = cve.get('risk_breakdown', {})
        scope_marker = "🚨" if "Changed" in rb.get('scope', '') else ""
        print("  [ Risk Profile ]")
        print(f"    ├─ Attack Vector          : {rb.get('attack_vector', 'N/A')}")
        print(f"    ├─ Attack Complexity      : {rb.get('attack_complexity', 'N/A')}")
        print(f"    ├─ Privileges Required    : {rb.get('privileges_required', 'N/A')}")
        print(f"    ├─ User Interaction       : {rb.get('user_interaction', 'N/A')}")
        print(f"    ├─ Scope                  : {rb.get('scope', 'N/A')} {scope_marker}")
        print(f"    ├─ Confidentiality Impact : {rb.get('confidentiality_impact', 'N/A')}")
        print(f"    ├─ Integrity Impact       : {rb.get('integrity_impact', 'N/A')}")
        print(f"    └─ Availability Impact    : {rb.get('availability_impact', 'N/A')}")

        genealogy = cve.get('genealogy', {})
        print("  [ Genealogy ]")
        if genealogy.get('status') == "Has Relatives":
            relatives = genealogy.get('related_cves', [])
            relatives_count = len(relatives)
            if relatives_count > 2: display_relatives = f"[{relatives[0]}, {relatives[1]}, and {relatives_count - 2} more...]"
            else: display_relatives = str(relatives)
            print(f"    └─ 🌳 Part of a Pack. Found {relatives_count} relative(s): {display_relatives}")
        else:
            print("    └─ 🐺 Isolated Case. No relatives found in this batch.")
            
    return final_documents

def load_to_mongodb(transformed_cves):
    if not transformed_cves: return 0, 0
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]
    inserted, updated = 0, 0
    for cve in transformed_cves:
        result = collection.update_one({'_id': cve['_id']}, {'$set': cve}, upsert=True)
        if result.upserted_id: inserted += 1
        elif result.modified_count > 0: updated += 1
    return inserted, updated

# --- Main Execution ---
if __name__ == "__main__":
    print("\n" + "="*80 + "\n🚀 STARTING VULNERABILITY GENEALOGY ETL PIPELINE 🚀\n" + "="*80)
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)
    print(f"\n[ 1/4 ] EXTRACT: Fetching CVEs from the last 30 days...")
    raw_cves = extract_cves(start_date, end_date)
    if raw_cves:
        print(f"✅ Extract successful. Found {len(raw_cves)} total CVEs.")
        if TEST_MODE:
            print(f"🔥 TEST MODE IS ACTIVE. Processing only the first {NUM_TO_TEST} CVEs. 🔥")
            raw_cves = raw_cves[:NUM_TO_TEST]
        print(f"\n[ 2/4 ] TRANSFORM & ENRICH: Building risk profiles and finding relatives...")
        transformed_data = transform_and_enrich_cves(raw_cves)
        print("\n" + "="*80 + f"\n✅ Enrichment Complete. {len(transformed_data)} CVEs were processed and are ready for loading.\n" + "="*80)
        print(f"\n[ 3/4 ] LOAD: Storing {len(transformed_data)} enriched documents into MongoDB...")
        inserted, updated = load_to_mongodb(transformed_data)
        if inserted > 0 or updated > 0: print("✅ Load successful.")
        else: print("❌ Load failed.")
        print("\n" + "="*80 + "\n📊 [ 4/4 ] ETL PIPELINE EXECUTION SUMMARY 📊\n" + "="*80)
        print(f"🔹 Mode                : TEST (Processed {len(transformed_data)} of {NUM_TO_TEST if TEST_MODE else len(raw_cves)} selected CVEs)")
        print(f"🔹 New CVEs Inserted   : {inserted}")
        print(f"🔹 Existing CVEs Updated : {updated}")
        print("="*80 + "\n✅ Pipeline Finished.\n" + "="*80 + "\n")