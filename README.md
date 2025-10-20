# 🔐 SSL Labs API ETL Pipeline

A comprehensive **Python-based ETL (Extract, Transform, Load)** pipeline that connects to the **SSL Labs API** to extract SSL/TLS security configuration data, transform it for MongoDB compatibility, and load it into a MongoDB database for analysis and storage.

---

## 🧭 Overview

This ETL connector extracts data from **5 different SSL Labs API endpoints:**

| # | Endpoint | Purpose | Data Scope |
|:-:|-----------|----------|-------------|
| 1 | `/info` | API version and engine information | Global |
| 2 | `/getStatusCodes` | Status code definitions | Global |
| 3 | `/analyze` | SSL/TLS configuration analysis | Per-host |
| 4 | `/getEndpointData` | Detailed endpoint information | Per-IP |
| 5 | `/getRootCertsRaw` | Trusted root certificates | Global |

---

## 🎯 Project Goals

✅ Extract data from SSL Labs API with proper error handling  
✅ Transform data by adding metadata (timestamps, endpoint info)  
✅ Load data into separate MongoDB collections per endpoint  
✅ Secure credentials using environment variables  
✅ Handle rate limits, timeouts, and API errors gracefully  

---

## 🌍 What is SSL Labs API?

**SSL Labs (by Qualys)** provides a free API to analyze the SSL/TLS configuration of public web servers — the same engine that powers the **SSL Server Test** tool.

### 🔑 Key Features
- Free to use (no API key required)
- Analyzes SSL/TLS certificates, protocols, and ciphers
- Provides letter grades (A+, A, B, C, D, F)
- Identifies common vulnerabilities
- Trusted by security professionals worldwide

### 💼 Use Cases
- Monitor SSL/TLS configurations across infrastructure  
- Track certificate expirations  
- Identify vulnerabilities  
- Maintain compliance  
- Perform historical SSL/TLS security data analysis  

### 📘 API Details
- **Base URL:** `https://api.ssllabs.com/api/v3`  
- **Authentication:** None (public API)  
- **Rate Limit:** 1 request per 2 seconds recommended  
- **Docs:** [Official API Documentation](https://github.com/ssllabs/ssllabs-scan/blob/master/ssllabs-api-docs-v3.md)  

---

## 🔍 API Endpoints Explained

### 1️⃣ `/info`
**URL:** `GET https://api.ssllabs.com/api/v3/info`

Retrieves API version and engine information.

**Extracted Fields:**
- API version number
- Engine version
- Max concurrent assessments
- Current assessments running
- API status

**MongoDB Collection:** `ssllabs_info_raw`

**Sample Response:**
```json
{
  "engineVersion": "2.2.0",
  "criteriaVersion": "2009q",
  "maxAssessments": 25,
  "currentAssessments": 0,
  "newAssessmentCoolOff": 1000
}
