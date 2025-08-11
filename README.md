# 🚀 NASA APOD ETL Pipeline

This project implements an **ETL (Extract → Transform → Load)** pipeline in Python to fetch random Astronomy Picture of the Day (APOD) entries from the **NASA API**, transform them for MongoDB storage, and load them into a MongoDB collection.

The script uses **environment variables** for secure handling of API keys and MongoDB credentials and is designed to be reusable for other API connectors.

---

## 📌 Features

- **Extract**: Fetches a configurable number of random APOD entries from NASA’s API.
- **Transform**: Cleans and structures the data for MongoDB insertion.
- **Load**: Inserts transformed records into a MongoDB Atlas collection.
- **Secure**: Uses `.env` file for API keys and secrets.
- **Error Handling**: Handles network failures, empty responses, and missing credentials.

---

### How to Run

1.  _Prerequisites:_ Ensure you have Python and MongoDB.
2.  _Clone & Install:_
    bash
    git clone <your-repo-url>
    cd <repo-name>
    pip install -r requirements.txt
3.  _Set Up Credentials:_ Create a .env file and add your credentials:
    ini
    NASA_API_KEY="your-key"
    MONGO_URI="your-mongo-uri"
4.  _Execute the Script:_
    bash
    python etl_connector.py
