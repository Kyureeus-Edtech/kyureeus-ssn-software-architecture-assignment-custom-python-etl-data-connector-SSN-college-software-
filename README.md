# ThreatFox IOCs ETL Data Connector

This project contains a Python ETL (Extract–Transform–Load) script to fetch Indicators of Compromise (IOCs) from the ThreatFox API, transform them into a clean format, and load them into a MongoDB collection.

## 🚀 How to Run

### 1️⃣ Prerequisites
- Python 3.8+ installed
- A MongoDB Atlas account (or local MongoDB instance)
- A ThreatFox API key (optional, but required for authenticated queries)

### 2️⃣ Clone & Install
```bash
git clone <your-repo-url>
cd <repo-name>
pip install -r requirements.txt
