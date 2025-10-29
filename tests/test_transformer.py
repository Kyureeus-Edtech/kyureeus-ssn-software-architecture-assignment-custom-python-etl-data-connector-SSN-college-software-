from etl_connector.transformer import TorExitNodeTransformer

def test_parse_exit_nodes():
    raw_data = "ExitAddress 1.1.1.1 2025-10-29\nExitAddress 2.2.2.2 2025-10-29"
    transformer = TorExitNodeTransformer()
    nodes = transformer.parse_exit_nodes(raw_data)
    assert len(nodes) == 2
    assert nodes[0]["ip"] == "1.1.1.1"
