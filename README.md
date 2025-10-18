# Abuse.ch ETL Pipeline

This project is a simple **ETL (Extract, Transform, Load) pipeline** that fetches threat intelligence data from [abuse.ch](https://abuse.ch/) feeds (like URLhaus), transforms it, and loads it into **MongoDB** for further analysis.

---

## 🧭 Features

* **Extract**: Downloads CSV feeds directly from abuse.ch via Python `requests`.
* **Transform**: Cleans the data, handles duplicates, parses dates, and extracts domain names.
* **Load**: Stores the cleaned data into a MongoDB collection.
* **Environment Config**: Supports `.env` files for sensitive data like MongoDB URI.

---

## 📦 Requirements

* Python 3.10+
* MongoDB running locally or remotely
* Install dependencies:

```bash
pip install -r requirements.txt
```

Dependencies included:

* `requests` – for HTTP requests
* `pandas` – for CSV parsing and transformation
* `pymongo` – for MongoDB interaction
* `python-dotenv` – for loading `.env` configuration

---

## ⚡ Usage

1. Clone the repository:

```bash
git clone <repository_url>
cd <repository_folder>
```

2. Create a `.env` file (optional if you want to use environment variables):

```env
MONGODB_URI=mongodb://localhost:27017
ABUSE_FEED_URL=https://urlhaus.abuse.ch/downloads/csv_recent/
```

3. Run the ETL script:

```bash
python p.py
```

---

## 🗄️ MongoDB Storage

* **Database**: `threat_intel`
* **Collection**: `urlhaus_feed`
* **Stored fields**:

| Field       | Description                                       |
| ----------- | ------------------------------------------------- |
| url         | Malicious URL                                     |
| domain      | Extracted domain from URL                         |
| threat      | Threat type (malware, phishing, etc.)             |
| url_status  | Status of the URL (online/offline)                |
| date_added  | Date when the URL was added                       |
| ingested_at | Timestamp when the data was ingested into MongoDB |

---

## 🛠️ Customization

* Change the feed URL by modifying `ABUSE_FEED_URL` in `.env` or directly in `p.py`.
* Change MongoDB connection by modifying `MONGODB_URI`.
* Add more transformations as needed (e.g., enrich with ASN, GeoIP, or threat tags).

---

## ⚠️ Notes

* Use this feed **only for defensive and research purposes**.
* Avoid overloading abuse.ch servers; respect their download policies.

---

## 📌 References

* [Abuse.ch URLhaus](https://urlhaus.abuse.ch/)
* [Abuse.ch Threat Intelligence Feeds](https://abuse.ch/)
* [MongoDB Documentation](https://www.mongodb.com/docs/)

---

