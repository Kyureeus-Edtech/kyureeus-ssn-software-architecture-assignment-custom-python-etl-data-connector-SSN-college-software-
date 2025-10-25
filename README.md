# CIRCL Passive DNS ETL Connector (Three Endpoints)

## Overview
This ETL connector fetches Passive DNS data from CIRCL API using three endpoints: 
1. `/query/{domain}`
2. `/get/{ip}`
3. `/get/{hash}`
Data is loaded into MongoDB with ingestion timestamps.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
