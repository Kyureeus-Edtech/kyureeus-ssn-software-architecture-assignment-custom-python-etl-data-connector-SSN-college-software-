# 🧪 RIPEstat ETL Connector

## 📋 Overview

The **RIPEstat ETL Connector** fetches network intelligence data from the **RIPEstat Data API**, transforms relevant information, and loads it into a MongoDB database. This ETL pipeline is designed for network research and analysis, enabling easy storage and querying of ASN and IP-related data.

---

## ✨ Features

* 🔌 Connects to the RIPEstat Data API using the `ripestat` Python client.
* 📊 Extracts data on Autonomous Systems (ASNs), IP prefixes, and routing status.
* 🎯 Transforms and stores the data in a MongoDB collection for analysis.
* 🔒 Uses environment variables for secure configuration (MongoDB URI and database name).
* 🕒 Logs ETL progress and prints a summary of inserted data.

---

## 🛠️ Prerequisites

* 🐍 Python 3.10+
* 🍃 MongoDB running locally or accessible via URI
* 📦 Required Python packages:

```bash
pip install ripestat pymongo python-dotenv
```

---

## 🔧 Environment Variables

Create a `.env` file in the project root (do **not** push it to GitHub).

Example `.env` file:

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=network_intelligence
```

💡 The repository includes an `ENV_TEMPLATE` file as a reference for required keys.

---

## 🚀 Usage

1. 📥 Clone the repository:

```bash
git clone <repository_url>
cd <repository_folder>
```

2. 📝 Create your `.env` file based on `ENV_TEMPLATE`.

3. ▶️ Run the ETL script:

```bash
python etl_connector.py
```

4. ✅ The script will fetch data from RIPEstat, transform it, and insert it into MongoDB.

5. 📊 View the summary of the inserted data directly in the console.

---

## 📌 Notes

* 🌐 Ensure your network allows access to `https://stat.ripe.net`. If blocked, consider using a VPN.
* 🗄️ MongoDB will automatically create the database and collection if they do not exist.
* 🔄 The ETL pipeline retrieves real-time data from RIPEstat and inserts it into MongoDB in a structured format.

---

## 👨‍💻 Author

**Prathiyangira Devi V C**
🏫 Sri Sivasubramaniya Nadar College of Engineering

---

## 📁 Project Structure

```
.
├── etl_connector.py    # 🐍 Main ETL script
├── ENV_TEMPLATE            # 📝 Template for environment variables
├── .gitignore              # 🚫 To exclude sensitive files like .env
└── README.md               # 📖 Project documentation
```
