# Ram Prasath P - 3122 22 5001 103

# MITRE ATT&CK TAXII API - ETL Data Connector

This Python script is a custom-built ETL (Extract, Transform, Load) pipeline. It uses the `requests` library to connect with the public MITRE ATT&CK API, fetch data from three distinct endpoints, perform sophisticated transformations, and load the cleaned data into a MongoDB database.

---

## ⚙️ Architecture Overview

This connector is built without a client library to demonstrate a fundamental understanding of API interaction.

-   **Extraction**: Makes direct HTTP GET requests to the API, handling headers and parameters as required by the TAXII 2.1 specification.
-   **Transformation**: Applies different transformation logic based on the data source. A sophisticated process cleans, shapes, and enriches the core "attack pattern" data, while a simpler transform is used for metadata endpoints.
-   **Loading**: Upserts the processed data into three separate MongoDB collections, ensuring data integrity and preventing duplicates.

---

## 🚀 API & Endpoints Used

The connector interacts with the following distinct endpoints from the MITRE ATT&CK API Root:

-   **API Root URL**: `https://attack-taxii.mitre.org/api/v21/`
-   **Target Collection**: Enterprise ATT&CK (`id: x-mitre-collection--1f5f1533-f617-4ca8-9ab4-6a02367fa019`)

| # | Endpoint                               | Description                                                              | MongoDB Collection             |
|---|----------------------------------------|--------------------------------------------------------------------------|--------------------------------|
| 1 | `/collections`                         | Fetches metadata about all available collections on the server.          | `mitre_collections_metadata`   |
| 2 | `/collections/{id}/objects`            | Fetches full data objects (filtered for `attack-pattern`).               | `mitre_attack_patterns`        |
| 3 | `/collections/{id}/manifest`           | Fetches the manifest (a list of object metadata) for the collection.     | `mitre_collection_manifest`    |

---

## ✨ Sophisticated Transformation

The ETL pipeline applies a sophisticated transformation to the raw `attack-pattern` data to make it clean and analytics-ready. Key transformations include:

-   **Field Selection**: Selects a focused subset of the most relevant fields.
-   **Data Enrichment**: Extracts the ATT&CK ID (e.g., "T1222") and URL from a nested list and promotes them to top-level fields.
-   **Data Shaping**: Flattens the `kill_chain_phases` into a simple list of tactics.
-   **Type Conversion**: Converts timestamp strings into native BSON `datetime` objects for proper querying.

---

## ✅ How to Run

### 1. Prerequisites

-   Python 3.8+
-   A running MongoDB instance (local or cloud-based).

### 2. Setup

1.  **Clone the Repository** and navigate to your project folder.
    ```bash
    git clone https://github.com/Kyureeus-Edtech/custom-python-etl-data-connector-ramprasathp-ssn.git
    cd custom-python-etl-data-connector-ramprasathp-ssn/ramprasathp_3122225001103/
    ```
2.  **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure Environment Variables**:
    Create a `.env` file and add your MongoDB connection string:
    ```
    MONGO_URI="your-mongodb-connection-string"
    ```

### 3. Execute the Script

Run the ETL connector from your terminal:
```bash
python etl_connector.py