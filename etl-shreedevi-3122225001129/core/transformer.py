from core.utils import log, timestamp

def transform_data(data, feed_name):
    if not data:
        log(f"No data to transform for {feed_name}")
        return []

    transformed = []

    # case 1: list of dicts (normal CVE data)
    if isinstance(data, list) and all(isinstance(i, dict) for i in data):
        for item in data:
            doc = {
                "cve_id": item.get("id", "N/A"),
                "summary": item.get("summary", ""),
                "cvss": item.get("cvss", None),
                "published": item.get("Published", None),
                "modified": item.get("Modified", None),
                "source": feed_name,
                "ingested_at": timestamp()
            }
            transformed.append(doc)

    # case 2: dict with nested structure (like dbInfo or vendor browse)
    elif isinstance(data, dict):
        if "vendor" in data:
            for product in data.get("product", []):
                transformed.append({
                    "vendor": data["vendor"],
                    "product": product,
                    "source": feed_name,
                    "ingested_at": timestamp()
                })
        else:
            transformed.append({
                "feed_name": feed_name,
                "data": data,
                "ingested_at": timestamp()
            })

    # case 3: list of strings (like vendor list)
    elif isinstance(data, list) and all(isinstance(i, str) for i in data):
        for entry in data:
            transformed.append({
                "entry": entry,
                "source": feed_name,
                "ingested_at": timestamp()
            })

    log(f"Transformed {len(transformed)} records for {feed_name}")
    return transformed
