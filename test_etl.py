#!/usr/bin/env python3
"""
Test script for CIRCL Passive DNS ETL Connector
==============================================

This script provides basic testing functionality for the ETL pipeline.
It validates the connector initialization and basic functionality.

Author: Kavin (Roll Number: 302004)
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from etl_connector import CIRCLPassiveDNSConnector, CIRCLPassiveDNSError


class TestCIRCLPassiveDNSConnector(unittest.TestCase):
    """Test cases for CIRCL Passive DNS ETL Connector."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock environment variables
        self.env_vars = {
            'CIRCL_USERNAME': 'test_user',
            'CIRCL_PASSWORD': 'test_pass',
            'CIRCL_BASE_URL': 'https://test.circl.lu',
            'MONGODB_URI': 'mongodb://localhost:27017/',
            'MONGODB_DATABASE': 'test_db',
            'MONGODB_COLLECTION': 'test_collection',
            'API_TIMEOUT': '30',
            'MAX_RETRIES': '3'
        }
        
        # Patch environment variables
        self.env_patcher = patch.dict(os.environ, self.env_vars)
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up after tests."""
        self.env_patcher.stop()
    
    def test_connector_initialization(self):
        """Test connector initialization with valid credentials."""
        try:
            connector = CIRCLPassiveDNSConnector()
            self.assertEqual(connector.username, 'test_user')
            self.assertEqual(connector.password, 'test_pass')
            self.assertEqual(connector.base_url, 'https://test.circl.lu')
            self.assertEqual(connector.mongodb_database, 'test_db')
            self.assertEqual(connector.mongodb_collection, 'test_collection')
            print("✅ Connector initialization test passed")
        except Exception as e:
            self.fail(f"Connector initialization failed: {e}")
    
    def test_missing_credentials(self):
        """Test connector initialization with missing credentials."""
        # Remove credentials from environment
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                CIRCLPassiveDNSConnector()
        print("✅ Missing credentials test passed")
    
    @patch('pymongo.MongoClient')
    def test_mongodb_connection_success(self, mock_mongo_client):
        """Test successful MongoDB connection."""
        # Mock successful MongoDB connection
        mock_client = MagicMock()
        mock_client.admin.command.return_value = True
        mock_mongo_client.return_value = mock_client
        
        connector = CIRCLPassiveDNSConnector()
        result = connector.connect_mongodb()
        
        self.assertTrue(result)
        print("✅ MongoDB connection success test passed")
    
    @patch('pymongo.MongoClient')
    def test_mongodb_connection_failure(self, mock_mongo_client):
        """Test MongoDB connection failure."""
        # Mock MongoDB connection failure
        from pymongo.errors import ConnectionFailure
        mock_mongo_client.side_effect = ConnectionFailure("Connection failed")
        
        connector = CIRCLPassiveDNSConnector()
        result = connector.connect_mongodb()
        
        self.assertFalse(result)
        print("✅ MongoDB connection failure test passed")
    
    def test_clean_record(self):
        """Test record cleaning functionality."""
        connector = CIRCLPassiveDNSConnector()
        
        # Test record with various data types
        test_record = {
            'rrname': '  example.com  ',
            'rrtype': 'A',
            'rdata': '192.168.1.1',
            'count': '150',
            'time_first': 1640995200,  # Unix timestamp
            'time_last': None,
            'bailiwick': ''
        }
        
        cleaned = connector._clean_record(test_record)
        
        # Check string fields are stripped
        self.assertEqual(cleaned['rrname'], 'example.com')
        self.assertEqual(cleaned['bailiwick'], '')
        
        # Check count is converted to int
        self.assertEqual(cleaned['count'], 150)
        
        # Check timestamp conversion
        self.assertIsNotNone(cleaned['time_first'])
        self.assertIsNone(cleaned['time_last'])
        
        print("✅ Record cleaning test passed")
    
    @patch('requests.Session.get')
    def test_api_request_success(self, mock_get):
        """Test successful API request."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'rrname': 'example.com',
                'rrtype': 'A',
                'rdata': '192.168.1.1',
                'time_first': '2024-01-01T00:00:00Z',
                'time_last': '2024-12-01T00:00:00Z',
                'count': 100,
                'bailiwick': 'example.com'
            }
        ]
        mock_get.return_value = mock_response
        
        connector = CIRCLPassiveDNSConnector()
        data = connector.extract_data('example.com', limit=10)
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['rrname'], 'example.com')
        print("✅ API request success test passed")
    
    @patch('requests.Session.get')
    def test_api_request_authentication_failure(self, mock_get):
        """Test API request with authentication failure."""
        # Mock authentication failure
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        connector = CIRCLPassiveDNSConnector()
        
        with self.assertRaises(CIRCLPassiveDNSError):
            connector.extract_data('example.com')
        print("✅ API authentication failure test passed")
    
    def test_transform_data(self):
        """Test data transformation."""
        connector = CIRCLPassiveDNSConnector()
        
        raw_data = [
            {
                'rrname': 'example.com',
                'rrtype': 'A',
                'rdata': '192.168.1.1',
                'time_first': '2024-01-01T00:00:00Z',
                'time_last': '2024-12-01T00:00:00Z',
                'count': 100,
                'bailiwick': 'example.com'
            }
        ]
        
        transformed = connector.transform_data(raw_data)
        
        self.assertEqual(len(transformed), 1)
        self.assertIn('ingestion_timestamp', transformed[0])
        self.assertIn('source', transformed[0])
        self.assertEqual(transformed[0]['source'], 'circl_passive_dns')
        self.assertEqual(transformed[0]['rrname'], 'example.com')
        
        print("✅ Data transformation test passed")
    
    @patch('pymongo.MongoClient')
    def test_load_data_success(self, mock_mongo_client):
        """Test successful data loading."""
        # Mock MongoDB collection
        mock_collection = MagicMock()
        mock_collection.insert_many.return_value = MagicMock(inserted_ids=[1, 2, 3])
        
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        
        mock_client = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client
        
        connector = CIRCLPassiveDNSConnector()
        connector.mongo_collection = mock_collection
        
        test_data = [
            {
                'ingestion_timestamp': '2024-12-01T10:00:00Z',
                'source': 'circl_passive_dns',
                'rrname': 'example.com',
                'rrtype': 'A',
                'rdata': '192.168.1.1'
            }
        ]
        
        result = connector.load_data(test_data)
        self.assertTrue(result)
        print("✅ Data loading success test passed")


def run_basic_validation():
    """Run basic validation tests without external dependencies."""
    print("🧪 Running basic validation tests...")
    print("=" * 50)
    
    # Test 1: Environment variable loading
    print("Test 1: Environment variable loading")
    try:
        load_dotenv()
        print("✅ Environment variables loaded successfully")
    except Exception as e:
        print(f"❌ Environment variable loading failed: {e}")
        return False
    
    # Test 2: Module import
    print("\nTest 2: Module import")
    try:
        from etl_connector import CIRCLPassiveDNSConnector, CIRCLPassiveDNSError
        print("✅ ETL connector module imported successfully")
    except Exception as e:
        print(f"❌ Module import failed: {e}")
        return False
    
    # Test 3: Class instantiation (with mocked environment)
    print("\nTest 3: Class instantiation")
    try:
        with patch.dict(os.environ, {
            'CIRCL_USERNAME': 'test',
            'CIRCL_PASSWORD': 'test'
        }):
            connector = CIRCLPassiveDNSConnector()
            print("✅ Connector class instantiated successfully")
    except Exception as e:
        print(f"❌ Class instantiation failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All basic validation tests passed!")
    return True


if __name__ == "__main__":
    print("🚀 CIRCL Passive DNS ETL Connector - Test Suite")
    print("=" * 60)
    
    # Run basic validation first
    if not run_basic_validation():
        print("❌ Basic validation failed. Exiting.")
        sys.exit(1)
    
    # Run unit tests
    print("\n🧪 Running unit tests...")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestCIRCLPassiveDNSConnector)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("🎉 All tests passed successfully!")
        print("\n📋 Test Summary:")
        print(f"   Tests run: {result.testsRun}")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
    else:
        print("❌ Some tests failed!")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
        sys.exit(1)
    
    print("\n🎯 ETL Connector is ready for use!")
    print("📖 See README.md for usage instructions.")

