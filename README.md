CIRCL Passive DNS ETL Connector (Python → MongoDB)

This project implements an ETL (Extract–Transform–Load) pipeline in Python to collect Passive DNS data from the CIRCL Passive DNS API and store it in MongoDB following secure and auditable ETL practices as specified in the Software Architecture assignment.

🚀 Features

Connects securely to CIRCL pDNS API

Uses Basic Authentication from .env (no hard-coding secrets)

Extracts raw DNS records (A, CNAME, MX, etc.)

Transforms records into MongoDB-friendly JSON

Loads batches into a dedicated MongoDB collection (circl_pdns_raw)

Stores ETL ingestion timestamps for audit trail

Supports configurable query, RR type and limits

📁 Project Structure
/your-branch-name/
├── circl_pdns_etl.py
├── README.md
├── .env # (NOT committed to Git)
├── requirements.txt
└── any other helpers...

🔐 Environment Variables (.env)

Create a .env file in the project root:

CIRCL_PDNS_USER=your_username_here
CIRCL_PDNS_PASS=your_password_here
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=etl_database
BATCH_SIZE=500

⚠️ Ensure .env is added to .gitignore before the first commit.

📦 Installation

Install dependencies:

pip install -r requirements.txt

Minimum packages required:

requests
pymongo
python-dotenv
python-dateutil

▶️ Run ETL
python3 circl_pdns_etl.py

Example output:

[INFO] Starting ETL for example.com...
[INFO] Inserted 150 docs.
[INFO] ETL complete. Processed: 150, Inserted: 150

🗃️ MongoDB Collection Strategy

Database: etl_database

Collection: circl_pdns_raw

Each document includes:

DNS fields: rrname, rrtype, rdata, count, timestamps

\_etl_ingested_at: UTC audit timestamp

\_etl_source: "circl_pdns"

\_raw: original COF record

✅ Assignment Submission Checklist

.env configured & excluded from Git

ETL script completed with Extract → Transform → Load

MongoDB inserts validated

README includes API usage & instructions

Commit includes Name & Roll Number

Code pushed to own branch and Pull Request created

📌 Notes

CIRCL pDNS is rate-limited — use limit to avoid blocking

Handle connectivity & invalid responses safely

Use separate Mongo collections for different connectors if extended
