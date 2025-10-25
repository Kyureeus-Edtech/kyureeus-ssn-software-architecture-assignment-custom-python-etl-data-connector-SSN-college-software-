def transform_info(data):
    """Extract only relevant info fields."""
    return {
        "engineVersion": data.get("engineVersion"),
        "criteriaVersion": data.get("criteriaVersion"),
        "maxAssessments": data.get("maxAssessments"),
    }

def transform_analysis(data):
    """Extract host, grade, protocols, etc."""
    results = []
    host = data.get("host")
    for ep in data.get("endpoints", []):
        details = ep.get("details", {})
        results.append({
            "host": host,
            "ipAddress": ep.get("ipAddress"),
            "grade": ep.get("grade"),
            "protocols": [p.get("name") + " " + str(p.get("version")) for p in details.get("protocols", [])],
            "forwardSecrecy": details.get("forwardSecrecy"),
            "certIssuer": details.get("cert", {}).get("issuerSubject"),
            "notAfter": details.get("cert", {}).get("notAfter"),
        })
    return results

def transform_endpoint(data):
    """Simplify endpoint data for clarity."""
    return {
        "host": data.get("host"),
        "ipAddress": data.get("ipAddress"),
        "serverName": data.get("serverName"),
        "statusMessage": data.get("statusMessage"),
        "detailsKeys": list(data.get("details", {}).keys()) if data.get("details") else []
    }
