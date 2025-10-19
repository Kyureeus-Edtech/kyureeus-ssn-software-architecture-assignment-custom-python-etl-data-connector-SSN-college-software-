# PublicWWW API ETL Connector

**Student Name:** Dharunika.S  
**Roll Number:** 3122225001026  
**Section:** CSE-A  
**Course:** Software Architecture - SSN CSE  
**Assignment:** Custom Python ETL Data Connector

This project implements a complete **ETL (Extract, Transform, Load)** pipeline for the PublicWWW API. PublicWWW is a source code search engine that allows you to search for code snippets, scripts, and technologies across millions of websites.

### What This Project Does

1. **Extract:** Connects to PublicWWW API and fetches data from 5 different endpoints
2. **Transform:** Processes and structures the raw data for MongoDB compatibility
3. **Load:** Stores the transformed data into MongoDB with timestamps and metadata
4. **Verify:** Validates that data extraction was successful

---

## 🌐 About PublicWWW

PublicWWW is a digital marketing and affiliate marketing research tool that finds any alphanumeric snippet, signature, or keyword in web pages' HTML, JS, and CSS code.

**Use Cases:**

- Finding websites using specific technologies (React, jQuery, WordPress)
- Identifying sites with particular analytics IDs (Google Analytics, Facebook Pixel)
- Discovering sites using specific eCommerce engines
- Tracking advertising network usage

**Website:** https://publicwww.com

## 🎯 Features Implemented

- ✅ Secure API authentication using environment variables
- ✅ Complete ETL pipeline (Extract → Transform → Load)
- ✅ **5 Different API Endpoints** extracted:
  1. Google Analytics tracking
  2. jQuery library usage
  3. WordPress CMS
  4. Facebook Pixel tracking
  5. Google AdSense network
- ✅ MongoDB integration with timestamped records
- ✅ Rate limiting to respect API throttling
- ✅ Comprehensive error handling and logging
- ✅ Data validation and verification script
- ✅ Detailed console output for monitoring

---

## 📁 Project Structure

```
Assignment-2/
├── connector.py              # Main ETL pipeline script
├── verify_extraction.py      # Data verification script
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .env                      # Environment variables (DO NOT COMMIT)
└── .gitignore               # Git ignore file
```

---

## 🔧 Prerequisites

Before running this project, ensure you have:

1. **Python 3.8 or higher**

   ```bash
   python --version
   ```

2. **MongoDB installed and running**

   ```bash
   # Check if MongoDB is running
   mongosh
   ```

3. **PublicWWW API Key** (Optional but recommended)

   - Sign up at: https://publicwww.com
   - Get your API key from account settings
   - Free tier available for testing

4. **Git** (for version control)
   ```bash
   git --version
   ```

---

## ⚙️ Installation & Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/Kyureeus-Edtech/custom-python-etl-data-connector-Dharunika-07.git
cd custom-python-etl-data-connector-Dharunika-07
git checkout Dharunika.S_3122225001026_CSE-A_Assignment-2
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies installed:**

- `requests` - For API calls
- `pymongo` - MongoDB driver
- `python-dotenv` - Environment variable management

### Step 3: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp env_template
```

Edit `.env` with your credentials:

```env
# PublicWWW API Configuration
PUBLICWWW_API_KEY=your_api_key_here
PUBLICWWW_BASE_URL=https://publicwww.com/api

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=etl_database

# Rate Limiting (seconds between requests)
RATE_LIMIT_DELAY=1.0
```

**⚠️ IMPORTANT:** Never commit your `.env` file to Git! It's already in `.gitignore`.

### Step 4: Start MongoDB

Make sure MongoDB is running:

```bash
# Windows
net start MongoDB

# macOS/Linux
sudo systemctl start mongod

# Or using MongoDB Compass - just open the application
```

---

## 🚀 How to Run

### Option 1: Run the Complete ETL Pipeline

This will extract data from all 5 endpoints:

```bash
python connector.py
```

**Expected Output:**

```
============================================================
PublicWWW API ETL Connector - Enhanced Version
============================================================

2025-10-19 22:30:00 - INFO - API Key loaded: d68411c1...
2025-10-19 22:30:00 - INFO - Configuration validated successfully
2025-10-19 22:30:00 - INFO - Starting ETL pipeline execution
2025-10-19 22:30:01 - INFO - Connected to MongoDB: etl_database.publicwww_raw

============================================================
STEP 1/3: EXTRACT - Fetching data from PublicWWW
============================================================
============================================================
Starting extraction from multiple endpoints
============================================================

[1/5] Extracting: analytics - google-analytics.com/analytics.js
2025-10-19 22:30:01 - INFO - Making GET request to: https://publicwww.com/websites/google-analytics.com/analytics.js/
2025-10-19 22:30:01 - INFO - With API key: True
2025-10-19 22:30:02 - INFO - Response status code: 200
2025-10-19 22:30:02 - INFO - Received HTML response (length: 125000 chars)
2025-10-19 22:30:02 - INFO - ✓ Successfully extracted data

[2/5] Extracting: technology - jquery
...
[5/5] Extracting: ad_network - googlesyndication.com
...

============================================================
Extraction complete: 5 endpoints processed
============================================================

============================================================
STEP 2/3: TRANSFORM - Processing data
============================================================
2025-10-19 22:30:15 - INFO - Data transformed successfully:
2025-10-19 22:30:15 - INFO -   - Total endpoints: 5
2025-10-19 22:30:15 - INFO -   - Successful: 5
2025-10-19 22:30:15 - INFO -   - Failed: 0

============================================================
STEP 3/3: LOAD - Storing data in MongoDB
============================================================
2025-10-19 22:30:15 - INFO - Data loaded successfully!
2025-10-19 22:30:15 - INFO -   - Document ID: 68f51abc...

============================================================
DATA VALIDATION RESULTS
============================================================
Total documents in collection: 1
Latest document details:
  - Timestamp: 2025-10-19 17:00:11...
  - Source: publicwww_api
  - Endpoints processed: 5
  - Has API key: True
  - Successful queries: 5
  - Failed queries: 0

Sample queries extracted:
  1. google-analytics.com/analytics.js - ✓ Data extracted
  2. jquery - ✓ Data extracted
  3. wordpress - ✓ Data extracted

============================================================

============================================================
FINAL STATUS: ✓ SUCCESS
============================================================
```

---

### Option 2: Run Data Verification

After running the ETL pipeline, verify the data was extracted correctly:

```bash
python verify_extraction.py
```

**Expected Output:**

```
======================================================================
PublicWWW ETL - Data Extraction Verification
======================================================================

✓ Connected to MongoDB
✓ Total documents in collection: 1
✓ Retrieved latest document (ID: 68f51abc...)

----------------------------------------------------------------------
DOCUMENT STRUCTURE VERIFICATION
----------------------------------------------------------------------
Source: publicwww_api
  ✓ Correct source
Ingestion Timestamp: 2025-10-19 17:00:11...
  ✓ Timestamp present

----------------------------------------------------------------------
METADATA VERIFICATION
----------------------------------------------------------------------
Endpoint Count: 5
  ✓ Found 5 endpoints (minimum 5 required)
Has API Key: True
  ✓ API key is being used

Query Summary:
  Total Queries: 5
  Successful: 5
  Failed: 0
  ✓ At least 5 successful queries

----------------------------------------------------------------------
RAW DATA VERIFICATION
----------------------------------------------------------------------
Number of endpoints in raw_data: 5

Detailed Endpoint Analysis:
----------------------------------------------------------------------

[1] Query: google-analytics.com/analytics.js
    Type: search
    Content Type: html
    Full Length: 125000 chars
    Preview Length: 5000 chars
    ✓ Data extracted successfully

[2] Query: jquery
    Type: search
    Content Type: html
    Full Length: 118000 chars
    Preview Length: 5000 chars
    ✓ Data extracted successfully

[3] Query: wordpress
    Type: search
    Content Type: html
    Full Length: 132000 chars
    Preview Length: 5000 chars
    ✓ Data extracted successfully

[4] Query: facebook.com/tr
    Type: search
    Content Type: html
    Full Length: 98000 chars
    Preview Length: 5000 chars
    ✓ Data extracted successfully

[5] Query: googlesyndication.com
    Type: search
    Content Type: html
    Full Length: 145000 chars
    Preview Length: 5000 chars
    ✓ Data extracted successfully

======================================================================
FINAL VERIFICATION SUMMARY
======================================================================
✓ [1/5] Documents exist in collection
✓ [2/5] Metadata structure present
✓ [3/5] Has 5 endpoints (minimum 5)
✓ [4/5] 5 successful queries
✓ [5/5] 5 endpoints have data

======================================================================
RESULT: 5/5 checks passed
🎉 ALL CHECKS PASSED! Data extraction is working correctly!
======================================================================
```

---

### Option 3: Complete Workflow (Recommended)

Run both scripts in sequence:

```bash
# Step 1: Run ETL pipeline
python connector.py

# Step 2: Verify data extraction
python verify_extraction.py
```

---

## 📊 API Endpoints Extracted

The ETL pipeline extracts data from these 5 PublicWWW endpoints:

| #   | Endpoint Type | Query                               | Description                     |
| --- | ------------- | ----------------------------------- | ------------------------------- |
| 1   | Analytics     | `google-analytics.com/analytics.js` | Websites using Google Analytics |
| 2   | Technology    | `jquery`                            | Websites using jQuery library   |
| 3   | CMS           | `wordpress`                         | Websites built with WordPress   |
| 4   | Tracking      | `facebook.com/tr`                   | Websites using Facebook Pixel   |
| 5   | Ad Network    | `googlesyndication.com`             | Websites using Google AdSense   |

---

## 🗄️ MongoDB Schema

### Collection: `publicwww_raw`

Each document stored in MongoDB follows this structure:

```json
{
  "_id": ObjectId("68f51abc..."),
  "source": "publicwww_api",
  "ingestion_timestamp": ISODate("2025-10-19T17:00:11.000Z"),
  "raw_data": {
    "extraction_timestamp": "2025-10-19T17:00:11.123456+00:00",
    "endpoints": [
      {
        "endpoint": "search",
        "query": "google-analytics.com/analytics.js",
        "timestamp": "2025-10-19T17:00:11.123456+00:00",
        "data": {
          "content_type": "html",
          "url": "https://publicwww.com/websites/google-analytics.com/analytics.js/",
          "status_code": 200,
          "html_content": "<!DOCTYPE html>...",
          "full_length": 125000,
          "response_headers": {...}
        }
      },
      // ... 4 more endpoints
    ]
  },
  "metadata": {
    "data_version": "1.0",
    "transformer": "PublicWWWETL",
    "endpoint_count": 5,
    "extraction_time": "2025-10-19T17:00:11.123456+00:00",
    "has_api_key": true,
    "summary": {
      "total_queries": 5,
      "successful_queries": 5,
      "failed_queries": 0
    }
  }
}
```

---

## 🔍 Viewing Data in MongoDB

### Method 1: MongoDB Compass (GUI)

1. Open MongoDB Compass
2. Connect to: `mongodb://localhost:27017/`
3. Navigate to database: `etl_database`
4. Open collection: `publicwww_raw`
5. Browse documents

### Method 3: Python Script

```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['etl_database']
collection = db['publicwww_raw']

# Get latest document
doc = collection.find_one(sort=[('ingestion_timestamp', -1)])

# Print summary
print(f"Endpoints: {doc['metadata']['endpoint_count']}")
print(f"Successful: {doc['metadata']['summary']['successful_queries']}")

# List queries
for ep in doc['raw_data']['endpoints']:
    print(f"- {ep['query']}")
```

---

## 🔒 Security Best Practices

### 1. Environment Variables

- ✅ All sensitive credentials stored in `.env`
- ✅ `.env` added to `.gitignore`
- ✅ Never hardcode API keys in source code
- ✅ Use `.env.example` as a template

### 2. API Key Management

- Keep your API key confidential
- Don't share it in screenshots or commits
- Rotate keys periodically
- Use different keys for dev/production

### 3. MongoDB Security

- Use strong passwords
- Enable authentication
- Restrict network access
- Regular backups

---

## 🐛 Troubleshooting

### Issue 1: "No module named 'dotenv'"

**Solution:**

```bash
pip install python-dotenv
```

### Issue 2: "Connection refused to MongoDB"

**Solution:**

```bash
# Start MongoDB service
# Windows:
net start MongoDB

# macOS/Linux:
sudo systemctl start mongod
```

### Issue 3: "API Key not found"

**Solution:**

- Verify `.env` file exists
- Check `.env` has `PUBLICWWW_API_KEY=your_key`
- Make sure no spaces around `=`

### Issue 4: "Rate limit exceeded"

**Solution:**

- Increase `RATE_LIMIT_DELAY` in `.env` to 2.0 or higher
- Wait 60 seconds between runs

### Issue 5: "Only 0 successful queries"

**Solution:**

- Check internet connection
- Verify PublicWWW is accessible
- Try with API key instead of free tier
- Check the logs for specific error messages

---

## 📝 Testing & Validation

### Complete Testing Workflow:

```bash
# 1. Run the ETL pipeline
python connector.py

# 2. Verify the extraction
python verify_extraction.py

# 3. Check MongoDB (optional)
mongosh
use etl_database
db.publicwww_raw.countDocuments()
```

### Success Indicators:

✅ ETL pipeline shows: `FINAL STATUS: ✓ SUCCESS`  
✅ Verification shows: `5/5 checks passed`  
✅ MongoDB has documents with `endpoint_count: 5`  
✅ All 5 queries show "✓ Data extracted successfully"

---

## 🔄 Rate Limiting

To respect API limits:

- Default: 1 second delay between requests
- Configurable via `RATE_LIMIT_DELAY` in `.env`
- Automatic retry on 429 (Too Many Requests)
- PublicWWW recommends 60 seconds between calls for free tier

---

## 📚 Assignment Requirements Fulfilled

| Requirement              | Status | Details                     |
| ------------------------ | ------ | --------------------------- |
| Choose API provider      | ✅     | PublicWWW API               |
| Understand documentation | ✅     | Endpoint structure analyzed |
| Secure credentials       | ✅     | `.env` file with dotenv     |
| Build ETL script         | ✅     | `connector.py`              |
| Extract data             | ✅     | 5 endpoints extracted       |
| Transform data           | ✅     | MongoDB-compatible format   |
| Load to MongoDB          | ✅     | Timestamped records         |
| Handle errors            | ✅     | Try-except blocks, logging  |
| Test & validate          | ✅     | `verify_extraction.py`      |
| Git structure            | ✅     | Proper branching            |
| Documentation            | ✅     | This README                 |
| Commit messages          | ✅     | Descriptive messages        |

---

## 🎓 Learning Outcomes

Through this project, I learned:

1. **ETL Pipeline Design:** How to structure Extract-Transform-Load workflows
2. **API Integration:** Working with REST APIs, authentication, and rate limiting
3. **MongoDB:** NoSQL database operations, document structure, and queries
4. **Error Handling:** Robust error handling for production-ready code
5. **Security:** Protecting sensitive credentials using environment variables
6. **Git Workflow:** Branching, committing, and pull requests
7. **Documentation:** Writing clear, comprehensive technical documentation

---

## 📄 License

This project is part of an academic assignment for SSN College of Engineering (Kyureeus EdTech program).

---

## 🙏 Acknowledgments

- **SSN College of Engineering** - For the academic program
- **Kyureeus EdTech** - For the course curriculum
- **PublicWWW** - For providing the API
- **Course Instructors** - For guidance and support
- **Teaching Assistants** - For technical support

---

## 📞 Contact & Support

**Student Information:**

- **Name:** Dharunika.S
- **Roll Number:** 3122225001026
- **Section:** CSE-A
- **Institution:** SSN College of Engineering
- **Course:** Software Architecture

## 📈 Project Statistics

- **Total Lines of Code:** ~500+ lines
- **API Endpoints:** 5
- **Dependencies:** 3
- **Test Coverage:** Validation script included
- **Documentation:** Comprehensive README

---

## 🚀 Future Enhancements

Possible improvements for this project:

1. **HTML Parsing:** Extract structured data from HTML responses
2. **Scheduling:** Automate ETL runs using cron jobs or schedulers
3. **Dashboard:** Create a web dashboard to visualize extracted data
4. **More Endpoints:** Add 10+ more PublicWWW queries
5. **Data Analysis:** Analyze trends in technology usage
6. **API Response Caching:** Reduce redundant API calls
7. **Export Features:** Export data to CSV, Excel, JSON

---

**Last Updated:** October 19, 2025  
**Version:** 1.0  
**Status:** ✅ Complete and Tested

---

## 📝 Quick Reference Commands

```bash
# Installation
pip install -r requirements.txt

# Run ETL Pipeline
python connector.py

# Verify Data
python verify_extraction.py

# Check MongoDB
mongosh
use etl_database
db.publicwww_raw.countDocuments()

# Git Commands
git add .
git commit -m "Your message"
git push origin Dharunika.S_3122225001026_CSE-A_Assignment-2
```

---

**🎉 Thank you for reviewing this project!**
