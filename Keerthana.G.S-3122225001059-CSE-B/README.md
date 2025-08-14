# AlienVault OTX ETL Pipeline

## Author
Name: Keerthana G.S  
Roll Number: 312225001059

---

## Overview
This project implements an ETL (Extract → Transform → Load) pipeline for fetching threat intelligence data (Pulses) from the AlienVault OTX API, transforming it into a structured format, and loading it into a MongoDB collection.

The pipeline:
1. Extracts subscribed OTX pulses using the API and your API key.
2. Transforms the data into a MongoDB-friendly format (cleaned fields, structured objects).
3. Loads the processed data into a MongoDB database.

---

## API Details

Base URL: https://otx.alienvault.com/api/v1/pulses/subscribed  
Authentication: Requires an OTX API Key (OTX_API_KEY)  
Pagination: The API returns paginated results with a "next" URL.  
Data Type: JSON  

Example Pulse Fields:
- id: Unique ID of the pulse
- name: Title of the threat intel report
- description: Summary of the threat
- author_name: Creator of the pulse
- tags: Related threat tags
- created: Creation timestamp
- modified: Last update timestamp
- references: Related external references

---

## Prerequisites

- Python 3.10+
- MongoDB installed locally or remotely
- OTX API Key (Get from AlienVault OTX: https://otx.alienvault.com)
