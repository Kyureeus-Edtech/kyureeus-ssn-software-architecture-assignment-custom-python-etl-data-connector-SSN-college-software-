def transform(data, limit=None):
    if isinstance(data, dict) and "results" in data:
        records = data["results"]
    elif isinstance(data, list):
        records = data
    else:
        records = [data]
    if limit:
        return records[:limit]
    return records