# Assignment 1 - Software Architecture : Python ETL Connector: An Advanced NVD Analysis Pipeline

**Name:** A Ankitha Reddy

**Roll Number:** 3122225001013

**Batch:** 2022-2026, CSE-A, Sri Sivasubramaniya Nadar College of Engineering

**Date:** 13.08.2025

## Project Overview

This project implements a robust, multi-stage ETL (Extract, Transform, Load) pipeline in Python. It interfaces with the National Vulnerability Database (NVD) API to ingest CVE data, but goes significantly beyond a simple data transfer. The core innovation lies in its sophisticated, API-free enrichment process, which transforms raw CVE data into a high-value, relational dataset, finally loading it into a MongoDB collection.

The pipeline is designed with data quality, idempotency, and analytical depth as first-class citizens, making it a powerful tool for vulnerability analysis.

---

## The Novelty: A Multi-Stage Enrichment Engine

The true innovation of this project is a two-stage, API-free enrichment process that operates on the entire data batch. This transforms the raw, isolated CVE entries into an interconnected, human-readable intelligence dataset.

### Stage 1: In-depth CVSS Risk Decomposition

Standard CVSS scores provide a single, top-level severity rating but obscure the critical details of a vulnerability's nature. This pipeline addresses this by **decomposing the cryptic CVSS 3.x vector string** (e.g., `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`) into a structured, human-readable object.

**Technical Approach:**
The script parses each metric of the vector string and maps it to a descriptive value. This enrichment answers critical operational questions that a simple score cannot:

-   **`attack_vector`**: Can this be exploited remotely over a **Network**, or does it require **Local** or **Physical** access?
-   **`privileges_required`**: Does the attacker need to be an administrator (**High**), have user-level access (**Low**), or need **None** at all?
-   **`user_interaction`**: Is the attack autonomous, or is it **Required** for a user to perform an action (e.g., click a malicious link)?
-   **`scope`**: Is the vulnerability's impact contained (**Unchanged**), or can it "escape" to affect other system components (**Changed**), indicating a higher-risk, escalated scenario?
-   **`Impact Metrics`**: Provides a clear breakdown of the impact on **Confidentiality**, **Integrity**, and **Availability**.

### Stage 2: Vulnerability Genealogy Analysis

Treating each CVE as an isolated event is a missed analytical opportunity. This pipeline's most unique feature is its ability to **discover latent relationships between vulnerabilities**, creating a "family tree" or genealogy.

**Technical Approach:**
This is achieved through a stateful, batch-aware analysis that does not require any external APIs:

1.  **Reference Mapping:** The script first performs a full pass on the entire batch of ingested CVEs, building a hash map where keys are reference URLs (e.g., security advisories from vendors) and values are a list of all CVEs that cite that URL.
2.  **Relational Augmentation:** In a second pass, the script re-evaluates each CVE. Using the reference map as a lookup table, it determines if a CVE shares one or more advisories with other CVEs in the batch.
3.  **Genealogy Object Creation:** If shared references are found, the CVE is enriched with a `genealogy` object containing a list of its "relatives" (`related_cves`).

This uncovers crucial context, such as coordinated disclosures from a single vendor (e.g., Microsoft Patch Tuesday), variants of the same underlying flaw, or bugs discovered by the same research team.

---

## Setup and Execution

### 1. Prerequisites
- Python 3.8+
- A running MongoDB instance
- Git

### 2. Clone and Set Up Your Branch
Fork the repository, clone your fork, and create your development branch.

### 3. Configure the Environment
Create a `.env` file in the project root with your MongoDB URI. An NVD API key is optional but recommended for higher rate limits.

### 4. Install Dependencies
All required libraries are listed in `requirements.txt`. Execute the command `pip install -r requirements.txt`.

### 5. Run the ETL Pipeline
The script includes a TEST_MODE flag at the top for quick, iterative development on a small subset of data. Set it to True for a development run or False for full execution. Run the command: `python3 etl_connector.py`

---

## Final Data Model in MongoDB

The resulting MongoDB documents are clean, structured, and enriched with high-value analytical objects. CVEs without a valid CVSS 3.x vector are intentionally filtered out to ensure data quality and schema consistency.

### Sample JSON

{
  "_id": "CVE-2023-22515",
  "cve_id": "CVE-2023-22515",
  "published_date": "2023-10-04T17:15:10.743",
  "description": "A privilege escalation vulnerability in Confluence Data Center and Server allows an unauthenticated attacker to create unauthorized Confluence administrator accounts...",
  "base_score": 10.0,
  "severity": "CRITICAL",
  "risk_breakdown": {
    "attack_vector": "Network",
    "attack_complexity": "Low",
    "privileges_required": "None",
    "user_interaction": "None",
    "scope": "Unchanged",
    "confidentiality_impact": "High",
    "integrity_impact": "High",
    "availability_impact": "High"
  },
  "genealogy": {
    "status": "Has Relatives",
    "related_cves": [
      "CVE-2023-22516",
      "CVE-2023-22517",
      "CVE-2023-22518"
    ],
    "shared_advisories": [
      "https://confluence.atlassian.com/doc/confluence-security-advisory-2023-10-04-1295682276.html"
    ]
  },
  "ingestion_timestamp": "2025-08-14T12:00:00.000Z"
}

## Key Technical Design Decisions

* Idempotency: The data loading step uses update_one with upsert=True, ensuring that the pipeline can be re-run safely without creating duplicate documents. This is a critical feature for robust data engineering workflows.
* Data Quality Enforcement: The pipeline deliberately filters out and discards any CVE that lacks a CVSS 3.x vector string. This ensures that every document in the final collection is complete and adheres to a consistent, high-quality schema suitable for analysis.
* Stateful Batch Analysis: The genealogy novelty is a stateful transformation that operates on the entire dataset batch, moving beyond simple one-to-one record mapping to discover emergent relationships within the data.