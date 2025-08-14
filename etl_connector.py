import os
import csv
import time
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError, ServerSelectionTimeoutError


class PhishTankETL:
    def __init__(self, mongo_uri, source_url, db_name="etl_db", coll_name="phishtank_raw"):
        self.mongo_uri = mongo_uri
        self.source_url = source_url
        self.db_name = db_name
        self.coll_name = coll_name
        self.collection = self._connect()
    
    def _connect(self):
        """Establish MongoDB connection and return the collection."""
        try:
            client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=10000)
            client.admin.command("ping")  # Immediate connection test
            db = client[self.db_name]
            coll = db[self.coll_name]
            coll.create_index("phish_id", unique=True)
            print(f"[INFO] Connected to MongoDB: {self.db_name}.{self.coll_name}")
            return coll
        except ServerSelectionTimeoutError:
            raise ConnectionError("Cannot connect to MongoDB. Check MONGO_URI and network access.")

    def _fetch_csv(self, retries=3, backoff=5):
        """Download CSV data from source with retry logic."""
        for attempt in range(retries):
            try:
                resp = requests.get(self.source_url, stream=True, timeout=30)
                resp.raise_for_status()
                return csv.DictReader(resp.iter_lines(decode_unicode=True))
            except requests.RequestException as e:
                print(f"[ERROR] Fetch attempt {attempt+1} failed: {e}")
                if attempt < retries - 1:
                    wait = backoff * (attempt + 1)
                    print(f"[INFO] Retrying in {wait}s...")
                    time.sleep(wait)
        raise RuntimeError("Failed to download data after multiple attempts.")

    @staticmethod
    def _clean_row(row):
        """Transform a single CSV row into a MongoDB document."""
        pid = row.get("phish_id", "").strip()
        link = row.get("url", "").strip()
        if not pid or not link:
            return None
        
        submitted_time = None
        if row.get("submission_time"):
            try:
                submitted_time = datetime.fromisoformat(row["submission_time"])
            except ValueError:
                pass
        
        return {
            "phish_id": pid,
            "url": link,
            "submission_time": submitted_time,
            "verified": row.get("verified", "").lower() in ("yes", "y", "true"),
            "ingested_at": datetime.now(timezone.utc)
        }

    def _commit_batch(self, batch_ops):
        """Write a batch of operations to MongoDB."""
        try:
            result = self.collection.bulk_write(batch_ops, ordered=False)
            return result.upserted_count, result.matched_count
        except BulkWriteError as bwe:
            print(f"[WARN] Bulk write error: {bwe.details}")
            return 0, 0

    def run(self, max_rows=None, batch_size=1000):
        """Main ETL process."""
        reader = self._fetch_csv()
        pending_ops = []
        inserted, updated, skipped, processed = 0, 0, 0, 0

        for row in reader:
            if max_rows and processed >= max_rows:
                break

            doc = self._clean_row(row)
            if not doc:
                skipped += 1
                processed += 1
                continue

            pending_ops.append(
                UpdateOne({"phish_id": doc["phish_id"]}, {"$set": doc}, upsert=True)
            )

            if len(pending_ops) >= batch_size:
                ins, upd = self._commit_batch(pending_ops)
                inserted += ins
                updated += upd
                pending_ops.clear()

            processed += 1

        if pending_ops:
            ins, upd = self._commit_batch(pending_ops)
            inserted += ins
            updated += upd

        print(f"[DONE] Inserted: {inserted}, Updated: {updated}, Skipped: {skipped}, Total: {processed}")


if __name__ == "__main__":
    load_dotenv()
    etl = PhishTankETL(
        mongo_uri=os.getenv("MONGO_URI"),
        source_url=os.getenv("PHISHTANK_URL")
    )
    etl.run(max_rows=500, batch_size=500)
