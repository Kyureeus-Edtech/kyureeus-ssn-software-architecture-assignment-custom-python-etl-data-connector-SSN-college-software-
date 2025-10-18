# tests/test_abusech_etl.py

import unittest
from unittest.mock import patch, MagicMock, call
import requests
from datetime import datetime
import logging

# Import the classes and functions we want to test
from connectors.abusech_api import AbuseCHConnector
from transformations.data_transformer import standardize_urlhaus_data, standardize_malwarebazaar_data
from database.mongo_loader import MongoLoader

# --- MOCK DATA SAMPLES ---
# These simulate the JSON responses we expect from the abuse.ch APIs

MOCK_URLHAUS_RESPONSE = {
    "query_status": "ok",
    "urls": [
        {
            "id": "1", 
            "url": "http://evil.com/payload.exe", 
            "date_added": "2025-10-16 10:00:00 UTC", 
            "threat": "malware_download", 
            "tags": ["exe", "trojan"]
        },
        {
            "id": "2", 
            "url": "http://phish.com/login", 
            "date_added": "2025-10-16 11:00:00 UTC", 
            "threat": "phishing", 
            "tags": None
        }
    ]
}

MOCK_MALWAREBAZAAR_RESPONSE = {
    "query_status": "ok",
    "data": [
        {
            "sha256_hash": "aaa123456789abcdef...", 
            "first_seen": "1729084200", 
            "file_type": "exe", 
            "signature": "evil_malware", 
            "tags": ["rat"]
        },
        {
            "sha256_hash": "bbb987654321fedcba...", 
            "first_seen": "2025-10-16 12:00:00", 
            "file_type": "pdf", 
            "signature": None, 
            "tags": []
        }
    ]
}

# Disable application logging during tests for cleaner output
logging.disable(logging.CRITICAL)


class TestETLExtract(unittest.TestCase):
    """Tests for the data extraction module (connectors/abusech_api.py)"""

    def test_connector_init_with_valid_key(self):
        """Testing: Connector initializes successfully with valid API key."""
        print("\nTesting: Connector initialization with valid API key...")
        connector = AbuseCHConnector(api_key="valid_test_key")
        self.assertEqual(connector.headers['Auth-Key'], "valid_test_key")
        print("-> Passed.")

    def test_connector_init_with_invalid_key(self):
        """Testing: Connector raises ValueError with missing or placeholder API key."""
        print("\nTesting: Connector initialization with invalid API key...")
        with self.assertRaises(ValueError):
            AbuseCHConnector(api_key="")
        with self.assertRaises(ValueError):
            AbuseCHConnector(api_key="YOUR_API_KEY_HERE")
        print("-> Passed.")

    @patch('connectors.abusech_api.requests.get')
    def test_get_urlhaus_success(self, mock_get):
        """Testing: Successful extraction of URLhaus data from the API."""
        print("\nTesting: Successful URLhaus data extraction...")
        # Configure the mock to return a successful response with our fake data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_URLHAUS_RESPONSE
        mock_get.return_value = mock_response

        connector = AbuseCHConnector(api_key="fake_key")
        data = connector.get_urlhaus_recent()
        
        # Assertions
        self.assertIsNotNone(data)
        self.assertEqual(data['query_status'], 'ok')
        self.assertEqual(len(data['urls']), 2)
        self.assertEqual(data['urls'][0]['url'], 'http://evil.com/payload.exe')
        print("-> Passed.")

    @patch('connectors.abusech_api.requests.post')
    def test_get_malwarebazaar_success(self, mock_post):
        """Testing: Successful extraction of MalwareBazaar data from the API."""
        print("\nTesting: Successful MalwareBazaar data extraction...")
        # Configure the mock to return a successful response with our fake data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_MALWAREBAZAAR_RESPONSE
        mock_post.return_value = mock_response

        connector = AbuseCHConnector(api_key="fake_key")
        data = connector.get_malwarebazaar_recent()
        
        # Assertions
        self.assertIsNotNone(data)
        self.assertEqual(data['query_status'], 'ok')
        self.assertEqual(len(data['data']), 2)
        self.assertEqual(data['data'][0]['sha256_hash'], 'aaa123456789abcdef...')
        print("-> Passed.")

    @patch('connectors.abusech_api.requests.get')
    def test_get_urlhaus_api_error(self, mock_get):
        """Testing: The extractor handles an API connection error gracefully."""
        print("\nTesting: URLhaus API connection failure...")
        # Configure the mock to simulate a failed request (e.g., 403 Forbidden)
        mock_get.side_effect = requests.exceptions.HTTPError("403 Client Error")

        connector = AbuseCHConnector(api_key="fake_key")
        data = connector.get_urlhaus_recent()
        
        # Assertions
        self.assertIsNone(data)  # Should return None on failure
        print("-> Passed: Handled API error gracefully.")

    @patch('connectors.abusech_api.requests.post')
    def test_get_malwarebazaar_api_error(self, mock_post):
        """Testing: The extractor handles MalwareBazaar API connection error gracefully."""
        print("\nTesting: MalwareBazaar API connection failure...")
        # Configure the mock to simulate a failed request
        mock_post.side_effect = requests.exceptions.RequestException("Connection timed out")

        connector = AbuseCHConnector(api_key="fake_key")
        data = connector.get_malwarebazaar_recent()
        
        # Assertions
        self.assertIsNone(data)  # Should return None on failure
        print("-> Passed: Handled API error gracefully.")


class TestETLTransform(unittest.TestCase):
    """Tests for the data transformation module (transformations/data_transformer.py)"""

    def test_transform_urlhaus_data(self):
        """Testing: Correct transformation of raw URLhaus data."""
        print("\nTesting: Data transformation for URLhaus...")
        raw_data = MOCK_URLHAUS_RESPONSE
        transformed = standardize_urlhaus_data(raw_data)

        # Assertions
        self.assertEqual(len(transformed), 2)
        self.assertIn('_id', transformed[0])
        self.assertEqual(transformed[0]['source'], 'URLhaus')
        self.assertEqual(transformed[0]['ioc_type'], 'url')
        self.assertEqual(transformed[0]['ioc_value'], 'http://evil.com/payload.exe')
        self.assertEqual(transformed[0]['threat_type'], 'malware_download')
        self.assertEqual(transformed[0]['tags'], ['exe', 'trojan'])
        self.assertIsInstance(transformed[0]['first_seen'], datetime)
        print("-> Passed.")

    def test_transform_urlhaus_threat_level_logic(self):
        """Testing: Correct threat level calculation based on tags."""
        print("\nTesting: Threat level calculation for URLhaus...")
        raw_data = MOCK_URLHAUS_RESPONSE
        transformed = standardize_urlhaus_data(raw_data)
        
        # Test the calculated field 'threat_level'
        self.assertEqual(transformed[0]['threat_level'], 'high')  # Has 'exe' tag
        self.assertEqual(transformed[1]['threat_level'], 'medium')  # No 'exe' tag
        print("-> Passed.")

    def test_transform_malwarebazaar_data(self):
        """Testing: Correct transformation of MalwareBazaar data, including calculated fields."""
        print("\nTesting: Data transformation for MalwareBazaar...")
        raw_data = MOCK_MALWAREBAZAAR_RESPONSE
        transformed = standardize_malwarebazaar_data(raw_data)
        
        # Assertions
        self.assertEqual(len(transformed), 2)
        self.assertIn('_id', transformed[0])
        self.assertEqual(transformed[0]['source'], 'MalwareBazaar')
        self.assertEqual(transformed[0]['ioc_type'], 'hash_sha256')
        self.assertEqual(transformed[0]['ioc_value'], 'aaa123456789abcdef...')
        self.assertEqual(transformed[0]['signature'], 'evil_malware')
        self.assertEqual(transformed[0]['tags'], ['rat'])
        self.assertIsInstance(transformed[0]['first_seen'], datetime)
        print("-> Passed.")

    def test_transform_malwarebazaar_file_class_logic(self):
        """Testing: Correct file class calculation based on file type."""
        print("\nTesting: File class calculation for MalwareBazaar...")
        raw_data = MOCK_MALWAREBAZAAR_RESPONSE
        transformed = standardize_malwarebazaar_data(raw_data)
        
        # Test the calculated field 'file_class'
        self.assertEqual(transformed[0]['file_class'], 'executable')  # exe file
        self.assertEqual(transformed[1]['file_class'], 'document')  # pdf file
        print("-> Passed.")

    def test_transform_malwarebazaar_date_parsing(self):
        """Testing: Correct parsing of different date formats."""
        print("\nTesting: Date parsing for MalwareBazaar...")
        raw_data = MOCK_MALWAREBAZAAR_RESPONSE
        transformed = standardize_malwarebazaar_data(raw_data)
        
        # Test that both date formats were parsed correctly
        self.assertIsInstance(transformed[0]['first_seen'], datetime)  # From timestamp
        self.assertIsInstance(transformed[1]['first_seen'], datetime)  # From string
        print("-> Passed.")

    def test_transform_empty_data(self):
        """Testing: Transform functions handle empty or invalid data gracefully."""
        print("\nTesting: Handling of empty/invalid data...")
        
        # Test with None
        result = standardize_urlhaus_data(None)
        self.assertEqual(result, [])
        
        # Test with empty dict
        result = standardize_urlhaus_data({})
        self.assertEqual(result, [])
        
        # Test with missing 'urls' key
        result = standardize_urlhaus_data({'query_status': 'ok'})
        self.assertEqual(result, [])
        
        print("-> Passed.")


class TestETLLoad(unittest.TestCase):
    """Tests for the data loading module (database/mongo_loader.py)"""
    
    @patch('database.mongo_loader.MongoClient')
    def test_mongo_loader_init_success(self, mock_mongo_client):
        """Testing: MongoLoader initializes successfully with valid connection."""
        print("\nTesting: MongoLoader initialization with valid connection...")
        # Mock successful connection
        mock_client = MagicMock()
        mock_client.admin.command.return_value = {'ismaster': True}
        mock_db = MagicMock()
        mock_db.name = 'threat_intelligence'
        mock_client.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client
        
        loader = MongoLoader(uri="mongodb://localhost:27017")
        
        # Assertions
        self.assertIsNotNone(loader.client)
        self.assertEqual(loader.db.name, 'threat_intelligence')
        print("-> Passed.")

    @patch('database.mongo_loader.MongoClient')
    def test_mongo_loader_init_connection_failure(self, mock_mongo_client):
        """Testing: MongoLoader handles connection failure gracefully."""
        print("\nTesting: MongoLoader initialization with connection failure...")
        # Simulate connection failure
        from pymongo.errors import ConnectionFailure
        mock_mongo_client.side_effect = ConnectionFailure("Could not connect to MongoDB")
        
        loader = MongoLoader(uri="mongodb://invalid:27017")
        
        # Assertions
        self.assertIsNone(loader.client)
        print("-> Passed: Handled connection failure gracefully.")

    @patch('database.mongo_loader.MongoClient')
    def test_upsert_data_success(self, mock_mongo_client):
        """Testing: Correct data upsert into MongoDB."""
        print("\nTesting: Correct data upsert into MongoDB...")
        # Mock the entire MongoDB connection and collection objects
        mock_collection = MagicMock()
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_client = MagicMock()
        mock_client.admin.command.return_value = {'ismaster': True}
        mock_client.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client
        
        loader = MongoLoader(uri="mongodb://localhost:27017")
        test_data = standardize_urlhaus_data(MOCK_URLHAUS_RESPONSE)
        loader.upsert_data('urlhaus_iocs', test_data)
        
        # Assertions
        # Check if the correct collection was accessed
        mock_db.__getitem__.assert_called_with('urlhaus_iocs')
        # Check if update_one was called for each record
        self.assertEqual(mock_collection.update_one.call_count, 2)
        print("-> Passed.")

    @patch('database.mongo_loader.MongoClient')
    def test_upsert_data_with_no_client(self, mock_mongo_client):
        """Testing: Upsert handles case when client is None."""
        print("\nTesting: Upsert with no client connection...")
        # Simulate connection failure during init
        from pymongo.errors import ConnectionFailure
        mock_mongo_client.side_effect = ConnectionFailure("Could not connect")
        
        loader = MongoLoader(uri="mongodb://invalid:27017")
        test_data = standardize_urlhaus_data(MOCK_URLHAUS_RESPONSE)
        
        # This should not raise an exception
        loader.upsert_data('urlhaus_iocs', test_data)
        print("-> Passed: Handled no client gracefully.")

    @patch('database.mongo_loader.MongoClient')
    def test_upsert_data_with_empty_data(self, mock_mongo_client):
        """Testing: Upsert handles empty data gracefully."""
        print("\nTesting: Upsert with empty data...")
        # Mock successful connection
        mock_client = MagicMock()
        mock_client.admin.command.return_value = {'ismaster': True}
        mock_mongo_client.return_value = mock_client
        
        loader = MongoLoader(uri="mongodb://localhost:27017")
        
        # Test with empty list
        loader.upsert_data('urlhaus_iocs', [])
        
        # Test with None
        loader.upsert_data('urlhaus_iocs', None)
        
        print("-> Passed: Handled empty data gracefully.")

    @patch('database.mongo_loader.MongoClient')
    def test_close_connection(self, mock_mongo_client):
        """Testing: Connection closure works correctly."""
        print("\nTesting: Connection closure...")
        # Mock successful connection
        mock_client = MagicMock()
        mock_client.admin.command.return_value = {'ismaster': True}
        mock_mongo_client.return_value = mock_client
        
        loader = MongoLoader(uri="mongodb://localhost:27017")
        loader.close_connection()
        
        # Assertions
        mock_client.close.assert_called_once()
        print("-> Passed.")


class TestETLIntegration(unittest.TestCase):
    """Integration tests for the complete ETL pipeline"""

    @patch('database.mongo_loader.MongoClient')
    @patch('connectors.abusech_api.requests.post')
    @patch('connectors.abusech_api.requests.get')
    def test_complete_etl_pipeline(self, mock_get, mock_post, mock_mongo_client):
        """Testing: Complete ETL pipeline from extraction to loading."""
        print("\nTesting: Complete ETL pipeline...")
        
        # Mock API responses
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = MOCK_URLHAUS_RESPONSE
        mock_get.return_value = mock_get_response
        
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = MOCK_MALWAREBAZAAR_RESPONSE
        mock_post.return_value = mock_post_response
        
        # Mock MongoDB connection
        mock_collection = MagicMock()
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_client = MagicMock()
        mock_client.admin.command.return_value = {'ismaster': True}
        mock_client.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client
        
        # Run the pipeline
        connector = AbuseCHConnector(api_key="test_key")
        loader = MongoLoader(uri="mongodb://localhost:27017")
        
        # URLhaus ETL
        urlhaus_raw = connector.get_urlhaus_recent()
        if urlhaus_raw:
            urlhaus_transformed = standardize_urlhaus_data(urlhaus_raw)
            loader.upsert_data('urlhaus_iocs', urlhaus_transformed)
        
        # MalwareBazaar ETL
        malwarebazaar_raw = connector.get_malwarebazaar_recent()
        if malwarebazaar_raw:
            malwarebazaar_transformed = standardize_malwarebazaar_data(malwarebazaar_raw)
            loader.upsert_data('malwarebazaar_iocs', malwarebazaar_transformed)
        
        loader.close_connection()
        
        # Assertions
        self.assertIsNotNone(urlhaus_raw)
        self.assertIsNotNone(malwarebazaar_raw)
        self.assertEqual(len(urlhaus_transformed), 2)
        self.assertEqual(len(malwarebazaar_transformed), 2)
        self.assertEqual(mock_collection.update_one.call_count, 4)  # 2 for each collection
        print("-> Passed.")


if __name__ == '__main__':
    unittest.main()