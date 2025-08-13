# ETL Data Connector for URLHaus 
This directory contains a custom Extract–Transform–Load (ETL) Python script that retrieves csv data from this <a href="https://urlhaus.abuse.ch/downloads/csv_online/">URLHaus endpoint</a> and stores it both in mongoDB and as a csv file.


## ✅ Submission Checklist

- [✅] Choose a data provider (API) and understand its documentation
- [NA] Secure all API credentials using a `.env` file
- [✅] Build a complete ETL pipeline: Extract → Transform → Load (into MongoDB)
- [✅] Test and validate your pipeline (handle errors, invalid data, rate limits, etc.)
- [✅] Follow the provided Git project structure
- [✅] Write a clear and descriptive `README.md` in your folder with API details and usage instructions
- [✅] **Include your name and roll number in your commit messages**
- [✅] Push your code to your branch and submit a Pull Request

---

## 📦 Project Structure

/Avaneesh_Koushik_31222225001018_A/
├── etl_connector.py
├── ENV_TEMPLATE
├── requirements.txt
├── README.md


- **`ENV_TEMPLATE`**: Sample .env file
- **`etl_connector.py`**: Main ETL script.
- **`requirements.txt`**: List all Python dependencies.
- **`README.md`**: Instructions for your connector.



## 🗃️ MongoDB Guidelines

- Used one MongoDB collection per connector (e.g., `connectorname_raw`).
- Stored ingestion timestamps for audit and update purposes.

# Sample Data Stored:
{
  "_id": {
    "$oid": "689ce121e32e541f9bb20304"
  },
  "id": "3602184",
  "dateadded": "2025-08-13 18:48:08",
  "url": "MALWARE_LINK",
  "url_status": "online",
  "last_online": "2025-08-13 18:48:08",
  "threat": "malware_download",
  "tags": "32-bit,elf,mips,Mozi",
  "urlhaus_link": "https://urlhaus.abuse.ch/url/3602184/",
  "reporter\r": "geenensp",
  "ingested_at": {
    "$date": "2025-08-14T00:31:53.570Z"
  }
}
---

## 🧪 Testing & Validation

- Check for invalid responses, empty payloads, rate limits, and connectivity issues.
- Ensure data is correctly inserted into MongoDB.

---



