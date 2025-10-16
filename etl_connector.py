# etl_connector.py
import logging, time
from fetcher import fetch_single, fetch_batch
from transformer import transform_raw_ipapi
from loader import MongoLoader
from config import BATCH_SIZE, RATE_LIMIT_BATCH, RATE_LIMIT_SINGLE
from typing import List, Dict

logger = logging.getLogger("etl_connector")
logging.basicConfig(level=logging.INFO)

class IPAPIEtlConnector:
    """Encapsulates the full ETL workflow for ip-api.com."""

    def __init__(self):
        self.loader = MongoLoader()

    def run_single_etl(self, query: str) -> Dict:
        logger.info(f"Running single ETL for: {query}")
        raw = fetch_single(query)
        doc = transform_raw_ipapi(raw, query=query)
        self.loader.upsert_one(doc)
        time.sleep(60.0 / RATE_LIMIT_SINGLE)
        return doc

    def run_batch_etl(self, queries: List[str]) -> List[Dict]:
        logger.info(f"Running batch ETL for {len(queries)} queries")
        results = []
        for i in range(0, len(queries), BATCH_SIZE):
            batch = queries[i:i + BATCH_SIZE]
            raw_list = fetch_batch(batch)
            docs = [transform_raw_ipapi(r, q) for r, q in zip(raw_list, batch)]
            self.loader.bulk_insert(docs)
            results.extend(docs)
            time.sleep(60.0 / RATE_LIMIT_BATCH)
        return results

if __name__ == "__main__":
    connector = IPAPIEtlConnector()
    queries = ["8.8.8.8", "1.1.1.1", "example.com", "github.com"]
    connector.run_batch_etl(queries)
