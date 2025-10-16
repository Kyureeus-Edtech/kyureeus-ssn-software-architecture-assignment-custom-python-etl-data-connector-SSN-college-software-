# etl_runner.py
from etl_connector import IPAPIEtlConnector

if __name__ == "__main__":
    connector = IPAPIEtlConnector()
    queries = ["8.8.8.8", "1.1.1.1", "example.com"]
    connector.run_batch_etl(queries)
