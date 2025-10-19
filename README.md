# MITRE Multi-Endpoint ETL

## Task Description

The objective of this task is to design and implement a Python-based ETL (Extract, Transform, Load) pipeline that collects, transforms, and stores structured threat intelligence data from **three different MITRE ATT&CK endpoints** — **Enterprise**, **Mobile**, and **ICS**.
Each endpoint provides STIX-formatted data describing adversarial techniques, tactics, malware, and mitigations.
The ETL process standardizes this data into a MongoDB-compatible structure, making it easier to query, analyze, and integrate into security tools.

---

## Detailed Explanation of the Task Performed

### 1. Extraction

* The script fetches STIX JSON data directly from the **MITRE ATT&CK public GitHub repository**, which mirrors data from the TAXII server.
* Three distinct endpoints are used for different ATT&CK domains:

  * **Enterprise ATT&CK:**
    `https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack.json`
  * **Mobile ATT&CK:**
    `https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/mobile-attack/mobile-attack.json`
  * **ICS ATT&CK:**
    `https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/ics-attack/ics-attack.json`
* Each endpoint is downloaded independently, and the number of STIX objects retrieved is logged.
* Clear console logs indicate which domain is being processed and confirm successful data extraction.

---

### 2. Transformation

* The STIX data retrieved contains deeply nested and metadata-heavy structures unsuitable for direct MongoDB insertion.
* The transformation step cleans and flattens this data by:

  * Extracting only **attack-pattern** records.
  * Keeping key attributes such as:

    * `id`, `name`, `description`, `created`, `modified`
    * `kill_chain_phases` (as a list)
    * `external_references` (as simplified sub-documents)
  * Removing redundant fields and metadata irrelevant for query analysis.
* Each transformation is logged with before-and-after samples for validation.
* The transformed records are compact, uniform, and optimized for fast MongoDB queries.

**Before Transformation (Raw STIX snippet)**:

```json
{
  "type": "attack-pattern",
  "id": "attack-pattern--b17a1a56-e99c-403c-8948-561df0cffe81",
  "name": "Phishing",
  "description": "Adversaries send deceptive emails...",
  "kill_chain_phases": [
    {"kill_chain_name": "mitre-attack", "phase_name": "initial-access"}
  ],
  "external_references": [
    {"source_name": "mitre-attack", "url": "https://attack.mitre.org/techniques/T1566/"}
  ]
}
```

**After Transformation (MongoDB-ready format)**:

```json
{
  "id": "attack-pattern--b17a1a56-e99c-403c-8948-561df0cffe81",
  "name": "Phishing",
  "description": "Adversaries send deceptive emails...",
  "created": "2017-05-31T21:30:00.000Z",
  "modified": "2023-05-05T20:34:00.000Z",
  "kill_chain_phases": ["initial-access"],
  "external_references": [
    {"source_name": "mitre-attack", "url": "https://attack.mitre.org/techniques/T1566/"}
  ]
}
```

---

### 3. Loading

* Using **`pymongo`**, the script connects to a MongoDB instance (local or remote, as defined in `.env`).
* Each domain’s data is loaded into its **own MongoDB collection**:

  * `enterprise_attack`
  * `mobile_attack`
  * `ics_attack`
* Before inserting, the script clears the existing collection to avoid duplication.
* The number of records inserted per domain is logged in the terminal for transparency.
<img width="1375" height="582" alt="image" src="https://github.com/user-attachments/assets/858b7983-c373-4583-8c97-ef806c385165" />

---

### 4. Environment Configuration

All configurable values are stored in a `.env` file for flexibility and security.

**Example `.env` file:**

```
MONGO_URI="Your mongo URI"
DB_NAME="Your database name"
```

---

### 5. Logging and Flow Control

Each major ETL stage (Extract → Transform → Load) prints detailed logs in the terminal:

* Endpoint being processed.
* Total records extracted and transformed.
* Sample data previews before and after transformation.
* Confirmation messages for database insertions.

This ensures full visibility of data flow and helps in debugging or extending the ETL logic.

<img width="1409" height="479" alt="image" src="https://github.com/user-attachments/assets/d20569ab-3d9f-429e-8cec-7685193da474" />

---
<img width="1599" height="480" alt="image" src="https://github.com/user-attachments/assets/8a54e729-5c19-477d-bc4d-375ed2c1d897" />

---
<img width="1581" height="479" alt="image" src="https://github.com/user-attachments/assets/6ab21df2-f308-4f82-9e1b-8d9d2bb29692" />


---

### Summary

This enhanced ETL pipeline automates the extraction of structured threat intelligence from **three MITRE ATT&CK knowledge bases**.
It then cleans and stores this intelligence in MongoDB, where analysts can perform advanced queries, visualize attack patterns, or integrate it into threat-hunting platforms.

**Domains Covered:**
✅ Enterprise ATT&CK
✅ Mobile ATT&CK
✅ ICS ATT&CK

By organizing threat intelligence across multiple domains in a consistent format, this ETL process supports more comprehensive, efficient, and scalable cybersecurity analytics.
