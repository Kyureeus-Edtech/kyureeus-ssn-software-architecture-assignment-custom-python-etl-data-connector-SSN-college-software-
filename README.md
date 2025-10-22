# Blocklist.de Python ETL Connector

Student: Kushal Varma
Roll Number: 3122225001031

---

1. Project Summary

This project implements a Python ETL (Extract, Transform, Load) pipeline that collects public IP blacklist feeds from Blocklist.de, transforms the data into structured documents, and saves them into a MongoDB database for analysis.

Blocklist.de provides publicly available lists of IP addresses that have exhibited suspicious behavior, such as SSH brute force attacks, mail server attacks, web server exploits, and botnet activity. The ETL pipeline retrieves these lists, structures the data, and ensures safe and efficient insertion into MongoDB for further use.

---

2. Key Features

* MongoDB Integration: Stores structured documents in a single collection (`blocklist`) for centralized analysis.
* Metadata Enrichment: Adds timestamps (`fetched_at`) and source information to every document.
* Error Handling: Logs connection issues, server errors, and bulk write exceptions clearly.
* Modular & Maintainable: Clear separation of extraction, transformation, and loading stages.

---

3. Project Structure


CUSTOM-PYTHON-ETL-DATA-CONNECTOR-KUSHALVARMA4923/
├── etl_connector.py       # Python script implementing the ETL pipeline
├── requirements.txt       # Python dependencies
├── .env.example           # Template for environment variables
├── .gitignore             # Excludes secrets, virtual environment, and temp files
└── README.md              # Documentation for the project
```


4. Setup & Execution

4.1 Install Python Dependencies

```bash
pip install -r requirements.txt
```

4.2 Configure Environment Variables

Create a `.env` file with the following entries:

```
BLOCKLIST_BASE=https://www.blocklist.de
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=blocklist_de

```

4.3 Run the ETL Connector

```bash
python etl_connector.py
```

The script will:

1. Fetch data from all configured Blocklist.de endpoints.
2. Transform each list into structured documents.
3. Insert the results into the MongoDB collection `blocklist`.

---

5. Supported Endpoints

| Service | URL                                                                                        |
| ------- | ------------------------------------------------------------------------------------------ |
| SSH     | [https://lists.blocklist.de/lists/ssh.txt](https://lists.blocklist.de/lists/ssh.txt)       |
| Mail    | [https://lists.blocklist.de/lists/mail.txt](https://lists.blocklist.de/lists/mail.txt)     |
| Apache  | [https://lists.blocklist.de/lists/apache.txt](https://lists.blocklist.de/lists/apache.txt) |

Each endpoint returns a plain-text list of IP addresses, which the ETL script parses and enriches with metadata before storing in MongoDB.

---

6. ETL Workflow

6.1 Extract

* Uses `requests` to retrieve plain-text IP lists from each endpoint.
* Handles network failures with retry logic and exponential backoff.

6.2 Transform

* Processes each line to filter out empty lines or comments.
* Converts each IP into a dictionary with fields:

```json
{
  "ip": "185.224.128.17",
  "service": "ssh",
  "source": "blocklist.de/lists",
  "fetched_at": "2025-10-22T08:00:00Z"
}
```

6.3 Load

* Connects to MongoDB using `pymongo`.
* Inserts all processed documents into a **single collection** called `blocklist`.
* Handles bulk write errors gracefully and logs the number of successful inserts.

---

7. Notes

* All data is stored in the `threat_feeds` database.
* Each document contains the `service` field to differentiate feeds.
* The pipeline can be scheduled or triggered periodically to maintain an updated blacklist database.

