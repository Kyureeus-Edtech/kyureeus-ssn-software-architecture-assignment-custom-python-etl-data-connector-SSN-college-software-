# NVD CVE Pipeline (MongoDB) — Extract & Transform

A compact pipeline that pulls CVE data from the National Vulnerability Database (NVD) Vulnerabilities API, stores the raw payload in MongoDB, transforms it into a flat, analysis‑friendly shape, and saves the transformed records back into MongoDB. No JSON files are written; both stages operate entirely on MongoDB collections.

---

## API Reference

**NVD Vulnerabilities API**  
Documentation: https://nvd.nist.gov/developers/vulnerabilities

**Base endpoint**
```
GET https://services.nvd.nist.gov/rest/json/cves/2.0
```

**Common query parameters**
- `startIndex` – zero‑based offset for pagination.
- `resultsPerPage` – number of records returned per page.

The response includes CVE metadata (ID, publication dates, status), human‑readable descriptions, CVSS metrics, weakness information (e.g., CWE), and reference URLs.

---

## Scripts

### `extract.py`
Pulls CVE data from the NVD API and writes the **raw response** into MongoDB.

- Reads connection details from `.env` (`MONGO_URI`, `MONGO_DB_NAME`).
- Stores the response in the collection: `nvd_raw`.
- Includes logging and error handling for HTTP and MongoDB operations.
- Optional clearing of the target collection before insert (see code).

### `transform.py`
Reads raw CVE documents from MongoDB and writes **transformed CVE records** back to MongoDB.

- Reads connection details from `.env` (`MONGO_URL`, `MONGO_DB`).
- Source collection: `nvd_raw`  
  Target collection: `nvd_vulnerabilities`
- Includes detailed logging, per‑record try/except, and robust failure reporting.

---

## Transform Tasks (as implemented)

For each item in `raw.vulnerabilities[]`:
1. Extract CVE metadata: `id`, `sourceIdentifier`, `published`, `lastModified`, `vulnStatus`.
2. Select the English description from `descriptions[]` into a single `description` field.
3. Flatten CVSS v2 metrics from the first entry in `metrics.cvssMetricV2[]` (if present):
   - `type`, `version`, `vectorString`, `baseScore`,
   - `accessVector`, `accessComplexity`, `authentication`,
   - `confidentialityImpact`, `integrityImpact`, `availabilityImpact`,
   - `baseSeverity`, `exploitabilityScore`, `impactScore`,
   - `acInsufInfo`, `obtainAllPrivilege`, `obtainUserPrivilege`, `obtainOtherPrivilege`,
   - `userInteractionRequired`.
4. Normalize weaknesses into a list of objects with `type` and English `description`.
5. Collect unique reference URLs into `references`.
6. Add `collected_at` as an ISO‑8601 UTC timestamp.
7. Log and skip records that fail transformation rather than aborting the batch.

---

## MongoDB Collections

- **`nvd_raw`** — raw NVD API response document(s).
- **`nvd_vulnerabilities`** — one document per transformed CVE, flattened and enriched.

---

## Setup

### 1) Clone
```bash
git clone <repo_url>
cd <repo_folder>
```

### 2) Python environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```
Minimum packages:
```
requests
pymongo
python-dotenv
```

### 4) Create `.env`
Create .env file using the ENV_TEMPLATE.

### 5) Run
```bash
# Fetch raw CVE data -> MongoDB (nvd_raw)
python extract.py

# Transform raw -> flattened documents (nvd_vulnerabilities)
python transform.py
```

---

## Logs

- `nvd_fetch.log` — HTTP fetch and raw‑stage MongoDB logs.
- `transform_vulnerabilities.log` — transformation and insert logs.