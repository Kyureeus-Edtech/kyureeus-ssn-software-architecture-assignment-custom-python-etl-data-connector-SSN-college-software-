#!/usr/bin/env python3
"""
Unit tests for MalShare ETL Connector
Author: [Shivakumaar] - [3122225001312]
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
import json
import pytest
from requests.exceptions import RequestException, HTTPError

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from etl_connector import MalShareETLConnector

class TestMalShareETLConnector(unittest.TestCase):
    """Test cases for MalShare ETL Connector"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'MALSHARE_API_KEY': 'test_api_key_123',
            'MALSHARE_BASE_URL': 'https://malshare.com',
            'MONGODB_URI': 'mongodb://localhost:27017/',
            'MONGODB_DATABASE': 'test_malware_db',
            'SAMPLE_LIMIT': '10',
            'RATE_LIMIT_DELAY': '0.1',
            'MAX_RETRIES': '2',
            'REQUEST_TIMEOUT': '10'
        })
        self.env_patcher.start()
        
        # Mock MongoDB connection
        self.mongo_patcher = patch('etl_connector.MongoClient')
        self.mock_mongo_client = self.mongo_patcher.start()
        self.mock_collection = Mock()
        self.mock_db = Mock()
        self.mock_db.__getitem__.return_value = self.mock_collection
        self.mock_mongo_client.return_value.__getitem__.return_value = self.mock_db
        
        # Sample test data
        self.sample_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        self.sample_api_response = {
            "MD5": "d41d8cd98f00b204e9800998ecf8427e",
            "SHA1": "da39a3ee5e6b4b0d3255bfef95601890afd80709", 
            "SHA256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "SSDEEP": "3::",
            "F_TYPE": "PE32 executable",
            "SOURCES": ["virustotal"],
            "ADDED": "2024-01-15 10:30:00"
        }
        
        self.sample_list_response = {
            "data": [
                "hash1",
                "hash2", 
                "hash3",
                ""  # Empty line to test filtering
            ]
        }
    
    def tearDown(self):
        """Clean up after each test method."""
        self.env_patcher.stop()
        self.mongo_patcher.stop()
    
    def test_init_success(self):
        """Test successful initialization of connector"""
        connector = MalShareETLConnector()
        
        self.assertEqual(connector.api_key, 'test_api_key_123')
        self.assertEqual(connector.base_url, 'https://malshare.com')
        self.assertEqual(connector.db_name, 'test_malware_db')
        self.assertEqual(connector.collection_name, 'malshare_raw')
    
    def test_init_missing_api_key(self):
        """Test initialization failure when API key is missing"""
        with patch.dict(os.environ, {'MALSHARE_API_KEY': ''}, clear=True):
            with self.assertRaises(ValueError) as context:
                MalShareETLConnector()
            self.assertIn("MALSHARE_API_KEY is required", str(context.exception))
    
    @patch('etl_connector.requests.get')
    def test_make_api_request_success(self, mock_get):
        """Test successful API request"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = self.sample_api_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        connector = MalShareETLConnector()
        result = connector._make_api_request('details', {'hash': self.sample_hash})
        
        self.assertEqual(result, self.sample_api_response)
        mock_get.assert_called_once()
    
    @patch('etl_connector.requests.get')
    def test_make_api_request_text_response(self, mock_get):
        """Test API request with text response (like getlist)"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/plain'}
        mock_response.text = "hash1\nhash2\nhash3\n"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        connector = MalShareETLConnector()
        result = connector._make_api_request('getlist')
        
        expected = {'data': ['hash1', 'hash2', 'hash3']}
        self.assertEqual(result, expected)
    
    @patch('etl_connector.requests.get')
    def test_make_api_request_rate_limit(self, mock_get):
        """Test handling of rate limit (429) responses"""
        # Setup mock responses - first rate limited, then success
        rate_limit_response = Mock()
        rate_limit_response.status_code = 429
        rate_limit_response.raise_for_status.side_effect = HTTPError("429 Rate Limited")
        
        success_response = Mock()
        success_response.status_code = 200
        success_response.headers = {'content-type': 'application/json'}
        success_response.json.return_value = self.sample_api_response
        success_response.raise_for_status.return_value = None
        
        mock_get.side_effect = [rate_limit_response, success_response]
        
        connector = MalShareETLConnector()
        with patch('etl_connector.time.sleep') as mock_sleep:
            result = connector._make_api_request('details', {'hash': self.sample_hash})
        
        self.assertEqual(result, self.sample_api_response)
        mock_sleep.assert_called()  # Should have slept due to rate limit
        self.assertEqual(mock_get.call_count, 2)  # Two calls - one failed, one success
    
    @patch('etl_connector.requests.get')
    def test_make_api_request_max_retries_exceeded(self, mock_get):
        """Test behavior when max retries are exceeded"""
        mock_get.side_effect = RequestException("Network error")
        
        connector = MalShareETLConnector()
        with patch('etl_connector.time.sleep'):
            result = connector._make_api_request('details', {'hash': self.sample_hash})
        
        self.assertIsNone(result)
        self.assertEqual(mock_get.call_count, connector.max_retries)
    
    @patch('etl_connector.MalShareETLConnector._make_api_request')
    def test_extract_sample_list_success(self, mock_api_request):
        """Test successful extraction of sample list"""
        mock_api_request.return_value = self.sample_list_response
        
        connector = MalShareETLConnector()
        result = connector.extract_sample_list(limit=10)
        
        expected = ['hash1', 'hash2', 'hash3']  # Empty string should be filtered
        self.assertEqual(result, expected)
        mock_api_request.assert_called_once_with('getlist')
    
    @patch('etl_connector.MalShareETLConnector._make_api_request')
    def test_extract_sample_list_failure(self, mock_api_request):
        """Test extraction failure when API request fails"""
        mock_api_request.return_value = None
        
        connector = MalShareETLConnector()
        result = connector.extract_sample_list()
        
        self.assertEqual(result, [])
    
    @patch('etl_connector.MalShareETLConnector._make_api_request')
    def test_extract_sample_details_success(self, mock_api_request):
        """Test successful extraction of sample details"""
        mock_api_request.return_value = self.sample_api_response
        
        connector = MalShareETLConnector()
        result = connector.extract_sample_details(self.sample_hash)
        
        self.assertEqual(result, self.sample_api_response)
        mock_api_request.assert_called_once_with('details', {'hash': self.sample_hash})
    
    @patch('etl_connector.MalShareETLConnector._make_api_request')
    def test_extract_sample_details_failure(self, mock_api_request):
        """Test extraction failure for sample details"""
        mock_api_request.return_value = None
        
        connector = MalShareETLConnector()
        result = connector.extract_sample_details(self.sample_hash)
        
        self.assertIsNone(result)
    
    def test_transform_data_success(self):
        """Test successful data transformation"""
        connector = MalShareETLConnector()
        
        with patch('etl_connector.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.strptime = datetime.strptime  # Keep original strptime
            
            result = connector.transform_data(self.sample_api_response, self.sample_hash)
        
        # Check essential fields
        self.assertEqual(result['sha256'], self.sample_hash)
        self.assertEqual(result['source'], 'malshare_api')
        self.assertEqual(result['connector_version'], '1.0')
        self.assertEqual(result['md5'], 'd41d8cd98f00b204e9800998ecf8427e')
        self.assertEqual(result['file_type'], 'PE32 executable')
        self.assertEqual(result['sample_type'], 'executable')
        self.assertIn('data_completeness', result)
        self.assertIn('raw_response', result)
    
    def test_transform_data_type_classification(self):
        """Test sample type classification in transformation"""
        connector = MalShareETLConnector()
        
        # Test PDF classification
        pdf_response = self.sample_api_response.copy()
        pdf_response['F_TYPE'] = 'PDF document'
        
        result = connector.transform_data(pdf_response, self.sample_hash)
        self.assertEqual(result['sample_type'], 'document')
        
        # Test ZIP classification
        zip_response = self.sample_api_response.copy()
        zip_response['F_TYPE'] = 'ZIP archive'
        
        result = connector.transform_data(zip_response, self.sample_hash)
        self.assertEqual(result['sample_type'], 'archive')
        
        # Test unknown classification
        unknown_response = self.sample_api_response.copy()
        unknown_response['F_TYPE'] = 'Unknown file type'
        
        result = connector.transform_data(unknown_response, self.sample_hash)
        self.assertEqual(result['sample_type'], 'unknown')
    
    def test_calculate_completeness(self):
        """Test data completeness calculation"""
        connector = MalShareETLConnector()
        
        # Test complete data
        completeness = connector._calculate_completeness(self.sample_api_response)
        self.assertEqual(completeness, 1.0)  # All expected fields present
        
        # Test partial data
        partial_data = {
            'MD5': 'hash',
            'SHA1': 'hash',
            # Missing SHA256, F_TYPE, ADDED
        }
        completeness = connector._calculate_completeness(partial_data)
        self.assertEqual(completeness, 0.4)  # 2 out of 5 fields
        
        # Test empty data
        completeness = connector._calculate_completeness({})
        self.assertEqual(completeness, 0.0)
    
    def test_load_data_success(self):
        """Test successful data loading to MongoDB"""
        # Setup mock collection
        mock_result = Mock()
        mock_result.upserted_id = 'new_id'
        mock_result.modified_count = 0
        self.mock_collection.replace_one.return_value = mock_result
        
        connector = MalShareETLConnector()
        
        test_data = {
            'sha256': self.sample_hash,
            'source': 'test',
            'ingestion_timestamp': datetime.now(timezone.utc)
        }
        
        result = connector.load_data(test_data)
        
        self.assertTrue(result)
        self.mock_collection.replace_one.assert_called_once()
    
    def test_load_data_failure(self):
        """Test data loading failure"""
        # Setup mock to raise exception
        self.mock_collection.replace_one.side_effect = Exception("Database error")
        
        connector = MalShareETLConnector()
        
        test_data = {
            'sha256': self.sample_hash,
            'source': 'test',
            'ingestion_timestamp': datetime.now(timezone.utc)
        }
        
        result = connector.load_data(test_data)
        
        self.assertFalse(result)
    
    def test_get_collection_stats_success(self):
        """Test getting collection statistics"""
        # Setup mock collection methods
        self.mock_collection.count_documents.return_value = 100
        self.mock_collection.aggregate.return_value = [
            {'_id': 'executable', 'count': 60},
            {'_id': 'document', 'count': 40}
        ]
        self.mock_collection.find_one.return_value = {
            'ingestion_timestamp': datetime.now(timezone.utc)
        }
        self.mock_db.command.return_value = {'size': 1024000}
        
        connector = MalShareETLConnector()
        stats = connector.get_collection_stats()
        
        self.assertEqual(stats['total_documents'], 100)
        self.assertEqual(len(stats['sample_types']), 2)
        self.assertIn('latest_ingestion', stats)
        self.assertEqual(stats['collection_size'], 1024000)
    
    def test_get_collection_stats_failure(self):
        """Test collection stats failure"""
        self.mock_collection.count_documents.side_effect = Exception("DB Error")
        
        connector = MalShareETLConnector()
        stats = connector.get_collection_stats()
        
        self.assertEqual(stats, {})
    
    @patch('etl_connector.MalShareETLConnector.extract_sample_list')
    @patch('etl_connector.MalShareETLConnector.extract_sample_details')
    @patch('etl_connector.MalShareETLConnector.load_data')
    @patch('etl_connector.time.sleep')
    def test_run_etl_pipeline_success(self, mock_sleep, mock_load, mock_details, mock_list):
        """Test successful ETL pipeline execution"""
        # Setup mocks
        mock_list.return_value = ['hash1', 'hash2']
        mock_details.return_value = self.sample_api_response
        mock_load.return_value = True
        
        connector = MalShareETLConnector()
        
        # Should not raise exception
        connector.run_etl_pipeline(sample_limit=2)
        
        # Verify calls
        mock_list.assert_called_once_with(2)
        self.assertEqual(mock_details.call_count, 2)
        self.assertEqual(mock_load.call_count, 2)
    
    @patch('etl_connector.MalShareETLConnector.extract_sample_list')
    def test_run_etl_pipeline_no_samples(self, mock_list):
        """Test ETL pipeline when no samples are extracted"""
        mock_list.return_value = []
        
        connector = MalShareETLConnector()
        
        # Should handle gracefully
        connector.run_etl_pipeline()
        
        mock_list.assert_called_once()


class TestIntegration(unittest.TestCase):
    """Integration tests that test multiple components together"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.env_patcher = patch.dict(os.environ, {
            'MALSHARE_API_KEY': 'test_key',
            'MONGODB_URI': 'mongodb://localhost:27017/',
            'RATE_LIMIT_DELAY': '0.1'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up integration test environment"""
        self.env_patcher.stop()
    
    @patch('etl_connector.MongoClient')
    @patch('etl_connector.requests.get')
    def test_full_etl_flow_integration(self, mock_get, mock_mongo):
        """Test complete ETL flow integration"""
        # Setup API responses
        list_response = Mock()
        list_response.status_code = 200
        list_response.headers = {'content-type': 'text/plain'}
        list_response.text = "hash1\nhash2"
        list_response.raise_for_status.return_value = None
        
        details_response = Mock()
        details_response.status_code = 200
        details_response.headers = {'content-type': 'application/json'}
        details_response.json.return_value = {
            'MD5': 'test_md5',
            'F_TYPE': 'PE32 executable',
            'ADDED': '2024-01-15 10:30:00'
        }
        details_response.raise_for_status.return_value = None
        
        mock_get.side_effect = [list_response, details_response, details_response]
        
        # Setup MongoDB mock
        mock_collection = Mock()
        mock_db = Mock()
        mock_db.__getitem__.return_value = mock_collection
        mock_mongo.return_value.__getitem__.return_value = mock_db
        
        mock_result = Mock()
        mock_result.upserted_id = 'test_id'
        mock_result.modified_count = 0
        mock_collection.replace_one.return_value = mock_result
        
        # Run integration test
        connector = MalShareETLConnector()
        
        with patch('etl_connector.time.sleep'):
            connector.run_etl_pipeline(sample_limit=2)
        
        # Verify the flow
        self.assertEqual(mock_get.call_count, 3)  # 1 list + 2 details calls
        self.assertEqual(mock_collection.replace_one.call_count, 2)  # 2 inserts


if __name__ == '__main__':
    # Set up test environment
    os.environ.setdefault('MALSHARE_API_KEY', 'test_key')
    
    # Run tests
    unittest.main(verbosity=2)