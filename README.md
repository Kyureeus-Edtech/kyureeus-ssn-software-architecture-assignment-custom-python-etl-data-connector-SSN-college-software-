# HIBP ETL Connector (Python)

**Custom Python ETL Data Connector for Have I Been Pwned (HIBP) API**

---

**Student:** Vineeth U \
**Roll Number:** 3122225001160 \
**Assignment:** Custom Python ETL Data Connector (Kyureeus EdTech, SSN CSE)

---

## 📖 Project Overview

This project implements a custom **Extract–Transform–Load (ETL) data connector** in Python using the **Have I Been Pwned (HIBP) API v3**. Developed as part of the **SSN CSE Software Architecture assignment**, its primary goal is to demonstrate secure API integration, robust data transformation, and reliable storage into **MongoDB**.

The ETL script extracts breach and data class information from the HIBP API, validates and enriches the data, and loads it into dedicated MongoDB collections. All loaded documents include an **`ingestion_timestamp`** for auditability.

---

## 🎯 Goals and Learning Objectives

The successful completion of this project demonstrates proficiency in:

- **API Usage:** Understanding and using external API documentation (HIBP API v3) effectively.
- **Security:** Securely handling sensitive data (API keys) using **environment variables**.
- **ETL Pipeline:** Building a Python ETL pipeline that adheres to best practices:
    - **Extract:** Calling specified HIBP API endpoints.
    - **Transform:** Validating, cleaning, and enriching data with UTC timestamps and source URLs.
    - **Load:** Inserting/upserting data into designated MongoDB collections.
- **Error Handling:** Implementing graceful and robust error handling for common issues like **rate limits** (using exponential backoff), invalid responses, and **authentication errors (401/403)**.
- **Architecture:** Following a clean repository structure and demonstrating architectural principles.

---

## 🔗 HIBP Endpoints Utilized

The connector uses the following HIBP API v3 endpoints:

| API Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/v3/breaches` | `GET` | Lists all known breaches. |
| `/api/v3/breach/{name}` | `GET` | Retrieves detailed information for a specific breach. |
| `/api/v3/dataclasses` | `GET` | Lists all available data classes found in breaches. |

<br>

**Optional Endpoints (Used only if `TEST_ACCOUNT_EMAIL` is set in `.env`):**

- `/api/v3/pasteaccount/{account}` (GET)
- `/api/v3/breachedaccount/{account}` (GET)

⚠️ **Note:** HIBP API v3 generally requires a valid subscription key. The provided demo key (`00000000000000000000000000000000`) is intended only for testing request formatting and will not return real production data.

---

## ⚙️ Setup and Installation

### Prerequisites

1.  **Python 3.x**
2.  **MongoDB Instance** (Local or MongoDB Atlas)

### Steps

1.  **Clone and Setup:** Clone the repository and prepare the virtual environment.
2.  **Configuration:** Create a **`.env`** file based on the provided template and fill in your credentials.
3.  **Dependencies:** Install all required libraries using the **`requirements.txt`** file:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run:** Execute the main ETL script:
    ```bash
    python etl_connector.py
    ```

### Optional Execution Modes

You can override variables or fetch specific breach details using environment variables directly:

```bash
# Fetch details for specific breaches (e.g., 'Adobe' and 'LinkedIn')
BREACH_NAMES="Adobe,LinkedIn" python etl_connector.py

