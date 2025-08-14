import os
import logging
import traceback
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient, errors

# ---------------- LOGGING CONFIG ----------------
LOG_FILE = "transform_vulnerabilities.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

# ---------------- LOAD ENV ----------------
try:
    load_dotenv()
    MONGO_URL = os.getenv("MONGO_URI")
    MONGO_DB = os.getenv("MONGO_DB_NAME")

    if not MONGO_URL or not MONGO_DB:
        raise ValueError("MONGO_URL or MONGO_DB not set in .env")

    logging.info("Loaded environment variables successfully.")
except Exception as e:
    logging.error(f"Failed to load environment variables: {e}")
    logging.error(traceback.format_exc())
    raise

# ---------------- MONGO CONNECTION ----------------
try:
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    client.server_info()  # Test connection
    db = client[MONGO_DB]
    raw_collection = db["nvd_raw"]
    transformed_collection = db["nvd_vulnerabilities"]

    logging.info(f"Connected to MongoDB: DB={MONGO_DB}")
except errors.ServerSelectionTimeoutError as e:
    logging.error(f"MongoDB connection failed: {e}")
    logging.error(traceback.format_exc())
    raise

# ---------------- CLEAR OLD DATA ----------------
try:
    delete_result = transformed_collection.delete_many({})
    logging.info(f"Cleared {delete_result.deleted_count} existing documents in '{transformed_collection.name}'.")
except Exception as e:
    logging.error(f"Failed to clear collection '{transformed_collection.name}': {e}")
    logging.error(traceback.format_exc())

# ---------------- LOAD RAW DATA ----------------
try:
    raw_data = raw_collection.find_one()
    if not raw_data or "vulnerabilities" not in raw_data:
        raise ValueError("No vulnerabilities found in raw data.")
    logging.info(f"Loaded raw data with {len(raw_data.get('vulnerabilities', []))} vulnerabilities.")
except Exception as e:
    logging.error(f"Failed to load raw data: {e}")
    logging.error(traceback.format_exc())
    raise

# ---------------- TRANSFORM DATA ----------------
vulnerabilities = []
try:
    for vuln_item in raw_data.get("vulnerabilities", []):
        try:
            cve = vuln_item["cve"]

            # English description
            description = next(
                (desc.get("value") for desc in cve.get("descriptions", []) if desc.get("lang") == "en"), ""
            )

            # Metrics: take first cvssMetricV2 entry if exists
            metrics_data = cve.get("metrics", {}).get("cvssMetricV2", [])
            metrics_transformed = {}
            if metrics_data:
                m = metrics_data[0]
                cvss = m.get("cvssData", {})
                metrics_transformed = {
                    "type": m.get("type"),
                    "version": cvss.get("version"),
                    "vectorString": cvss.get("vectorString"),
                    "baseScore": cvss.get("baseScore"),
                    "accessVector": cvss.get("accessVector"),
                    "accessComplexity": cvss.get("accessComplexity"),
                    "authentication": cvss.get("authentication"),
                    "confidentialityImpact": cvss.get("confidentialityImpact"),
                    "integrityImpact": cvss.get("integrityImpact"),
                    "availabilityImpact": cvss.get("availabilityImpact"),
                    "baseSeverity": m.get("baseSeverity"),
                    "exploitabilityScore": m.get("exploitabilityScore"),
                    "impactScore": m.get("impactScore"),
                    "acInsufInfo": m.get("acInsufInfo"),
                    "obtainAllPrivilege": m.get("obtainAllPrivilege"),
                    "obtainUserPrivilege": m.get("obtainUserPrivilege"),
                    "obtainOtherPrivilege": m.get("obtainOtherPrivilege"),
                    "userInteractionRequired": m.get("userInteractionRequired")
                }

            # Weaknesses
            weaknesses_list = []
            for w in cve.get("weaknesses", []):
                type_ = w.get("type")
                desc_en = next((d.get("value") for d in w.get("description", []) if d.get("lang") == "en"), "")
                weaknesses_list.append({"type": type_, "description": desc_en})

            # References: only URLs
            references = list({ref.get("url") for ref in cve.get("references", []) if ref.get("url")})

            # Construct transformed vulnerability
            transformed_vuln = {
                "id": cve.get("id"),
                "sourceIdentifier": cve.get("sourceIdentifier"),
                "published": cve.get("published"),
                "lastModified": cve.get("lastModified"),
                "vulnStatus": cve.get("vulnStatus"),
                "description": description,
                **metrics_transformed,
                "weaknesses": weaknesses_list,
                "references": references,
                "collected_at": datetime.utcnow().isoformat()
            }

            vulnerabilities.append(transformed_vuln)
        except Exception as inner_e:
            logging.warning(f"Failed to transform a vulnerability record: {inner_e}")
            logging.warning(traceback.format_exc())

    logging.info(f"Transformed {len(vulnerabilities)} vulnerabilities successfully.")
except Exception as e:
    logging.error(f"Transformation process failed: {e}")
    logging.error(traceback.format_exc())
    raise

# ---------------- STORE TRANSFORMED DATA ----------------
try:
    if vulnerabilities:
        insert_result = transformed_collection.insert_many(vulnerabilities)
        logging.info(f"Inserted {len(insert_result.inserted_ids)} vulnerabilities into '{transformed_collection.name}'.")
    else:
        logging.warning("No vulnerabilities to insert.")
except Exception as e:
    logging.error(f"Failed to insert transformed data into MongoDB: {e}")
    logging.error(traceback.format_exc())
    raise

logging.info("[DONE] Transformation process completed successfully.")
