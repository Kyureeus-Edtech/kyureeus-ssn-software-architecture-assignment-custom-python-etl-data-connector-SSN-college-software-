
# SonarQube Metrics ETL Project

This project fetches SonarQube metrics for a specific project and stores them in MongoDB using Python. It uses the SonarQube API to retrieve project-level metrics such as bugs, code smells, vulnerabilities, coverage, and duplication density.

---

## Project Structure

```

A2/
├── n.py                  # Main ETL script
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation

````

---

##  Requirements

- Python 3.10+  
- MongoDB running locally or on a remote server  
- SonarQube Community Edition running locally (http://localhost:9000)  
- SonarScanner installed for project analysis  

---

##  Environment Variables

Create a `.env` file in the project root with the following:

```env
PORT=4000
SONAR_API_BASE=http://localhost:9000/api
SONAR_TOKEN=sqa_e6b6d99027a85d57c66b6dcf7dd2eca7f0704026
DB_URI=mongodb://localhost:27017/vi
SONAR_PROJECT_KEY=VIGS
````

##  Usage

1. **Analyze your project using SonarScanner**:

```bash
sonar-scanner ^
  -Dsonar.projectKey=VIGS ^
  -Dsonar.sources=. ^
  -Dsonar.host.url=http://localhost:9000 ^
  -Dsonar.token=<your_sonar_token_here>
```

This step uploads your code metrics to SonarQube.

2. **Run the Python ETL script**:

```bash
python etl_connector.py
```

The script will:

* Fetch metrics from the SonarQube API
* Transform the data
* Insert the metrics into the MongoDB collection `sonar_metrics`

---

##  Metrics Fetched

* `bugs`
* `code_smells`
* `vulnerabilities`
* `coverage`
* `duplicated_lines_density`

Each record also includes a `timestamp` for when the data was fetched.

---

## Output

Example document inserted into MongoDB:

```json
{
  "project_key": "VIGS",
  "timestamp": "2025-10-15T09:34:07.882215",
  "coverage": "0.0",
  "bugs": "0",
  "code_smells": "1",
  "duplicated_lines_density": "0.0",
  "vulnerabilities": "0"
}
```

---

##  Dependencies

Install dependencies using:

```bash
pip install -r requirements.txt
```

**Example `requirements.txt`:**

```
requests
pymongo
python-dotenv
```

---

##  Notes

* Make sure SonarQube server is running at `http://localhost:9000` before running the script.
* Run `sonar-scanner` on your project to generate metrics before fetching them via the script.
* The ETL script uses timezone-aware UTC datetimes in the latest Python versions.

---

##  References

* [SonarQube API Documentation](https://sonarcloud.io/web_api)
* [MongoDB Python Driver (PyMongo)](https://pymongo.readthedocs.io/)


