# DShield Top Attackers – Custom Python ETL Connector

## Overview
This ETL connector fetches the **Top Attacking IPs** list from the [DShield Internet Storm Center](https://www.dshield.org) and loads it into a MongoDB collection.  
The connector is built as part of the **Kyureeus EdTech / SSN CSE** Software Architecture assignment.

The source data is a plain text feed containing:
- IP address of the attacker
- Number of attacks reported
- Country code

Each record is stored with an ingestion timestamp (`ingested_at`) for audit and update tracking.

---

## API Details
- **Base URL:** `https://www.dshield.org`
- **Endpoint:** `/ipsascii.html`
- **Format:** Plain Text (`TXT`)
- **Authentication:** None (public endpoint)
- **Pagination:** Not applicable (single file)
- **Rate Limit Handling:** Retries with exponential backoff for transient errors or 429 responses.

---


