# OTX IP General Data ETL Connector

## Overview
This project is a custom Python ETL (Extract → Transform → Load) data connector built as part of the **SSN College - Software Architecture Assignment** under the Kyureeus EdTech program.  
It connects to the **AlienVault OTX API** to fetch general information for given IPv4 addresses, transforms the data for MongoDB compatibility, and loads it into a specified MongoDB collection.

---

## API Details

- **Provider:** [AlienVault OTX](https://otx.alienvault.com/)
- **Endpoint:**  
  ```
  GET https://otx.alienvault.com/api/v1/indicators/IPv4/{ip}/general
  ```
- **Authentication:** API key (stored in `.env` for security)
- **Response Format:** JSON
- **Rate Limits:** Subject to OTX free-tier restrictions.

---

## Project Structure

```
/pradeep-3122225001092-b/
  ├── etl_connector.py      # Main ETL pipeline script
  ├── .env                  # Local environment variables (not committed)
  ├── requirements.txt      # Python dependencies
  ├── README.md             # This documentation
```

---

## Installation

1. Clone the repository and checkout to your branch:
   ```bash
   git clone https://github.com/Kyureeus-Edtech/custom-python-etl-data-connector-pradeepkmaran
   cd custom-python-etl-data-connector-pradeepkmaran
   git checkout -b pradeep-3122225001092-b
   ```

2. Create a `.env` file in the same folder as `etl_connector.py`:
   ```
   OTX_BASE=
   OTX_API_KEY=
   MONGO_URI=
   MONGO_DB=
   COLLECTION_NAME=
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

Run the ETL script with one or more IPs:
```bash
python etl_connector.py --ips "8.8.8.8,1.1.1.1"
```

---

## Example Output (Terminal)

```
2025-08-11 10:35:29,953 INFO Fetching OTX general data for IP: 8.8.8.8
2025-08-11 10:35:30,637 INFO Inserted data for 8.8.8.8 into MongoDB.
2025-08-11 10:35:30,638 INFO Fetching OTX general data for IP: 1.1.1.1
2025-08-11 10:35:31,043 INFO Inserted data for 1.1.1.1 into MongoDB.
```

---

## Example Document in MongoDB

```json
{
  "ip": "8.8.8.8",
  "pulse_count": 15,
  "is_malicious": false,
  "raw": { ... },  // Full JSON response from OTX
  "ingested_at": "2025-08-11T10:35:30.637Z"
}
```

---

## Notes

- Ensure MongoDB is running locally or update `MONGO_URI` in `.env`.
- `.env` must **not** be committed to Git.
- Follow the SSN assignment guidelines for commit messages:
  ```
  Added OTX ETL Connector - Pradeep - 3122225001092
  ```

---

## Author
- **Name:** Pradeep KM 
- **Roll Number:** 3122225001092
- **Course:** SSN CSE - Software Architecture Assignment  
