# OTX IPv4 General Threat Intelligence API

This project provides a custom ETL connector to interact with the **AlienVault OTX (Open Threat Exchange)** API to fetch threat intelligence details for a given IPv4 address.

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

Run for a single IP:
```bash
python etl_connector.py 8.8.8.8
```

Run for multiple IPs:
```bash
python etl_connector.py 8.8.8.8 1.1.1.1
```
If no IP is provided, the script defaults to 8.8.8.8.

---

## API Endpoint Details
**Base URL:** `https://otx.alienvault.com/api/v1/indicators/IPv4/<IPv4_Address>/general`

Method: `GET`

---

## Example Output


### Logs

<img width="1423" height="284" alt="Screenshot 2025-08-13 193023" src="https://github.com/user-attachments/assets/a7c397c4-7ad8-43e3-90b7-27f37655f52b" />


### MongoDB
<img width="739" height="538" alt="Screenshot 2025-08-13 194540" src="https://github.com/user-attachments/assets/d0e902ce-4033-423b-b40c-41c2533373ca" />
<img width="516" height="544" alt="Screenshot 2025-08-13 194547" src="https://github.com/user-attachments/assets/a968c61d-5e22-456a-b93e-9e578a94970f" />
<img width="618" height="246" alt="Screenshot 2025-08-13 194552" src="https://github.com/user-attachments/assets/40383e65-35fa-4d70-a558-5e2f3f9fb12b" />




## Author
**Name:** Aashika Jetti  
**Roll No.:** 3122225001050 

---

