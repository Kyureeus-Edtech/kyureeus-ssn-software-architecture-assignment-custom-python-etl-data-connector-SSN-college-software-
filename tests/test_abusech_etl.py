import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import requests
import logging

# Import the classes and functions we want to test
from connectors.abusech_api import AbuseCHConnector
from transformations.data_transformer import standardize_urlhaus_data, standardize_malwarebazaar_data
from database.mongo_loader import MongoLoader

# --- MOCK DATA SAMPLES ---
# These simulate the JSON responses from the abuse.ch APIs

MOCK_URLHAUS_RESPONSE = {
    "query_status": "ok",
    "urls": [
        {"id": "1", "url": "http://evil.com/payload.exe", "date_added": "2025-10-16 10:00:00 UTC", "threat": "malware_download", "tags": ["exe", "trojan"]},
        {"id": "2", "url": "http://phish.com/login", "date_added": "2025-10-16 11:00:00 UTC", "threat": "phishing", "tags": None}
    ]
}

MOCK_MALWAREBAZAAR_RESPONSE = {
    "query_status": "ok",
    "data": [
        {"sha256_hash": "aaa...", "first_seen": "1729084200", "file_type": "exe", "signature": "evil_malware", "tags": ["rat"]},
        {"sha256_hash": "bbb...", "first_seen": "2025-10-16 12:00:00", "file_type": "pdf", "signature": None, "tags": []}
    ]
}

# Disable application logging during tests for a cleaner output
logging.disable(logging.CRITICAL)


class TestETLExtract(unittest.TestCase):
    """Tests for the data extraction module (connectors/abusech_api.py)"""

    @patch('connectors.abusech_api.requests.get')
    def test_get_urlhaus_success(self, mock_get):
        """Testing: Successful extraction of URLhaus data."""
        print("\nTesting: Successful URLhaus data extraction...")
        # Configure mock to return a successful response with fake data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_URLHAUS_RESPONSE
        mock_get.return_value = mock_response

        connector = AbuseCHConnector(api_key="fake_key")
        data = connector.get_urlhaus_recent()

        self.assertIsNotNone(data)
        self.assertEqual(data['query_status'], 'ok')
        print("-> Passed.")

    @patch('connectors.abusech_api.requests.post')
    def test_get_malwarebazaar_success(self, mock_post):
        """Testing: Successful extraction of MalwareBazaar data."""
        print("\nTesting: Successful MalwareBazaar data extraction...")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_MALWAREBAZAAR_RESPONSE
        mock_post.return_value = mock_response

        connector = AbuseCHConnector(api_key="fake_key")
        data = connector.get_malwarebazaar_recent()

        self.assertIsNotNone(data)
        self.assertEqual(len(data['data']), 2)
        print("-> Passed.")

    @patch('connectors.abusech_api.requests.get')
    def test_get_data_api_error(self, mock_get):
        """Testing: Extractor handles an API connection error gracefully."""
        print("\nTesting: API connection failure...")
        mock_get.side_effect = requests.exceptions.RequestException("Connection timed out")

        connector = AbuseCHConnector(api_key="fake_key")
        data = connector.get_urlhaus_recent()

        self.assertIsNone(data) # Should return None on failure
        print("-> Passed: Handled API error gracefully.")


class TestETLTransform(unittest.TestCase):
    """Tests for the data transformation module (transformations/data_transformer.py)"""

    def test_transform_urlhaus_data(self):
        """Testing: Correct transformation of URLhaus data."""
        print("\nTesting: Data transformation for URLhaus...")
        transformed = standardize_urlhaus_data(MOCK_URLHAUS_RESPONSE)

        self.assertEqual(len(transformed), 2)
        # Test threat_level logic (first item has 'exe' tag)
        self.assertEqual(transformed[0]['threat_level'], 'high')
        # Test threat_level logic (second item has no tags)
        self.assertEqual(transformed[1]['threat_level'], 'medium')
        self.assertIsInstance(transformed[0]['first_seen'], datetime)
        print("-> Passed.")

    def test_transform_malwarebazaar_data(self):
        """Testing: Correct transformation of MalwareBazaar data, including multiple date formats."""
        print("\nTesting: Data transformation for MalwareBazaar...")
        transformed = standardize_malwarebazaar_data(MOCK_MALWAREBAZAAR_RESPONSE)
        
        self.assertEqual(len(transformed), 2)
        # Test file_class logic
        self.assertEqual(transformed[0]['file_class'], 'executable')
        self.assertEqual(transformed[1]['file_class'], 'document')
        # Test that both date formats were parsed correctly
        self.assertIsInstance(transformed[0]['first_seen'], datetime) # From timestamp
        self.assertIsInstance(transformed[1]['first_seen'], datetime) # From string
        print("-> Passed.")


class TestETLLoad(unittest.TestCase):
    """Tests for the data loading module (database/mongo_loader.py)"""

    @patch('database.mongo_loader.MongoClient')
    def test_upsert_data_success(self, mock_mongo_client):
        """Testing: Correct upsert operation into MongoDB."""
        print("\nTesting: Correct data upsert into MongoDB...")
        # Mock the entire MongoDB connection and collection objects
        mock_collection = MagicMock()
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_mongo_client.return_value.__getitem__.return_value = mock_db

        loader = MongoLoader(uri="fake_uri")
        test_data = standardize_urlhaus_data(MOCK_URLHAUS_RESPONSE)
        loader.upsert_data('urlhaus_iocs', test_data)

        # Assertions
        # Check if the correct collection was accessed
        mock_db.__getitem__.assert_called_with('urlhaus_iocs')
        # Check if update_one was called for each record
        self.assertEqual(mock_collection.update_one.call_count, 2)
        print("-> Passed.")

    @patch('database.mongo_loader.MongoClient')
    def test_loader_handles_connection_failure(self, mock_mongo_client):
        """Testing: Loader handles a database connection failure gracefully."""
        print("\nTesting: Database connection failure...")
        # Simulate a ConnectionFailure exception when MongoClient is called
        from pymongo.errors import ConnectionFailure
        mock_mongo_client.side_effect = ConnectionFailure("Could not connect")

        # The loader should catch the exception and not crash
        loader = MongoLoader(uri="fake_uri")
        self.assertIsNone(loader.client) # The client should be None after a failed connection
        print("-> Passed: Handled database connection error.")


if __name__ == '__main__':
    unittest.main()
