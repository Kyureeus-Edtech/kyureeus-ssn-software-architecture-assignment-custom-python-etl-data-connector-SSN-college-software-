# Simplified ETL Connectors for CERT.at Threat Intelligence

A single-file ETL pipeline for processing CERT.at threat intelligence data from CSV and RSS feeds.

## Features

- **CSV Processing**: Extract, transform, and load CSV threat intelligence data
- **RSS Processing**: Fetch and process RSS security feeds from CERT.at
- **MongoDB Integration**: Store processed data in MongoDB with proper indexing
- **Sample Data Generation**: Generate realistic sample CSV data for testing
- **Unified Interface**: Single class handles all ETL operations

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install pymongo feedparser python-dotenv python-dateutil
   ```

2. **Setup MongoDB**:
   ```bash
   # Using Docker (recommended)
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   
   # Or install MongoDB locally
   ```

3. **Run the Pipeline**:
   ```bash
   # Run complete pipeline with sample data generation
   python etl_connectors.py --generate-sample
   
   # Run only CSV pipeline
   python etl_connectors.py --csv-only --generate-sample
   
   # Run only RSS pipeline
   python etl_connectors.py --rss-only
   ```

## Usage Examples

```python
from etl_connectors import ETLConnectors

# Initialize ETL connectors
etl = ETLConnectors(
    mongo_uri='mongodb://localhost:27017/',
    db_name='certat_intelligence_db',
    data_dir='data'
)

# Run complete pipeline
success = etl.run_complete_pipeline(generate_sample=True)

# Run only CSV pipeline
csv_success = etl.run_csv_pipeline(generate_sample=True)

# Run only RSS pipeline
rss_success = etl.run_rss_pipeline()

# Get collection statistics
stats = etl.get_collection_stats()
print(f"Total documents: {sum(stats.values())}")
```

## Data Sources

### CSV Feeds
- **Malware Infections**: Infected systems and C2 communications
- **Vulnerable Systems**: Systems with known vulnerabilities  
- **Brute Force Attacks**: Brute force attack attempts

### RSS Feeds
- **Warnings**: Security warnings and alerts
- **Blog**: Security blog posts (German/English)
- **Daily Reports**: Daily security summaries
- **Current News**: Latest security developments
- **Special Topics**: In-depth security analyses

## MongoDB Collections

### CSV Collections
- `threats_csv_malware_infections`
- `threats_csv_vulnerable_systems`
- `threats_csv_brute_force_attacks`

### RSS Collections
- `rss_warnings`
- `rss_blog`
- `rss_blog_en`
- `rss_daily_reports`
- `rss_current`
- `rss_specials`

## Configuration

Set environment variables or pass parameters directly:

```python
# Environment variables
MONGO_URI=mongodb://localhost:27017/
DB_NAME=certat_intelligence_db

# Or pass directly
etl = ETLConnectors(
    mongo_uri='mongodb://localhost:27017/',
    db_name='my_database',
    data_dir='custom_data'
)
```

## Requirements

- Python 3.8+
- MongoDB 4.4+
- Internet connection (for RSS feeds)

## Dependencies

- pymongo
- feedparser
- python-dotenv
- python-dateutil
