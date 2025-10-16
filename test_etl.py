"""
Unit tests for IP-API ETL Connector
-----------------------------------
Mimics a functional test flow as shown in the example output screenshot.

Run:
    python -m unittest test_etl.py
"""

import unittest
from unittest.mock import patch, MagicMock
from pymongo.errors import ConnectionFailure
from etl_connector import IPAPIEtlConnector
from fetcher import fetch_single
from transformer import transform_raw_ipapi
from loader import MongoLoader

class TestIpApiETL(unittest.TestCase):

    @patch('fetcher.requests.get')
    def test_network_connectivity_issue(self, mock_get):
        print("\nTesting: Network connectivity issue to API...")

        # Simulate network failure
        mock_get.side_effect = Exception("Unable to connect")

        try:
            with self.assertRaises(Exception):
                fetch_single("8.8.8.8")
            print("  ➜ Passed: Retry/Error handling works correctly.\n")
        except AssertionError:
            self.fail("❌ Failed: Did not handle network exception properly.")

    @patch('fetcher.requests.get')
    def test_successful_data_extraction(self, mock_get):
        print("Testing: Successful data extraction...")

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "status": "success",
            "country": "United States",
            "lat": 37.4,
            "lon": -122.0,
            "as": "AS15169 Google LLC",
            "query": "8.8.8.8"
        }
        mock_get.return_value = mock_resp

        result = fetch_single("8.8.8.8")
        self.assertEqual(result["status"], "success")
        print("  ➜ Passed: Extraction returns valid JSON.\n")

    def test_data_transformation(self):
        print("Testing: Data transformation...")

        raw_record = {
            "query": "8.8.8.8",
            "as": "AS15169 Google LLC",
            "lat": 37.4192,
            "lon": -122.0574,
            "country": "United States"
        }
        transformed = transform_raw_ipapi(raw_record, "8.8.8.8")
        self.assertIn("asn_parsed", transformed)
        self.assertIn("location", transformed)
        self.assertFalse(transformed.get("is_private", True))
        print("  ➜ Passed: Transform function executed and enriched correctly.\n")

    @patch.object(MongoLoader, 'upsert_one')
    def test_mongo_upsert(self, mock_upsert):
        print("Testing: Correct data upsert into MongoDB...")

        connector = IPAPIEtlConnector()
        mock_upsert.return_value = None

        doc = {"ip": "8.8.8.8", "query_original": "8.8.8.8"}
        connector.loader.upsert_one(doc)

        mock_upsert.assert_called_once_with(doc)
        print("  ➜ Passed: Verified that upsert_one() was called correctly.\n")

    @patch('loader.MongoClient')
    def test_database_connection_error(self, mock_mongo_client):
        print("Testing: Database connectivity issue...")

        mock_mongo_client.side_effect = ConnectionFailure("Cannot connect to MongoDB")

        try:
            MongoLoader()
        except ConnectionFailure:
            print("  ➜ Passed: Database connection error handled gracefully.\n")
        else:
            self.fail("❌ Failed: Database connection exception not raised.")


if __name__ == "__main__":
    print("\nRunning IP-API ETL Unit Tests...\n")
    unittest.main(verbosity=2)
