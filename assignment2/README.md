# FreeGeoIP ETL Connector - Assignment 2

**Student:** Hemalatha  
**Roll No:** 3122225001039

## Overview
This Python ETL connector retrieves IP geolocation data from [FreeGeoIP.app](https://freegeoip.app) using three endpoints:
- `/json/{ip}`
- `/csv/{ip}`
- `/xml/{ip}`

The connector extracts data from the API, transforms it into a unified JSON structure, and loads it into a MongoDB collection.

## Steps to Run

1. Create a `.env` file (based on `.env.template`) and add your MongoDB connection details.  
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
3.Run the ETL connector:
     python etl_connector.py
4.Verify inserted data in your MongoDB database.
