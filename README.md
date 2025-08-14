# MITRE TAXII to MongoDB ETL

## Task Description
The objective of this task is to develop a Python-based ETL (Extract, Transform, Load) pipeline that connects to the MITRE ATT&CK TAXII server, retrieves STIX-formatted threat intelligence data, transforms it into a MongoDB-compatible structure, and stores it in a local MongoDB database. The goal is to make threat intelligence data easier to query and analyze for security-related applications.

---

## Detailed Explanation of the Task Performed

### 1. Extraction
- The script uses the **`taxii2-client`** library to connect to the official MITRE ATT&CK TAXII server.
- A TAXII collection client is created to pull STIX objects containing threat intelligence data.
- All available STIX domain objects (SDOs) from the specified MITRE ATT&CK collection are retrieved in JSON format.

**Example Source URL**:  
`https://cti-taxii.mitre.org/taxii/`  

---

### 2. Transformation
- The raw STIX JSON data retrieved from the TAXII server contains nested fields and metadata not necessary for MongoDB queries.
- The script processes the data to:
  - Extract relevant fields (`id`, `type`, `name`, `description`, `created`, `modified`, `kill_chain_phases`, etc.).
  - Flatten nested JSON structures for MongoDB compatibility.
  - Remove unnecessary or redundant metadata.
- The transformed data is structured in a clean, query-friendly format.

---

### 3. Loading
- Using the **`pymongo`** library, the processed data is inserted into a local MongoDB collection.
- The script:
  - Connects to the MongoDB server using a connection string (loaded from `.env`).
  - Creates a new collection if it does not exist.
  - Inserts all transformed threat intelligence objects.
- Each ETL stage outputs status logs showing progress and number of records processed.

---

### 4. Environment Configuration
- All sensitive and configurable values are stored in a `.env` file:
  - `MONGO_URI` – MongoDB connection string.
  - `DB_NAME` – Name of the MongoDB database.
  - `COLLECTION_NAME` – Name of the MongoDB collection.
  - `TAXII_API_URL` – MITRE ATT&CK TAXII API root URL.

---

### Summary
This ETL pipeline automates the process of fetching, cleaning, and storing MITRE ATT&CK threat intelligence data for use in security analysis tools.  
By transforming STIX objects into a simplified MongoDB schema, it allows security teams to run faster, more targeted queries without complex parsing.
