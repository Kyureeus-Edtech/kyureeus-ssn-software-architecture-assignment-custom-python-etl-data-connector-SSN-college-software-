# Custom Python ETL Data Connector: SonarQube Metrics

## 🎯 Goal
This Python script implements an Extract, Transform, Load (ETL) pipeline to connect to a local SonarQube instance, extract code quality metrics, and securely store them in a MongoDB database. This adheres to the Software Architecture Assignment guidelines.

## 🛠️ Prerequisites
1.  **Running SonarQube:** The SonarQube server must be running locally on the configured port **9002**.
2.  **MongoDB:** A local MongoDB instance must be running on the default port **27017**.
3.  **Python Dependencies:** The packages listed in `requirements.txt` must be installed.

## 📦 Project Structure
/your-branch-name/
├── etl_connector.py    # Main ETL logic script.
├── .env                # Securely stores credentials (Ignored by Git).
├── requirements.txt    # Lists Python dependencies.
└── README.md           # This documentation file.

## 🛡️ Secure Authentication

All API credentials and connection strings are managed securely via a local **`.env`** file. The credentials are loaded into the Python script using the `python-dotenv` library.

The following variables **must** be set in your local `.env` file:

```dotenv
# .env file content
SONARQUBE_BASE_URL=http://localhost:9002/
SONARQUBE_TOKEN=sqa_your_generated_token
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/
