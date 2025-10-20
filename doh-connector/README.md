# DNS over HTTPS ETL Connector using AdGuard DNS

> **Custom Python ETL Data Connector Assignment**  
> SSN College of Engineering - Software Architecture  
> Kyureeus EdTech Program

---

## 👨‍🎓 Student Information

**Name:** Shankari S R 
**Roll Number:** 3122225001125 
**Branch:** Computer Science and Engineering  
**College:** SSN College of Engineering  
**Date:** October 19, 2025

---

## 📋 Project Overview

This project implements a complete **ETL (Extract, Transform, Load) pipeline** that connects to the **AdGuard DNS over HTTPS (DoH) API**, retrieves DNS query data for multiple record types, transforms the data into a structured format, and loads it into a **MongoDB** collection.

### Why AdGuard DNS?
- **DNS over HTTPS (DoH)** - Encrypted DNS queries over HTTPS protocol
- **Public API** - No authentication required
- **Three Different Record Types** - A, AAAA, and MX records as separate endpoints
- **Structured JSON Data** - RFC 8427 compliant DNS JSON format
- **Real-world Application** - DNS resolution is fundamental to internet infrastructure
- **Free & Reliable** - High availability with no rate limits for reasonable use

---

## 🔌 API Provider Details

### AdGuard DNS over HTTPS

| Attribute | Details |
|-----------|---------|
| **Base URL** | `https://dns.adguard-dns.com/resolve` |
| **Documentation** | https://adguard-dns.io/en/public-dns.html |
| **Authentication** | None required (Public API) |
| **Rate Limits** | No strict limits for reasonable use |
| **Response Format** | JSON (RFC 8427 - DNS Queries over HTTPS) |
| **Protocol** | HTTPS (DNS over HTTPS - DoH) |
| **Method** | GET |

### DNS Record Types Supported
- A (IPv4 addresses)
- AAAA (IPv6 addresses)
- MX (Mail exchange servers)
- TXT (Text records)
- CNAME (Canonical names)
- NS (Name servers)
- And many more...

---

## 🎯 Three Endpoints Implementation

This ETL connector queries **three different DNS record types** from the same domain as separate endpoints:

### 1️⃣ Endpoint 1: A Record (IPv4 Address)
```
GET https://dns.adguard-dns.com/resolve?name=google.com&type=A
```
- **Purpose:** Retrieves IPv4 addresses for domain names
- **Record Type Code:** 1
- **Use Case:** Finding the IPv4 address where a website is hosted
- **Example Response:**
  ```json
  {
    "Status": 0,
    "TC": false,
    "RD": true,
    "RA": true,
    "AD": false,
    "CD": false,
    "Question": [
      {
        "name": "google.com",
        "type": 1
      }
    ],
    "Answer": [
      {
        "name": "google.com",
        "type": 1,
        "TTL": 300,
        "data": "142.250.185.46"
      }
    ]
  }
  ```

### 2️⃣ Endpoint 2: AAAA Record (IPv6 Address)
```
GET https://dns.adguard-dns.com/resolve?name=google.com&type=AAAA
```
- **Purpose:** Retrieves IPv6 addresses for domain names
- **Record Type Code:** 28
- **Use Case:** Finding the IPv6 address for modern internet connectivity
- **Example Response:**
  ```json
  {
    "Status": 0,
    "Question": [
      {
        "name": "google.com",
        "type": 28
      }
    ],
    "Answer": [
      {
        "name": "google.com",
        "type": 28,
        "TTL": 300,
        "data": "2607:f8b0:4004:c07::71"
      }
    ]
  }
  ```

### 3️⃣ Endpoint 3: MX Record (Mail Exchange)
```
GET https://dns.adguard-dns.com/resolve?name=google.com&type=MX
```
- **Purpose:** Retrieves mail server information with priorities
- **Record Type Code:** 15
- **Use Case:** Finding which mail servers handle email for a domain
- **Example Response:**
  ```json
  {
    "Status": 0,
    "Question": [
      {
        "name": "google.com",
        "type": 15
      }
    ],
    "Answer": [
      {
        "name": "google.com",
        "type": 15,
        "TTL": 600,
        "data": "smtp.google.com",
        "priority": 10
      }
    ]
  }
  ```

---

## 🏗️ ETL Pipeline Architecture

### Extract Phase
```python
def extract(domain, record_type, retry_count=3):
    # 1. Build query parameters (domain name, record type)
    # 2. Set proper headers for JSON response
    # 3. Send GET request to AdGuard DNS API
    # 4. Handle rate limits (HTTP 429)
    # 5. Implement retry logic (3 attempts)
    # 6. Handle network timeouts (20 seconds)
    # 7. Parse JSON response
    # 8. Validate DNS response status
    # 9. Return structured data
```

**Key Features:**
- ✅ Timeout protection (20 seconds)
- ✅ Retry logic (3 attempts with progressive delays)
- ✅ Rate limit detection and auto-retry
- ✅ Connection error handling
- ✅ JSON parsing validation
- ✅ HTTP status code verification
- ✅ DNS response status checking

### Transform Phase
```python
def transform(raw_data, query_info):
    # 1. Add ingestion timestamp (for audit trail)
    # 2. Extract query context (domain, type, timestamp)
    # 3. Parse DNS response flags (RD, RA, AD, CD, TC)
    # 4. Map status codes to descriptions (NOERROR, NXDOMAIN, etc.)
    # 5. Structure answer records (name, type, TTL, data)
    # 6. Map record type codes to names (1→A, 28→AAAA, 15→MX)
    # 7. Include question, authority, and additional sections
    # 8. Store raw response for reference
    # 9. Ensure MongoDB compatibility
```

**Key Features:**
- ✅ Timestamp injection for tracking
- ✅ Human-readable status descriptions
- ✅ Record type code to name mapping
- ✅ Complete DNS response structure
- ✅ Nested document structure
- ✅ Handles missing/optional fields
- ✅ Preserves all DNS response data

### Load Phase
```python
def load(transformed_data):
    # 1. Connect to MongoDB collection
    # 2. Insert transformed document
    # 3. Capture and return insertion ID
    # 4. Handle insertion errors gracefully
```

**Key Features:**
- ✅ Automatic database/collection creation
- ✅ Error handling for duplicate data
- ✅ Connection pooling
- ✅ Insertion ID tracking

---

## 📊 MongoDB Collection Schema

### Collection Name
```
adguard_dns_raw
```

### Document Structure
```json
{
  "_id": ObjectId("68f5113f67dd781f099e7656"),
  "ingestion_timestamp": ISODate("2025-10-19T10:30:45.123Z"),
  "dns_provider": "AdGuard DNS",
  "query": {
    "domain": "google.com",
    "record_type": "A",
    "record_description": "IPv4 Address Record",
    "query_timestamp": "2025-10-19T10:30:45.120000+00:00"
  },
  "response": {
    "status": 0,
    "status_description": "NOERROR - No error condition",
    "truncated": false,
    "recursion_desired": true,
    "recursion_available": true,
    "authenticated_data": false,
    "checking_disabled": false
  },
  "question": [
    {
      "name": "google.com",
      "type": 1,
      "type_name": "A"
    }
  ],
  "answers": [
    {
      "name": "google.com",
      "type": 1,
      "type_name": "A",
      "ttl": 300,
      "data": "142.250.185.46"
    }
  ],
  "metadata": {
    "answer_count": 1,
    "authority_count": 0,
    "additional_count": 0,
    "question_count": 1
  },
  "raw_response": {
    "Status": 0,
    "TC": false,
    "RD": true,
    "RA": true,
    "AD": false,
    "CD": false,
    "Question": [...],
    "Answer": [...]
  }
}
```

### Collection Strategy
- **One collection per connector** - `adguard_dns_raw`
- **Ingestion timestamps** - Track when data was collected
- **Query context preserved** - Know what was requested
- **Full response data** - All DNS fields captured including raw response
- **Audit trail** - Can track changes over time
- **Structured metadata** - Answer/authority/additional counts

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MongoDB (local installation or Atlas cloud)
- Internet connection
- Git (for version control)

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd SSN-college-software-architecture-Assignments
git checkout -b yourname-rollnumber
cd your-folder
```

### Step 2: Install Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
```bash
# Create .env file
cp .env.template .env

# Edit .env with your MongoDB connection details
# For local MongoDB:
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=dns_etl_db

# For MongoDB Atlas (cloud):
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DB=dns_etl_db
```

### Step 4: Verify MongoDB is Running
```bash
# For local MongoDB
mongosh

# You should see MongoDB shell
# Type 'exit' to quit
```

### Step 5: Update Student Information
Edit `etl_connector.py` and update:
```python
Author: [Your Name]          # Line 6
Roll Number: [Your Roll Number]  # Line 7
```

### Step 6: Run the ETL Pipeline
```bash
python etl_connector.py
```

---

## 📺 Expected Output

```
✓ Connected to MongoDB: dns_etl_db.adguard_dns_raw
✓ Using DNS Provider: AdGuard DNS over HTTPS
✓ Base URL: https://dns.adguard-dns.com/resolve
======================================================================
DNS over HTTPS ETL Pipeline - Starting
======================================================================

[TEST] Testing AdGuard DNS API connectivity...
✓ AdGuard DNS API is reachable (Status: 200)
  Test query successful - Status: 0

======================================================================
Processing Query: google.com - Type: A (IPv4 Address Record)
======================================================================

[EXTRACT] Querying A record for google.com... (Attempt 1/3)
✓ Successfully extracted A record data
  Response Status: 0
  Answers Received: 1
[TRANSFORM] Processing A record data...
✓ Transformation complete - 1 answers processed
[LOAD] Inserting into MongoDB collection: adguard_dns_raw
✓ Document inserted with ID: 68f5113f67dd781f099e7656
✓ ETL completed successfully for A record

======================================================================
Processing Query: google.com - Type: AAAA (IPv6 Address Record)
======================================================================

[EXTRACT] Querying AAAA record for google.com... (Attempt 1/3)
✓ Successfully extracted AAAA record data
  Response Status: 0
  Answers Received: 1
[TRANSFORM] Processing AAAA record data...
✓ Transformation complete - 1 answers processed
[LOAD] Inserting into MongoDB collection: adguard_dns_raw
✓ Document inserted with ID: 68f5114267dd781f099e7657
✓ ETL completed successfully for AAAA record

======================================================================
Processing Query: google.com - Type: MX (Mail Exchange Record)
======================================================================

[EXTRACT] Querying MX record for google.com... (Attempt 1/3)
✓ Successfully extracted MX record data
  Response Status: 0
  Answers Received: 5
[TRANSFORM] Processing MX record data...
✓ Transformation complete - 5 answers processed
[LOAD] Inserting into MongoDB collection: adguard_dns_raw
✓ Document inserted with ID: 68f5114667dd781f099e7658
✓ ETL completed successfully for MX record

======================================================================
ETL Pipeline Summary
======================================================================
DNS Provider: AdGuard DNS over HTTPS
Total queries processed: 3
✓ Successful: 3
✗ Failed: 0

✓ Pipeline completed successfully!
  Check MongoDB collection 'adguard_dns_raw' for results

📊 Verify Data:
  mongosh
  use dns_etl_db
  db.adguard_dns_raw.find().pretty()
======================================================================

✓ MongoDB connection closed
```

---

## 🧪 Testing & Validation

### Validate Data in MongoDB

#### Using MongoDB Shell:
```bash
mongosh

# Switch to database
use dns_etl_db

# Count total documents
db.adguard_dns_raw.countDocuments()
// Expected output: 3

# View all documents
db.adguard_dns_raw.find().pretty()

# Query specific record types
db.adguard_dns_raw.find({"query.record_type": "A"})
db.adguard_dns_raw.find({"query.record_type": "AAAA"})
db.adguard_dns_raw.find({"query.record_type": "MX"})

# Check all answers
db.adguard_dns_raw.find({}, {"query.record_type": 1, "answers": 1})

# View DNS response statuses
db.adguard_dns_raw.find({}, {"query.record_type": 1, "response.status": 1, "response.status_description": 1})

# Check ingestion timestamps
db.adguard_dns_raw.find({}, {ingestion_timestamp: 1, "query.record_type": 1})

# View latest entry
db.adguard_dns_raw.find().sort({ingestion_timestamp: -1}).limit(1)

# Count answers by record type
db.adguard_dns_raw.aggregate([
  {$group: {_id: "$query.record_type", total_answers: {$sum: "$metadata.answer_count"}}}
])
```

Expected aggregation output:
```json
[
  { "_id": "A", "total_answers": 1 },
  { "_id": "AAAA", "total_answers": 1 },
  { "_id": "MX", "total_answers": 5 }
]
```

#### Using MongoDB Compass (GUI):
1. Open MongoDB Compass
2. Connect using: `mongodb://localhost:27017/`
3. Navigate to `dns_etl_db` → `adguard_dns_raw`
4. You should see 3 documents
5. Click on any document to view full structure
6. Use Schema tab to visualize data structure
7. Try filter: `{"query.record_type": "MX"}` to see mail servers

### Test Cases Covered

| Test Case | Status | Description |
|-----------|--------|-------------|
| Valid DNS Query | ✅ | Successfully queries all three record types |
| Network Timeout | ✅ | 20-second timeout protection |
| Retry Logic | ✅ | 3 attempts with progressive delays (3s, 6s, 9s) |
| Rate Limiting | ✅ | Detects HTTP 429 and waits 60 seconds |
| JSON Parsing | ✅ | Handles malformed JSON responses |
| MongoDB Connection | ✅ | Graceful failure if DB unavailable |
| Empty Responses | ✅ | Handles queries with no answers |
| DNS Status Codes | ✅ | Maps status codes to descriptions |
| Record Type Mapping | ✅ | Converts type codes to names (1→A, 28→AAAA) |
| Data Transformation | ✅ | All fields correctly structured |
| Timestamp Injection | ✅ | Every document has ingestion time |
| Raw Response Storage | ✅ | Original API response preserved |
| Error Logging | ✅ | Clear error messages for debugging |

---

## 🔒 Security Best Practices

### ✅ What We Did Right:
1. **Environment Variables** - All credentials in `.env` file
2. **Git Ignore** - `.env` never committed to repository
3. **No Hardcoded Secrets** - No credentials in source code
4. **Secure Loading** - Using `python-dotenv` library
5. **Public API** - AdGuard DNS requires no authentication
6. **HTTPS Only** - All DNS queries encrypted over HTTPS

### ⚠️ Important Security Notes:
- **Never commit `.env` file** to Git
- **Never share MongoDB credentials** publicly
- **Use strong passwords** for MongoDB Atlas
- **Whitelist IPs** in MongoDB Atlas Network Access
- **Rotate credentials** regularly
- **DNS Privacy** - DoH encrypts DNS queries, preventing ISP snooping

---

## 📦 Project Structure

```
adguard-dns-connector/
├── etl_connector.py      # Main ETL pipeline script
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (NOT committed)
├── .env.template        # Template for .env file
├── .gitignore           # Git ignore rules
├── README.md            # This documentation file
└── SETUP_GUIDE.md       # Detailed setup instructions (optional)
```

---

## 🐛 Troubleshooting

### Problem 1: Module Not Found Error
```
ModuleNotFoundError: No module named 'requests'
```
**Solution:**
```bash
pip install -r requirements.txt
```

### Problem 2: MongoDB Connection Timeout
```
pymongo.errors.ServerSelectionTimeoutError
```
**Solution:**
- Check if MongoDB is running: `sudo systemctl status mongod` (Linux)
- Windows: Check Services for MongoDB
- Verify `.env` has correct `MONGODB_URI`
- For Atlas: Check Network Access settings

### Problem 3: DNS API Request Failed
```
✗ API request failed: Connection timeout
```
**Solution:**
- Check internet connection
- Test API manually in browser: https://dns.adguard-dns.com/resolve?name=google.com&type=A
- Check firewall settings
- Verify DNS resolution is working

### Problem 4: No Answers in Response
```
Response Status: 0
Answers Received: 0
```
**Solution:**
- This is normal for some domains/record types
- Status 0 (NOERROR) means query succeeded but no records exist
- Status 3 (NXDOMAIN) means domain doesn't exist

### Problem 5: Rate Limit Exceeded
```
✗ Rate limit exceeded. Waiting 60 seconds...
```
**Solution:**
- AdGuard DNS has generous rate limits
- Wait for the cooldown period
- Script automatically retries after 60 seconds

---

## 📚 Technical References

### DNS Record Types Reference

| Type | Code | Description | Example |
|------|------|-------------|---------|
| A | 1 | IPv4 address | 142.250.185.46 |
| NS | 2 | Name server | ns1.google.com |
| CNAME | 5 | Canonical name | www.example.com |
| SOA | 6 | Start of authority | Primary DNS server info |
| MX | 15 | Mail exchange | smtp.google.com |
| TXT | 16 | Text record | "v=spf1 include:_spf.google.com" |
| AAAA | 28 | IPv6 address | 2607:f8b0:4004:c07::71 |
| SRV | 33 | Service record | Service location |

### DNS Response Status Codes

| Code | Name | Description |
|------|------|-------------|
| 0 | NOERROR | Query completed successfully |
| 1 | FORMERR | Format error in query |
| 2 | SERVFAIL | Server failed to complete |
| 3 | NXDOMAIN | Domain name does not exist |
| 4 | NOTIMP | Query type not implemented |
| 5 | REFUSED | Query refused by server |

### DNS Response Flags

| Flag | Name | Description |
|------|------|-------------|
| TC | Truncated | Response was truncated |
| RD | Recursion Desired | Client requested recursion |
| RA | Recursion Available | Server supports recursion |
| AD | Authenticated Data | DNSSEC validated |
| CD | Checking Disabled | DNSSEC validation disabled |

### API Documentation Links
- [AdGuard DNS Documentation](https://adguard-dns.io/en/public-dns.html)
- [RFC 8484 - DNS over HTTPS](https://tools.ietf.org/html/rfc8484)
- [RFC 8427 - DNS JSON Format](https://tools.ietf.org/html/rfc8427)
- [DNS Record Types](https://en.wikipedia.org/wiki/List_of_DNS_record_types)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [Requests Library](https://docs.python-requests.org/)

---

## 📝 Assignment Submission Checklist

Before submitting, verify all items:

### Code Requirements
- [x] Chose AdGuard DNS over HTTPS as data provider
- [x] Implemented three different endpoints (A, AAAA, MX record types)
- [x] Built complete ETL pipeline (Extract → Transform → Load)
- [x] All credentials secured in `.env` file
- [x] Error handling for all failure scenarios
- [x] Retry logic with exponential backoff
- [x] MongoDB integration with proper collection strategy
- [x] Ingestion timestamps included
- [x] Raw response preservation

### Documentation Requirements
- [x] Clear README.md with API details
- [x] Three endpoint descriptions with examples
- [x] Installation and setup instructions
- [x] Expected output documentation
- [x] Testing and validation steps
- [x] Troubleshooting guide
- [x] MongoDB schema documentation
- [x] DNS concepts explained

### Project Structure Requirements
- [x] Proper file organization
- [x] `.gitignore` includes `.env`
- [x] `requirements.txt` lists all dependencies
- [x] Student name and roll number in code
- [x] Code comments and docstrings
- [x] Professional code formatting

### Git Requirements
- [x] Created personal branch
- [x] Clear commit messages with name and roll number
- [x] `.env` NOT committed to repository
- [x] Code pushed to remote branch
- [x] Ready for Pull Request

---

## 🎓 Learning Outcomes

By completing this assignment, you have learned:

1. **DNS Fundamentals** - Understanding DNS record types and resolution
2. **DNS over HTTPS (DoH)** - Encrypted DNS queries for privacy
3. **API Integration** - RESTful API consumption with error handling
4. **ETL Pipeline Design** - Complete Extract, Transform, Load workflow
5. **Error Handling** - Robust retry logic and exception management
6. **NoSQL Databases** - MongoDB document storage and querying
7. **Security Practices** - Environment variables and secure coding
8. **Data Transformation** - Parsing and structuring complex responses
9. **Python Best Practices** - Code organization and documentation
10. **Version Control** - Git workflow and collaboration
11. **Production Readiness** - Building reliable data pipelines
12. **Network Protocols** - HTTP/HTTPS and DNS protocol understanding

---

## 🌐 Real-World Applications

This ETL pipeline demonstrates skills applicable to:

- **Network Monitoring** - Track DNS changes and availability
- **Security Analysis** - Detect DNS hijacking or suspicious queries
- **Performance Optimization** - Analyze DNS resolution times
- **Data Analytics** - Build DNS query datasets for analysis
- **DevOps** - Monitor infrastructure DNS configurations
- **Threat Intelligence** - Track malicious domains
- **Compliance** - Audit DNS query patterns

---

## 📄 License

This project is submitted as part of academic coursework for SSN College of Engineering.

---

## 🙏 Acknowledgments

- **AdGuard DNS** - For providing free DNS over HTTPS service
- **MongoDB** - For database platform
- **SSN College of Engineering** - For academic guidance
- **Kyureeus EdTech** - For educational program
- **IETF** - For DNS over HTTPS standards (RFC 8484, 8427)

---

## 🔄 Alternative DNS Providers

If AdGuard DNS becomes unavailable, this connector can be adapted for:

- **Google DNS**: `https://dns.google/resolve`
- **Cloudflare DNS**: `https://1.1.1.1/dns-query`
- **Quad9 DNS**: `https://dns.quad9.net/dns-query`
- **NextDNS**: `https://dns.nextdns.io/dns-query`

Simply change the `ADGUARD_DNS_BASE_URL` in the code.

---

**Last Updated:** October 19, 2025  
**Version:** 1.0.0  
**Status:** ✅ Ready for Testing  
**API Provider:** AdGuard DNS over HTTPS  
**Protocol:** DNS over HTTPS (DoH)  
**Endpoints:** 3 (A, AAAA, MX records)
