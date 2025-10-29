import requests

class TorExitNodeExtractor:
    """Extracts raw Tor exit node data from the Tor Project."""

    URL = "https://check.torproject.org/exit-addresses"

    def fetch_data(self):
        """Fetch the Tor exit node list from the official source."""
        response = requests.get(self.URL, timeout=10)
        response.raise_for_status()
        return response.text
