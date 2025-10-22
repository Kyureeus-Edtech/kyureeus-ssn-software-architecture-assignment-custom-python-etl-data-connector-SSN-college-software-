# CIRCL Passive DNS ETL Connector

## Summary
ETL connector to query CIRCL Passive DNS and load normalized records into MongoDB.

## Prerequisites
- CIRCL PDNS account (username/password)
- Python 3.8 or higher
- MongoDB running locally or remotely

## Setup
1. Create a Python virtual environment and install dependencies:
   ```bash
   python -m venv venv
   venv\Scripts\activate   # on Windows
   pip install -r requirements.txt
