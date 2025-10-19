# 🚀 Quick Start Guide - Cloudflare ETL Connector

**Student:** Rithika S (3122225001705)  
**Branch:** RithikaS_3122225001705_A_ETL2

---

## ⚡ Quick Setup (5 Minutes)

### 1. Install Dependencies

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install packages
pip install -r requirements.txt
```

### 2. Set Up MongoDB

```bash
# If MongoDB is not installed:
# macOS:
brew install mongodb-community

# Start MongoDB
brew services start mongodb-community

# Verify MongoDB is running
mongosh --eval "db.version()"
```

### 3. Create Environment File

```bash
# Copy template to .env
cp env_template.txt .env

# Edit .env with your settings (optional - defaults work fine)
nano .env
```

**Default `.env` content:**

```env
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=cloudflare_etl_db
COLLECTION_NAME=cloudflare_trace_raw
```

### 4. Run the ETL Pipeline

```bash
python etl_connector.py
```

### 5. Verify Data in MongoDB

```bash
# Open MongoDB shell
mongosh

# Use the database
use cloudflare_etl_db

# View the data
db.cloudflare_trace_raw.find().pretty()

# Count documents
db.cloudflare_trace_raw.countDocuments()

# Exit
exit
```

---

## 📋 Expected Output

When you run `python etl_connector.py`, you should see:

```
✓ Successfully connected to MongoDB: cloudflare_etl_db

======================================================================
EXTRACTION PHASE - Fetching data from Cloudflare endpoints
======================================================================

→ Extracting data from trace...
✓ Successfully extracted 15 fields from trace

→ Extracting data from trace_alternate...
✓ Successfully extracted 15 fields from trace_alternate

→ Extracting data from ipinfo...
✓ Successfully extracted 15 fields from ipinfo

✓ Extraction complete: 3/3 endpoints successful

======================================================================
TRANSFORMATION PHASE - Processing and cleaning data
======================================================================

✓ Transformation complete: Document ready for MongoDB

======================================================================
LOAD PHASE - Inserting data into MongoDB
======================================================================

✓ Successfully inserted document

======================================================================
✓ ETL PIPELINE COMPLETED SUCCESSFULLY
======================================================================
```

---

## 🔍 What the Connector Does

1. **Extracts** data from 3 Cloudflare endpoints:

   - `https://www.cloudflare.com/cdn-cgi/trace`
   - `https://1.1.1.1/cdn-cgi/trace`
   - `https://cloudflare.com/cdn-cgi/trace`

2. **Transforms** the data:

   - Parses key-value pairs
   - Converts data types
   - Adds metadata (timestamp, student info)
   - Enriches with derived fields

3. **Loads** into MongoDB:
   - Collection: `cloudflare_trace_raw`
   - Database: `cloudflare_etl_db`
   - Includes ingestion timestamps

---

## 🐛 Troubleshooting

### MongoDB Connection Error

```bash
# Error: "ServerSelectionTimeoutError"
# Solution: Start MongoDB
brew services start mongodb-community
```

### Import Error

```bash
# Error: "ModuleNotFoundError: No module named 'requests'"
# Solution: Activate virtual environment and install packages
source venv/bin/activate
pip install -r requirements.txt
```

### Permission Error

```bash
# Error: "Permission denied"
# Solution: Ensure MongoDB has proper permissions
sudo chown -R $(whoami) /usr/local/var/mongodb
```

---

## 📤 Git Commands for Submission

### Check Current Branch

```bash
git branch
# Should show: * RithikaS_3122225001705_A_ETL2
```

### Stage and Commit Files

```bash
# Check status
git status

# Add files (excluding .env)
git add .gitignore requirements.txt etl_connector.py CLOUDFLARE_CONNECTOR_README.md QUICKSTART.md env_template.txt

# Commit with proper message format
git commit -m "RithikaS_3122225001705: Complete Cloudflare ETL connector implementation

- Implemented ETL pipeline with 3 Cloudflare endpoints
- Added comprehensive error handling and validation
- Created detailed documentation
- Added .gitignore to exclude sensitive files
- Included requirements.txt with dependencies"

# Push to branch
git push origin RithikaS_3122225001705_A_ETL2
```

### Verify No Sensitive Files

```bash
# Check what will be committed
git status

# Verify .env is not tracked
git ls-files | grep .env
# Should return nothing (only env_template.txt is fine)
```

---

## ✅ Pre-Submission Checklist

Before pushing to GitHub, verify:

- [ ] `.env` file is NOT being committed (check with `git status`)
- [ ] All code files are added and committed
- [ ] Documentation files are included
- [ ] requirements.txt is present
- [ ] .gitignore file is present
- [ ] Virtual environment is NOT being committed
- [ ] Commit message includes name and roll number
- [ ] Code runs without errors
- [ ] Data is successfully inserted into MongoDB

---

## 📁 Files to Commit

✅ **DO COMMIT:**

- `.gitignore`
- `requirements.txt`
- `etl_connector.py`
- `CLOUDFLARE_CONNECTOR_README.md`
- `QUICKSTART.md`
- `env_template.txt`

❌ **DO NOT COMMIT:**

- `.env` (contains credentials)
- `venv/` (virtual environment)
- `__pycache__/`
- `*.pyc`
- `.DS_Store`

---

## 🎯 Next Steps

1. **Test the connector** - Run it at least once successfully
2. **Verify MongoDB data** - Check that data is stored correctly
3. **Review documentation** - Make sure everything is clear
4. **Push to GitHub** - Use the git commands above
5. **Create Pull Request** - Submit for review

---

## 📞 Need Help?

- Check `CLOUDFLARE_CONNECTOR_README.md` for detailed documentation
- Review error messages in the console output
- Verify MongoDB is running: `brew services list`
- Check Python version: `python3 --version` (need 3.8+)
- Post questions in the KYUREEUS/SSN College WhatsApp group

---

**You're ready to submit! Good luck! 🎉**
