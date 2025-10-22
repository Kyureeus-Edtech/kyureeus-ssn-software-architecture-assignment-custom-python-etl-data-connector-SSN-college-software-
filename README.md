# HIBP ETL Connector (Python) — SSN CSE Software Architecture

**Student:** Vineeth U  
**Roll Number:** 3122225001160  
**Assignment:** Custom Python ETL Data Connector (Kyureeus EdTech, SSN CSE)

---

## 📖 Overview

This project implements a custom **Extract–Transform–Load (ETL) data connector** in Python using the **Have I Been Pwned (HIBP) API v3**. The connector is developed as part of the **Software Architecture assignment** to demonstrate secure API integration, data transformation, and storage in MongoDB.

The ETL script extracts breach and data class information from the HIBP API, validates and enriches the data, and loads it into MongoDB collections with ingestion timestamps for auditability.

---

## 🎯 Goals

- Understand and use API documentation effectively.
- Securely handle API keys using environment variables.
- Build a Python ETL pipeline that follows best practices:
  - **Extract** → call HIBP API endpoints.
  - **Transform** → validate and enrich data with timestamps.
  - **Load** → insert into MongoDB collections.
- Validate error handling for rate limits, invalid responses, and authentication errors.
- Follow Git repository structure and submission guidelines.

---

## 🔗 Endpoints Used

The connector uses at least **three HIBP endpoints** as required:

1. `GET /api/v3/breaches` → List all known breaches.
2. `GET /api/v3/breach/{name}` → Detailed info for a given breach.
3. `GET /api/v3/dataclasses` → List of available data classes.

**Optional endpoints** (only if `TEST_ACCOUNT_EMAIL` is set in `.env`):

- `GET /api/v3/pasteaccount/{account}` → Pastes related to an account.
- `GET /api/v3/breachedaccount/{account}` → Breaches for a specific account.

⚠️ Note: HIBP API v3 generally requires a valid subscription key. The demo key (`00000000000000000000000000000000`) is provided for testing request formatting but will not return real production data.

---

## 🗂 Project Structure
