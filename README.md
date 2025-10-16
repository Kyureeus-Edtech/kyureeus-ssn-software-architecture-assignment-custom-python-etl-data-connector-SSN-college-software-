# Wayback Machine General Website Archive API

This project provides a custom ETL connector to interact with the Wayback Machine API for fetching historical snapshot details for any website URL
---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd repo-name
```


### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create and Activate Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate
```

### 4. Configure Environment Variables
Copy the template file and update it with your actual values:
```bash
cp ENV_TEMPLATE .env
```


### 5. Run the Connector

Run for a url:
```bash
python etl_connector.py https://www.example.com
```
---

## API Endpoints Details

**1. Base URL:** `http://archive.org/wayback/available`

Method: `GET`


**2. Base URL:** `https://web.archive.org/cdx/search/cdx`

Method: `GET`


**3. Base URL:** `https://web.archive.org/web/timemap/json/<URL>`

Method: `GET`


---

## Example Output


### Logs

<img width="1721" height="706" alt="image" src="https://github.com/user-attachments/assets/8baae860-b3ec-4b4b-bd53-f8864fcb9b9a" />



### MongoDB
<img width="1431" height="458" alt="image" src="https://github.com/user-attachments/assets/cd7eb094-256c-4aa9-9a1d-ef7b0f5f0e2b" />

<img width="1416" height="537" alt="image" src="https://github.com/user-attachments/assets/fda87f70-b5c9-4f4f-b240-72f84903cc4b" />






## Author
**Name:** Aashika Jetti  
**Roll No.:** 3122225001050 

---
