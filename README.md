# HIBP ETL Data Connector

This project extracts data from [HaveIBeenPwned v3 API](https://haveibeenpwned.com/API/v3), transforms it, and loads it into MongoDB Atlas.

## Setup
```bash
# Clone repo
git clone <repo_url>
cd custom-python-etl-data-connector-hibp

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate # Linux/Mac

# Install dependencies
pip install -r requirements.txt
