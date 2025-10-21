from etl_connector import transform

def test_transform_logic():
    raw_data = [
        "192.168.0.1",    # valid IP
        "192.168.0.0/24", # valid CIDR
        "invalid_ip",     # invalid
        "192.168.0.1"     # duplicate
    ]
    transformed = transform(raw_data)

    # Assertions
    assert len(transformed) == 2, "Invalid or duplicate filtering failed"
    ip_record = next(r for r in transformed if r["type"] == "ip")
    cidr_record = next(r for r in transformed if r["type"] == "cidr")

    assert ip_record["ip"] == "192.168.0.1"
    assert cidr_record["ip"] == "192.168.0.0/24"

    print("Validation test passed.")

if __name__ == "__main__":
    test_transform_logic()
