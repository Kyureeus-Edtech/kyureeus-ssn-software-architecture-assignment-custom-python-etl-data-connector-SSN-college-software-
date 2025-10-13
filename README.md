# 🕵️‍♂️ GreyNoise Full ETL Pipeline

This project is a **Python-based ETL (Extract, Transform, Load) pipeline** for fetching data from the **[GreyNoise API](https://docs.greynoise.io/reference/)** and storing it in a **MongoDB** database for further analysis or threat intelligence processing.

---

## 📘 Overview

The script automates the following steps:

1. **Extract** — Retrieves data from multiple GreyNoise API endpoints (like `ping`, `community_ip`, `ip_context`, etc.).
2. **Transform** — Optionally normalizes or filters the fetched data (placeholder for custom logic).
3. **Load** — Inserts the structured data and metadata into a MongoDB collection with timestamp and source tracking.

Each API response is stored in MongoDB along with metadata such as:
- The endpoint name
- Request parameters
- Status code
- Time of retrieval

---

## ⚙️ Features

- Supports multiple GreyNoise modules/endpoints in one run.
- Modular ETL architecture — easy to extend with more endpoints.
- Built-in logging for monitoring and debugging.
- Secure configuration using environment variables.
- MongoDB integration with error handling.
- Easily customizable for your organization’s threat intelligence workflows.

---

## 🧩 Endpoints Used

By default, the following **GreyNoise API v3** endpoints are included:

| Module Name        | Path | Description |
|--------------------|------|--------------|
| `ping`             | `/v3/ping` | Checks API connectivity |
| `community_ip`     | `/v3/community/{ip}` | Fetches GreyNoise community data for a given IP |
| `ip_context`       | `/v3/ip/{ip}` | Retrieves full context for a specific IP |
| `gnql_query`       | `/v3/gnql/query` | Performs GNQL search query (default: `last_seen:1d`) |
| `gnql_stats`       | `/v3/gnql/stats` | Returns aggregated stats for a GNQL query |
| `ip_timeline_daily`| `/v3/noise/ips/{ip}/daily-summary` | Gets a daily summary timeline for an IP |
| `ip_similarity`    | `/v3/ip/similar/{ip}` | Finds IPs similar to the given one |
| `tag_metadata`     | `/v3/tags` | Lists GreyNoise tag metadata |

> You can easily add more endpoints by editing the `ENDPOINTS` dictionary in the script.

---

## 🧰 Requirements

### 🐍 Python Version
- **Python 3.8 or higher**

### 📦 Python Libraries
Install the dependencies using pip:
```bash
pip install -r requirements.txt
