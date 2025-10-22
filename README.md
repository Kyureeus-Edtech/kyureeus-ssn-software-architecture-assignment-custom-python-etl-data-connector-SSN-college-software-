# 🧩 Software Architecture Assignment: Custom Python ETL Data Connector

**Student Name:** Rupnarayan B
**Roll Number:** 3122 22 5001 114
**Department & Year:** CSE - C, IV Year  
**Date:** 22 October 2025  

---

## 📘 Overview

This project implements a **Python-based ETL (Extract, Transform, Load) pipeline** that fetches **threat intelligence data** from the [Abuse.ch](https://abuse.ch) ecosystem — specifically **ThreatFox**, **FeodoTracker**, and **URLhaus**.  

The ETL workflow:
1. **Extracts** threat data from APIs or CSV feeds  
2. **Transforms** and normalizes the data into JSON structures  
3. **Loads** it into a **MongoDB** database with audit timestamps  

---

## ⚙️ Features

- Fetches live threat data from **Abuse.ch** sources  
- Handles both **JSON** and **CSV** formatted data  
- Adds ingestion timestamps for audit tracking  
- Handles HTTP errors, timeouts, and rate limits gracefully  
- Inserts data into **MongoDB** collections for long-term storage  
- Ensures deduplication and consistent schema across sources  

---

## 🧠 API Providers

### 1. ThreatFox  
- **Endpoint:** `https://threatfox-api.abuse.ch/api/v1/`  
- **Auth Required:** Yes (via `.env` → `THREATFOX_AUTH_KEY`)  
- **Response Type:** JSON  
- **Purpose:** Provides Indicators of Compromise (IOCs) such as IPs, domains, and file hashes.  

### 2. FeodoTracker  
- **Endpoint:** `https://feodotracker.abuse.ch/downloads/ipblocklist.csv`  
- **Auth Required:** No  
- **Response Type:** CSV  
- **Purpose:** Lists botnet C2 IP addresses related to the Emotet/Feodo family.  

### 3. URLhaus  
- **Endpoint:** `https://urlhaus-api.abuse.ch/v1/urls/recent/`  
- **Auth Required:** Optional (`URLHAUS_AUTH_KEY`)  
- **Response Type:** JSON  
- **Purpose:** Tracks recently reported malicious URLs and payload sites.  

---

## 🧩 ETL Workflow

### 🔹 Extract  
Connects to each data provider’s API or CSV feed and retrieves data using `requests`.

### 🔹 Transform  
Cleans and reshapes the data for MongoDB compatibility:
- Renames inconsistent fields  
- Removes empty or invalid entries  
- Adds `_ingested_at` timestamp and `_source` label  

### 🔹 Load  
Uses **PyMongo** to insert processed data into MongoDB collections:
- `threatfox_raw`  
- `feodotracker_raw`  
- `urlhaus_raw`  

Each record is tagged with ingestion metadata for audit purposes.

---

## 🗃️ MongoDB Schema

**Database Name:** `abusech_db`  

| Collection | Source | Key Field | Example |
|-------------|---------|------------|----------|
| `threatfox_raw` | ThreatFox | `ioc` | `maliciousdomain.com` |
| `feodotracker_raw` | FeodoTracker | `ip` | `185.62.188.189` |
| `urlhaus_raw` | URLhaus | `url` | `http://malicioussite.com/bad.exe` |

**Common Field:** `_ingested_at` → UTC timestamp of insertion  

---

## 📦 Folder Structure

your-branch-name/
│
├── etl_connector.py # Main ETL script
├── .env # Contains API keys and Mongo URI (excluded from Git)
├── requirements.txt # Dependencies
└── README.md # Project documentation