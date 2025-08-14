# Custom Python ETL Data Connector

**Author:** Srivathsan Sundarrajan  
**Roll No:** 3122225001141  

## 📌 Overview
This project implements a **Custom Python ETL (Extract, Transform, Load) Data Connector** that fetches data from a specified API, processes/transforms it, and stores the results in a chosen format (CSV, JSON, or database).

The project is part of the **Software Architecture Assignment 1**.

---

## 🛠 Features
- Extract data from a public API.
- Transform and clean the retrieved data.
- Load the processed data into a file or database.
- Supports environment-based configuration using `.env`.
- Easy to extend for multiple APIs.

---

## 📂 Project Structure
custom-python-etl-data-connector-Srivathsansundarrajan/
│
├── .github/ # GitHub configuration
├── venv/ # Virtual environment
├── .env # Environment variables (API keys, URLs)
├── .gitignore # Ignored files for Git
├── etl.py # Main ETL script
├── README.md # Documentation
└── requirements.txt # Python dependencies


---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone <repository-url>
cd custom-python-etl-data-connector-Srivathsansundarrajan

Create and Activate Virtual Environment :

    python -m venv venv

    # Windows
    venv\Scripts\activate

    # macOS/Linux
    source venv/bin/activate

Install Dependencies : 

    pip install -r requirements.txt

Configure .env File :

    MALSHARE_API_KEY=your_api_key_here
    MONGO_URI=mongodb://localhost:27017


