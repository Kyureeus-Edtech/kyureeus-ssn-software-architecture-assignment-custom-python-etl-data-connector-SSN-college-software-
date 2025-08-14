[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/b1x675tx)
# SSN-college-software-architecture-Assignment

# VirusTotal File Hash Analysis ETL Connector

A streamlined ETL connector for analyzing file hashes using the **VirusTotal API v3** and storing results in MongoDB.

## 🚀 Quick Start

### 1. Setup
```bash
git clone <your-repository-url>
cd virustotal-etl-connector

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install requests pymongo python-dotenv
```

### 2. Configure Environment
Create a `.env` file:
```env
VT_API_KEY="your_virustotal_api_key_here"
MONGO_URI="your_mongo_URI"
MONGO_DB="Mongo_DB"
COLLECTION_NAME="collection_name"
```

**Get API Key**: Create free account at [VirusTotal](https://www.virustotal.com/gui/join-us) → Profile → Generate API Key

### 3. Usage

**Command Line:**
```bash
# Single hash
python etl_connector.py d41d8cd98f00b204e9800998ecf8427e

# Multiple hashes
python etl_connector.py hash1 hash2 hash3
```

**Interactive Mode:**
```bash
python etl_connector.py
# Choose: 1) File input (CSV/JSON) or 2) Manual entry
```

## 📊 API Details

- **Endpoint**: `https://www.virustotal.com/api/v3/files/{hash}`
- **Method**: GET
- **Supported Hashes**: MD5 (32 chars), SHA-1 (40 chars), SHA-256 (64 chars)
- **Rate Limit**: 4 requests/minute (free tier)

## 📁 Input Formats

**CSV:**
```csv
d41d8cd98f00b204e9800998ecf8427e
5d41402abc4b2a76b9719d911017c592
```

**JSON:**
```json
{
  "hashes": [
    "d41d8cd98f00b204e9800998ecf8427e",
    "5d41402abc4b2a76b9719d911017c592"
  ]
}
```


## 📈 Example Queries

**Find malicious files:**
```javascript
db.virustotal_scans.find({
  "detection_stats.malicious": { $gt: 5 }
})
```

**Files not in VirusTotal:**
```javascript
db.virustotal_scans.find({
  "vt_found": false
})
```

## 📋 Requirements

- Python 3.7+
- MongoDB 4.0+
- VirusTotal API key (free tier available)

## 🔒 Security

- Store API keys in `.env` file (never commit to Git)
- Add `.env` to `.gitignore`
- Use MongoDB authentication in production

---

**Author:** Ravindran V | **Roll Number:** 3122225001701
**Institution:** SSN College of Engineering
