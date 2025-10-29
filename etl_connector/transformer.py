import re

class TorExitNodeTransformer:
    """Transforms raw Tor data into structured dictionary objects."""

    def parse_exit_nodes(self, raw_data):
        """Parse Tor exit node text into a list of dictionaries."""
        exit_nodes = []
        node_entries = raw_data.strip().split("\n")
        for line in node_entries:
            if line.startswith("ExitAddress"):
                parts = re.split(r"\s+", line)
                if len(parts) >= 3:
                    exit_nodes.append({
                        "ip": parts[1],
                        "timestamp": parts[2]
                    })
        return exit_nodes
