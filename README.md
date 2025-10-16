# Blocklist.de ETL Data Connector

**Student Name:** K. Keerthana  
**Roll No:** 3122225001060  
**Course:** Software Architecture (Kyureeus EdTech, SSN CSE)

---

## 🔍 Overview
This ETL (Extract, Transform, Load) connector fetches cybersecurity threat data from multiple **Blocklist.de** APIs (such as SSH, Mail, Apache, IMAP, and Bots) and loads structured IP data into **MongoDB**.

---

## 🧠 ETL Flow
1. **Extract** – Fetch data using HTTP GET requests from Blocklist.de APIs.  
2. **Transform** – Clean raw text, remove comments, and format IPs into a list.  
3. **Load** – Store structured JSON documents into MongoDB with ingestion timestamps.

---

## ⚙️ Requirements
- Python 3.10+
- MongoDB (Local or Atlas)
- Installed dependencies:
  ```bash
  pip install -r requirements.txt

  ## ETL Script Output

Here is the output when the ETL connector runs successfully:

![ETL Output](images/img1.png)
![ETL Output](images/img2.png)
