import pytest
from etl_connector.loader import TorExitNodeLoader

class MockCollection:
    def insert_many(self, data):
        return type('MockInsertResult', (object,), {"inserted_ids": range(len(data))})

class MockDB:
    def __getitem__(self, name):
        return MockCollection()

class MockClient:
    def __getitem__(self, name):
        return MockDB()

def test_save_to_mongodb(monkeypatch):
    data = [{"ip": "1.1.1.1", "timestamp": "2025-10-29"}]

    def mock_client(uri):
        return MockClient()

    monkeypatch.setattr("etl_connector.loader.MongoClient", mock_client)
    loader = TorExitNodeLoader()
    inserted = loader.save_to_mongodb(data)
    assert inserted == 1
