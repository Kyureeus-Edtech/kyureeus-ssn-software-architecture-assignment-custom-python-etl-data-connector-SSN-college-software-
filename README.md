# AbuseIPDB ETL Pipeline

## Project Overview
This project implements a complete **ETL (Extract → Transform → Load)** pipeline that fetches IP reputation data from the [AbuseIPDB API](https://docs.abuseipdb.com/), processes it, and stores the results in a **MongoDB database**.

## Features
- **Extract:** Fetch IP address reputation details from AbuseIPDB API.
- **Transform:** Normalize and structure the raw API data.
- **Load:** Store transformed data in MongoDB for further analysis.
- **Secure Credentials:** API key stored in `.env` file, not hardcoded.
- **Error Handling:** Handles API errors, invalid IPs, and rate limits.
- **Scalable:** Can process multiple IP addresses at once.

## Tech Stack
- **Language:** Python 3
- **Database:** MongoDB
- **Libraries:** `requests`, `pymongo`, `python-dotenv`

## Installation & Setup

### Clone the Repository
```bash
git clone https://github.com/Kyureeus-Edtech/kyureeus-ssn-software-architecture-assignment-custom-python-etl-data-connector-SSN-college-software-.git
cd <your-project-folder>
