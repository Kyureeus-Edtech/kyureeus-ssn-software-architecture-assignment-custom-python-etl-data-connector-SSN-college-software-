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
cd \Users\aditya\OneDrive\Desktop\aditya.ssn\software architecture\custom-python-etl-data-connector-rkja130

output
```````
{
  _id: ObjectId('689c4b1db255bcbc6056b01c'),
  ipAddress: '8.8.8.8',
  isWhitelisted: true,
  abuseConfidenceScore: 0,
  countryCode: 'US',
  usageType: 'Content Delivery Network',
  isp: 'Google LLC',
  domain: 'google.com',
  totalReports: 20,
  lastReportedAt: '2025-08-13T03:24:54+00:00',
  ingestion_time: 2025-08-13T08:21:49.105Z
}

{
  _id: ObjectId('689c4b1db255bcbc6056b01d'),
  ipAddress: '1.1.1.1',
  isWhitelisted: true,
  abuseConfidenceScore: 0,
  countryCode: 'AU',
  usageType: 'Content Delivery Network',
  isp: 'APNIC and Cloudflare DNS Resolver project',
  domain: 'cloudflare.com',
  totalReports: 41,
  lastReportedAt: '2025-08-12T13:42:31+00:00',
  ingestion_time: 2025-08-13T08:21:49.930Z
}

{
  _id: ObjectId('689c4b1db255bcbc6056b01d'),
  ipAddress: '1.1.1.1',
  isWhitelisted: true,
  abuseConfidenceScore: 0,
  countryCode: 'AU',
  usageType: 'Content Delivery Network',
  isp: 'APNIC and Cloudflare DNS Resolver project',
  domain: 'cloudflare.com',
  totalReports: 41,
  lastReportedAt: '2025-08-12T13:42:31+00:00',
  ingestion_time: 2025-08-13T08:21:49.930Z
}
