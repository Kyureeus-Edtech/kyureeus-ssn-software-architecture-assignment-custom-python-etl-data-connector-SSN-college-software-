# 🧠 Software Architecture Assignment — Custom Python ETL Data Connector  
### API Provider: FilterLists (Public API)

**Student Name:** Vishal S. S  
**Roll Number:** (Add your roll number here)  
**Course:** SSN College of Engineering — CSE  
**Program:** Kyureeus EdTech  

---

## 📌 Project Overview

This project implements a **custom Python ETL (Extract–Transform–Load) data connector** for the **FilterLists API**.  
The connector extracts structured data from multiple endpoints of the API, transforms it for MongoDB compatibility, and loads it into separate collections within a MongoDB database.

The ETL script is designed following **secure coding, modularity, and error handling** practices, aligning with software architecture principles.

---

## ⚙️ API Provider Details

**Base URL:**  



**Available Endpoints:**

| Endpoint | Description | MongoDB Collection |
|-----------|--------------|-------------------|
| `/lists` | Contains metadata about available filter lists | `lists_collection` |
| `/licenses` | Provides licensing details for filter lists | `licenses_collection` |
| `/maintainers` | Information about list maintainers | `maintainers_collection` |
| `/software` | Details of software supported by FilterLists | `software_collection` |
| `/syntaxes` | Lists syntaxes used by different filters | `syntaxes_collection` |
| `/tags` | Categorization tags used for lists | `tags_collection` |

Each endpoint’s response is stored in a **separate MongoDB collection** for better modularity and query performance.

---

## 🔐 Secure Configuration Using `.env`

Sensitive credentials and configuration values are stored in a `.env` file (excluded from Git).  

**Example `.env` file:**
```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=filterlists_db
API_BASE_URL=https://api.filterlists.com
