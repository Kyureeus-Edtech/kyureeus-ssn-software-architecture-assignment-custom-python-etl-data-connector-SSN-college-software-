# NVD CVE ETL Connector

This Python script extracts CVE vulnerability data from the NVD API, transforms it, and loads it into a MongoDB collection.

## Setup

1. Clone the repository.

2. Create a `.env` file with;

   ```
   NVD_API_KEY=your_api_key_here
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

## Run

```
python3 etl_connector.py
```

## Output

The script creates a MongoDB database named `etl_project` and a collection named `nvd_cves_raw` containing CVE data.
