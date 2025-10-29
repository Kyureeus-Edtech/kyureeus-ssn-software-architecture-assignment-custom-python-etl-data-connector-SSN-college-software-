import pytest
from etl_connector.extractor import TorExitNodeExtractor

def test_fetch_data(monkeypatch):
    """Test data extraction from URL."""
    class MockResponse:
        def __init__(self, text): self.text = text
        def raise_for_status(self): pass

    def mock_get(url, timeout):
        return MockResponse("ExitAddress 1.1.1.1 2025-10-29")

    monkeypatch.setattr("requests.get", mock_get)
    extractor = TorExitNodeExtractor()
    data = extractor.fetch_data()
    assert "ExitAddress" in data
