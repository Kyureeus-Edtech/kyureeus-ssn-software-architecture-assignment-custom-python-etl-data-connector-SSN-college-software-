# 🛡️ MITRE ATT&CK ETL Connector

## 📋 Overview
This project fetches threat intelligence data from the **MITRE ATT&CK TAXII server**, transforms relevant objects, and loads them into a MongoDB database. It serves as a reference ETL pipeline for security research and analysis. 🔍

---

## ✨ Features
- 🔌 Connects to the MITRE ATT&CK TAXII server using `taxii2client`
- 📊 Extracts data from the **Enterprise ATT&CK collection**
- 🎯 Filters objects of type: `attack-pattern`, `intrusion-set`, and `malware`
- 💾 Loads transformed data into a MongoDB collection (`mitre_attack_raw`)
- 🔒 Uses environment variables for secure configuration

---

## 📁 Project Structure
```
.
├── etl_connector.py    # 🐍 Main ETL script
├── ENV_TEMPLATE        # 📝 Template for environment variables
├── .gitignore          # 🚫 To exclude sensitive files like .env
└── README.md           # 📖 Project documentation
```

---

## 🛠️ Prerequisites
- 🐍 Python 3.10+  
- 🍃 MongoDB running locally or accessible via URI  
- 📦 Required Python packages:
```bash
pip install taxii2client pymongo python-dotenv
```

## 🔧 Environment Variables
Create a `.env` file in the project root (not pushed to GitHub) with real credentials:
```env
MONGO_URI=mongodb://<username>:<password>@<host>:<port>
MONGO_DB=<your_database_name>
```
💡 The repository includes `ENV_TEMPLATE` as a reference for required keys (with placeholders).

## 🚀 Usage
1. 📥 Clone the repository
2. 📝 Create your `.env` file based on `ENV_TEMPLATE`
3. ▶️ Run the ETL script:
```bash
python etl_connector.py
```
4. ✅ The script will fetch data from MITRE, transform relevant objects, and insert them into MongoDB

## 📌 Notes
- 🌐 Make sure your network allows access to `https://cti-taxii.mitre.org/taxii/`. If blocked, consider using a different network or VPN
- 🗄️ MongoDB will automatically create the database and collection if they do not exist
- 🔄 Data is processed in real-time from the official MITRE ATT&CK framework

## 👨‍💻 Author
**Prathiyangira Devi V C**  
🏫 Sri Sivasubramaniya Nadar College of Engineering

---

## Acknowledgments
- 🏛️ MITRE Corporation for providing the ATT&CK framework and TAXII server