# Software Architecture: ETL Pipeline for NetworkCalc

This project is a Python-based ETL (Extract, Transform, Load) pipeline built for a software architecture assignment. It connects to the `networkcalc.com` API, extracts data from its available endpoints, transforms the data into a clean format, and loads it into a local MongoDB database.

## 🚀 Features

* **Extract:** Connects to the `networkcalc.com/api` and fetches data.
* **Transform:**
    * Parses the JSON response.
    * Validates incoming data to prevent errors.
    * Enriches the data with new fields (e.g., `is_private`, `last_processed_utc`).
* **Load:** Loads the transformed data into a MongoDB database (`network_data`).
* **Modular Design:** The code is separated by concern into `api_client.py` (Extract), `transformer.py` (Transform), `loader.py` (Load), and `main.py` (Orchestrator).
* **Idempotent Loading:** Uses `update_one` with `upsert=True` to prevent duplicate entries and allow the pipeline to be run multiple times safely.

## 💻 Tech Stack

* **Python 3**
* **requests:** For making HTTP API calls.
* **pymongo:** The official Python driver for MongoDB.
* **python-dotenv:** For managing environment variables (like the database connection string).
* **MongoDB:** The NoSQL database used for storing the data.

## 📁 Project Structure

```
etl_project/
├── .env                  # Stores secrets like the MONGO_URI
├── .gitignore            # Tells Git to ignore .env, __pycache__, etc.
├── requirements.txt      # List of Python dependencies
├── config.py             # Loads environment variables
├── main.py               # Main script to run the entire pipeline
└── src/
    ├── api_client.py     # Handles all API extraction logic
    ├── transformer.py    # Handles all data transformation logic
    └── loader.py         # Handles all database loading logic
```

---

## 🛠️ Setup and Installation

### 1. Prerequisites

* [Python 3.10+](https://www.python.org/downloads/)
* [MongoDB Community Server](https://www.mongodb.com/try/download/community) (Make sure the service is running!)
* [MongoDB Compass](https://www.mongodb.com/try/download/compass) (To view your data)
* [Git](https://git-scm.com/downloads)

### 2. Clone the Repository

```bash
git clone [https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git](https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git)
cd YOUR-REPO-NAME
```

### 3. Install Dependencies

It's highly recommended to use a virtual environment.

```bash
# Create a virtual environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate
# (macOS/Linux)
# source venv/bin/activate

# Install the required libraries
pip install -r requirements.txt
```

### 4. Configure Environment

Create a file named `.env` in the project root and add your MongoDB connection string.

```
# .env
MONGO_URI="mongodb://localhost:27017/"
DB_NAME="network_data"
```

---

## ▶️ How to Run the Pipeline

With your MongoDB service running and your virtual environment activated, simply run `main.py`:

```bash
python main.py
```

You will see the log output in your terminal as it extracts, transforms, and loads the data.

```
INFO:src.loader:MongoDB connection successful.
INFO:__main__:--- Starting /ip/{ip} Pipeline ---
INFO:src.api_client:Successfully fetched data for IP: 8.8.8.8
INFO:src.loader:Inserted new record for cidr_notation: 8.8.8.8/32
INFO:src.api_client:Successfully fetched data for IP: 1.1.1.1
INFO:src.loader:Inserted new record for cidr_notation: 1.1.1.1/32
...
INFO:__main__:--- /ip/{ip} Pipeline Finished ---
INFO:__main__:All pipelines finished. MongoDB connection closed.
```

---

