# SSL Labs API v4 → MongoDB ETL Connector

## 📌 Overview
This Python ETL connector queries the **SSL Labs API v4** for SSL/TLS scan results of given domains, then stores the results in **MongoDB** with ingestion timestamps.

It is designed for the **SSN College Software Architecture – ETL Assignment** and follows secure coding and project structure guidelines.

---

## 🛠 Prerequisites
- **Python** 3.8 or higher
- **MongoDB** running locally or remotely
- **Registered Email** with SSL Labs API v4 (required in request header `email`)

> ❗ You must register your email with SSL Labs API v4 before running scans.

---

## 📂 Project Structure
etl_connector.py # Main ETL script
.env # Your environment variables (DO NOT COMMIT)
ENV_TEMPLATE # Template for environment variables (share this instead of .env)
requirements.txt # Python dependencies
---

## ⚙️ Setup Instructions

### **1. Clone the Repository**
git clone <repo-url>
cd your-branch-nam

### **2. Install Dependencies**
pip install -r requirements.txt

### **3. Register Email with SSL Labs API v4**
- Use the `/register` endpoint of SSL Labs API v4 to register your organizational email.
- The email must be included in all API requests via the HTTP header `email`.

### **4. Configure Environment Variables**
- Copy the template and edit it:
cp ENV_TEMPLATE .env

- Update `.env` with your actual values:
SSL_LABS_EMAIL=your.registered.email@yourdomain.com
MONGO_URI=mongodb://localhost:27017
DB_NAME=ssllabs_etl
> Never commit `.env` to GitHub. It contains sensitive information.

---

## ▶️ Running the ETL Script
python etl_connector.py

The script will:
1. Loop through the predefined `HOSTS` list.
2. Request a scan from SSL Labs API v4.
3. Poll until the scan status is `READY` or `ERROR`.
4. Store the final report in MongoDB with the field `ingested_at`.

---

## 📝 Notes & Best Practices
- **Email header requirement**: The `email` must be sent as an HTTP request header, not as a query parameter.
- **Blacklist handling**: Some domains such as `example.com`, `google.com`, and other popular services are blacklisted from scanning.
- **Private results**: Setting `"publish": "off"` keeps scan results private.
- **Polling interval**: The script waits 30 seconds between checks to respect API rate limits.
- **Storage format**: Each scan result is stored in collection `<connector>_raw` for raw ingestion records.

---

## 📚 References
- **SSL Labs API Documentation**: [https://www.ssllabs.com/projects/documentation/](https://www.ssllabs.com/projects/documentation/)
- **pymongo Documentation**: https://pymongo.readthedocs.io/en/stable/
- **python-dotenv Documentation**: https://pypi.org/project/python-dotenv/