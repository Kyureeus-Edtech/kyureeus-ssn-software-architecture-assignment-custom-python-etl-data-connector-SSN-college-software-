# ExploitDB ETL Pipeline

This project extracts, transforms, and loads ExploitDB CSV data into a MongoDB database.

## Features

- Downloads and parses ExploitDB CSV data.
- Cleans and transforms date columns (`date_published`, `date_added`, `date_updated`).
- Handles missing/invalid data and skips records without an `id`.
- Loads cleaned data into MongoDB.
- Retries downloads on network errors (basic rate limit handling).
- Logs errors and warnings for easier debugging.

## Requirements

- Python 3.8+
- MongoDB running locally (default URI: `mongodb://localhost:27017/`)
- Python packages: `requests`, `pandas`, `pymongo`

Install dependencies:
```sh
pip install -r requirements.txt
```

## Usage

Run the ETL pipeline:
```sh
python etl_exploitdb.py
```

## Configuration

- **CSV Source:**  
  [ExploitDB CSV](https://gitlab.com/exploit-database/exploitdb/-/raw/main/files_exploits.csv)
- **MongoDB URI:**  
  `mongodb://localhost:27017/`
- **Database:**  
  `exploitdb`
- **Collection:**  
  `exploits`

## Error Handling & Validation

- Network errors and rate limits are handled with retries and logging.
- Invalid CSV or MongoDB errors are logged and will halt the pipeline.
- Records missing the required `id` field are skipped and logged as warnings.
- Invalid dates are set to `None`.

## Testing & Validation

- Run the script and check MongoDB for loaded data.
- Errors and warnings will be logged to the console.
- For unit tests, create a file like `test_etl_exploitdb.py` and use `pytest` or `unittest`.

## Contact

For issues or questions, please