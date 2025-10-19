# SonarQube ETL Data Connector

This project is a custom **Extract–Transform–Load (ETL)** Python script that connects to a local **SonarQube server**, extracts data from its public REST APIs (metrics, quality profiles, and rules), transforms it into a clean JSON format, and stores it into MongoDB collections for analysis and reporting.

---

## ⚙️ Prerequisites

- **Python** 3.9 or newer
- **MongoDB** installed and running locally or accessible remotely
- `pip` for installing dependencies

---

## 📌 Features
- **Extracts** the latest data from SonarQube API endpoints (`/api/metrics/search`, `/api/qualityprofiles/search`, `/api/rules/search`)
- **Transforms** the data by:
  - Flattening nested JSON structures (e.g., metrics inside profiles)
  - Cleaning and normalizing field names for MongoDB
  - Handling missing or null values
- **Loads** each record into MongoDB as a structured document with relevant fields (`id`, `key`, `name`, `type`, `description`, `domain`, `direction`, `qualitative`, etc.)
- Supports configuration via environment variables for API credentials, endpoints, and MongoDB connection

---

## 🔌 Data Source / API

**Base URL:**  
`http://localhost:9000`

**Endpoint 1:**  
`/api/metrics/search`

When fetched, the endpoint returns JSON containing metrics. Each metric can be stored as a separate record in MongoDB.

**Example JSON row:**
{
    "metrics": [
        {
            "id": "c707e4e5-7054-4a66-a982-d79d463c6842",
            "key": "accepted_issues",
            "type": "INT",
            "name": "Accepted Issues",
            "description": "Accepted issues",
            "domain": "Issues",
            "direction": -1,
            "qualitative": false,
            "hidden": false
        }, ... ] }

**Endpoint 2:**  
`/api/qualityprofiles/search`

When fetched, the endpoint returns quality profile information for projects. Each profile can be stored as a separate document in MongoDB..

**Example JSON row:**
{
    "profiles": [
        {
            "key": "####",
            "name": "Sonar way",
            "language": "azureresourcemanager",
            "languageName": "Azure Resource Manager",
            "isInherited": false,
            "isDefault": true,
            "activeRuleCount": 31,
            "activeDeprecatedRuleCount": 0,
            "rulesUpdatedAt": "2025-10-19T08:56:36+0000",
            "isBuiltIn": true,
            "actions": {
                "edit": false,
                "setAsDefault": false,
                "copy": true,
                "associateProjects": false,
                "delete": false
            }
        }, ... ]}

**Endpoint 3:**  
`/api/rules/search`

When fetched, the endpoint returns rules for a specific language or quality profile. Can store each rule as a separate MongoDB document.

**Example JSON row:**
{
    "total": 4061,
    "p": 1,
    "ps": 100,
    "rules": [
    {
            "key": "php:S1131",
            "repo": "php",
            "name": "Lines should not end with trailing whitespaces",
            "createdAt": "2025-10-19T14:25:57+0530",
            "severity": "MINOR",
            "status": "READY",
            "isTemplate": false,
            "tags": [],
            "sysTags": [
                "convention",
                "psr2"
            ],
            "lang": "php",
            "langName": "PHP",
            "params": [],
            "defaultDebtRemFnType": "CONSTANT_ISSUE",
            "debtRemFnType": "CONSTANT_ISSUE",
            "type": "CODE_SMELL",
            "defaultRemFnType": "CONSTANT_ISSUE",
            "defaultRemFnBaseEffort": "1min",
            "remFnType": "CONSTANT_ISSUE",
            "remFnBaseEffort": "1min",
            "remFnOverloaded": false,
            "scope": "MAIN",
            "isExternal": false,
            "descriptionSections": [
                {
                    "key": "root_cause",
                    "content": "Trailing whitespaces bring no information, they may generate noise when comparing different versions of the same file, and they can create bugs when they appear after a marking a line continuation. They should be systematically removed.An automated code formatter allows to completely avoid this family of issues and should be used wherever possible.Exceptions:Lines containing only whitespaces."
                }
            ],
            "educationPrinciples": [],
            "updatedAt": "2025-10-19T14:25:57+0530",
            "cleanCodeAttribute": "FORMATTED",
            "cleanCodeAttributeCategory": "CONSISTENT",
            "impacts": [
                {
                    "softwareQuality": "MAINTAINABILITY",
                    "severity": "LOW"
                }
            ]
        }, ...] }

---

## 📂 Project Structure

    custom-python-etl-data-connector-Athish369/
    │
    ├── etl_connector1.py # ETL script for first endpoint: Extract, Transform, Load
    ├── etl_connector2.py # ETL script for second endpoint: Extract, Transform, Load
    ├── etl_connector3.py # ETL script for third endpoint: Extract, Transform, Load
    ├── requirements.txt # Python dependencies list
    ├── .env # Environment variables (not tracked in git)
    ├── .gitignore # Git ignore rules
    ├── README.md # Project documentation

---

## ▶️ Usage

Run the ETL pipeline:
    python etl_connector1.py
![OUTPUT after running etl_connector1.py](images/SQ_etl1.png)

    python etl_connector2.py
![OUTPUT after running etl_connector2.py](images/SQ_etl2.png)
    
    python etl_connector3.py
![OUTPUT after running etl_connector3.py](images/SQ_etl3.png)



**Process Flow:**
1. **Fetch** data from `BASEURL + API_ENDPOINT`
2. **Parse & clean** Nested JSON to structured records
3. **Insert** cleaned records into MongoDB

---

## 📂 MongoDB Output Format

Documents in MongoDB will look like:
**Endpoint 1:**  
`/api/metrics/search`
{
  "_id": {
    "$oid": "68f4b13a204bbc8a056b053f"
  },
  "id": "c707e4e5-7054-4a66-a982-d79d463c6842",
  "key": "accepted_issues",
  "type": "INT",
  "name": "Accepted Issues",
  "description": "Accepted issues",
  "domain": "Issues",
  "direction": -1,
  "qualitative": false,
  "hidden": false,
  "parent_id": null
}

![Sonarqube metrics in MongoDB](images/SQ_Metrics_Mongo.png)

**Endpoint 2:**  
`/api/qualityprofiles/search`
{
  "_id": {
    "$oid": "68f4b27678e4182e9dd58f84"
  },
  "key": "871e3a25-3bb9-49c0-8004-255f2c874caf",
  "name": "Sonar way",
  "language": "azureresourcemanager",
  "languageName": "Azure Resource Manager",
  "isInherited": false,
  "isDefault": true,
  "activeRuleCount": 31,
  "activeDeprecatedRuleCount": 0,
  "rulesUpdatedAt": "2025-10-19T08:56:36+0000",
  "isBuiltIn": true,
  "actions": {
    "edit": false,
    "setAsDefault": false,
    "copy": true,
    "associateProjects": false,
    "delete": false
  }
}

![Sonarqube quality profiles in MongoDB](images/SQ_QualityProfiles_Mongo.png)

**Endpoint 3:**  
`/api/rules/search`
{
  "_id": {
    "$oid": "68f4b3e7eedbc0a537f3f414"
  },
  "key": "php:S1131",
  "repo": "php",
  "name": "Lines should not end with trailing whitespaces",
  "createdAt": "2025-10-19T14:25:57+0530",
  "severity": "MINOR",
  "status": "READY",
  "isTemplate": false,
  "tags": [],
  "sysTags": [
    "convention",
    "psr2"
  ],
  "lang": "php",
  "langName": "PHP",
  "params": [],
  "defaultDebtRemFnType": "CONSTANT_ISSUE",
  "debtRemFnType": "CONSTANT_ISSUE",
  "type": "CODE_SMELL",
  "defaultRemFnType": "CONSTANT_ISSUE",
  "defaultRemFnBaseEffort": "1min",
  "remFnType": "CONSTANT_ISSUE",
  "remFnBaseEffort": "1min",
  "remFnOverloaded": false,
  "scope": "MAIN",
  "isExternal": false,
  "descriptionSections": [
    {
      "key": "root_cause",
      "content": "Trailing whitespaces bring no information, they may generate noise when comparing different versions of the same file, and they can create bugs when they appear after a marking a line continuation. They should be systematically removed.An automated code formatter allows to completely avoid this family of issues and should be used wherever possible.Exceptions:Lines containing only whitespaces."
    }
  ],
  "educationPrinciples": [],
  "updatedAt": "2025-10-19T14:25:57+0530",
  "cleanCodeAttribute": "FORMATTED",
  "cleanCodeAttributeCategory": "CONSISTENT",
  "impacts": [
    {
      "softwareQuality": "MAINTAINABILITY",
      "severity": "LOW"
    }
  ]
}

![Sonarqube rules in MongoDB](images/SQ_Rules_Mongo.png)

---

## Limitations

**Paginated Endpoints:**

`/api/rules/search` is paginated. The current ETL fetches only a single page by default. To retrieve all rules, the ETL should loop through all pages using p (page number) and ps (page size).

**Authentication Required:**

Accessing SonarQube APIs requires valid credentials. The ETL uses HTTP Basic Auth. Ensure .env contains SONARQUBE_USERNAME and SONARQUBE_PASSWORD.

**Local SonarQube Only:**

The ETL is currently designed for a local or accessible SonarQube server. Remote deployments may require network adjustments.
