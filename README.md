# 🛠 MalShare ETL Connector

## 📌 Description
This Python ETL (Extract → Transform → Load) script connects to the **MalShare API**, retrieves the latest malware hash list, transforms it into a MongoDB-compatible format, and stores it in a MongoDB collection.  
It follows **secure coding practices** by keeping API keys in a `.env` file and excluding them from version control.

---

## 🌐 API Details
- **Base URL:** `https://malshare.com/api.php`
- **Endpoint:**  
  ```
  ?api_key=[API_KEY]&action=getlist
  ```
- **Parameters:**
  - `api_key` → Your personal MalShare API key (stored in `.env`).
  - `action` → `"getlist"` to get the latest malware hashes.
- **Rate Limits:** MalShare enforces request limits based on your account type.
- **Response Format:** May be JSON or plain text depending on the API version and account settings.

---

## 📂 Project Structure
```
/custom-python-etl-data-connector-Abishnaaa/
├── etl_connector.py        # Main ETL script
├── .env                    # Stores sensitive credentials (NOT committed)
├── requirements.txt        # Python dependencies
├── README.md               # Documentation
└── .gitignore              # Ignore .env and unnecessary files
```

---

## 🔒 Secure Credentials
- Create a `.env` file in the same directory as your script:
```env
MALSHARE_API_KEY=your_api_key_here
MONGO_URI=mongodb://localhost:27017
```
- **Important:** `.env` must be listed in `.gitignore` so it is never committed.

---

## ⚙ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Kyureeus-Edtech/custom-python-etl-data-connector-Abishnaaa.git
cd custom-python-etl-data-connector-Abishnaaa
git checkout Abishna-3122225001005-A
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Start MongoDB
####  Local MongoDB Server
- Make sure MongoDB is installed and running:
```bash
mongod
```
- Default connection: `mongodb://localhost:27017`



### 4️⃣ Run the ETL Script
```bash
python etl_connector.py
```

---

## 📦 How It Works

### Extract
- Connects to MalShare API using your API key.
- Fetches latest malware hashes.

### Transform
- Converts API response into structured JSON.
- Adds a `fetched_at` timestamp.

### Load
- Inserts transformed data into MongoDB collection: `malshare_raw`.

---

## 🧪 Example Output in MongoDB
```json
{
  "_id": "64cfd821b32f1c8d2a000001",
  "hash": "abc1234567890abcdef...",
  "source": "malshare",
  "fetched_at": "2025-08-14T10:00:00Z"
}
```

---

## 🚨 Error Handling
- Handles invalid API key errors.
- Skips empty or invalid responses.
- Catches connection failures to API or MongoDB.
- Supports plain-text and JSON API outputs.

---

## 📜 Requirements
- Python 3.8+
- MongoDB (local or cloud)
- Packages in `requirements.txt`:
```
requests
pymongo
python-dotenv
```

---

## ✍ Author
- **Name:** Abishna A
- **Roll Number:** 3122225001005

---

## 📢 Notes
- Respect MalShare's rate limits.
- Keep your API key private at all times.
- Use separate MongoDB collections for different connectors.

l