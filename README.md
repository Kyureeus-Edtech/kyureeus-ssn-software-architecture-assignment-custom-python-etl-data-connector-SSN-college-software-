
````markdown
# Python ETL Data Connector

This project extracts phishing data from **PhishTank**, transforms it, and loads it into a **MongoDB** collection.

## Steps to Run

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
````

2. **Set up `.env` file**

   ```
   MONGO_URI=your_mongo_connection_string
   PHISHTANK_URL=https://data.phishtank.com/data/online-valid.csv
   ```

3. **Run the script**

   ```bash
   python etl_connector.py
   ```

## What it does

* **Extract**: Downloads CSV from PhishTank
* **Transform**: Cleans and validates data
* **Load**: Inserts/updates records in MongoDB

---
