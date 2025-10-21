# Custom Python ETL Data Connector

**File**: README.md  
**Author**: Rohith Arumugam S - 31222250001110
**Assignment**: Software Architecture - Custom Python ETL Data Connector  
**Institution**: Kyureeus EdTech, SSN CSE  
**Data Source**: CISA KEV Catalog (Entry #16 from provided connector list)

## Overview

This project implements a robust ETL (Extract, Transform, Load) pipeline that connects to the **CISA Known Exploited Vulnerabilities (KEV) Catalog**, processes critical cybersecurity vulnerability data, and stores it in a MongoDB database. The connector follows secure coding practices and handles real-world vulnerability intelligence from the U.S. Cybersecurity and Infrastructure Security Agency (CISA).

## Features

- Secure API configuration using environment variables
- Robust error handling and logging
- KEV data transformation with risk assessment
- MongoDB integration with proper indexing
- Rate limiting compliance
- Comprehensive data validation
- Pipeline statistics and monitoring
- Real cybersecurity threat intelligence processing

## API Details

**Provider**: U.S. Cybersecurity and Infrastructure Security Agency (CISA)  
**Source**: Entry #16 from provided connector list  
**Base URL**: https://www.cisa.gov  
**Endpoint**: /sites/default/files/feeds/known_exploited_vulnerabilities.json  
**Method**: GET  
**Authentication**: None required (public API)  
**Rate Limits**: Conservative 2-second delays (respectful usage)  
**Response Format**: JSON with comprehensive KEV catalog data

### API Response Structure
```json
{
  "title": "CISA Catalog of Known Exploited Vulnerabilities",
  "catalogVersion": "2024.01.01",
  "dateReleased": "2024-01-01T00:00:00.0000Z",
  "count": 1000,
  "vulnerabilities": [
    {
      "cveID": "CVE-2024-XXXX",
      "vendorProject": "Microsoft",
      "product": "Windows",
      "vulnerabilityName": "Remote Code Execution Vulnerability",
      "dateAdded": "2024-01-01",
      "shortDescription": "Description of the vulnerability...",
      "requiredAction": "Apply updates per vendor instructions.",
      "dueDate": "2024-02-01",
      "knownRansomwareCampaignUse": "Known",
      "notes": "Additional context..."
    }
  ]
}
```

## Project Structure

```
/cisa-kev-etl-connector/
├── etl_connector.py          # Main ETL script
├── .env                      # Environment variables (NOT COMMITTED)
├── requirements.txt          # Python dependencies
├── README.md                 # This documentation
├── .gitignore               # Git ignore rules
└── ENV_TEMPLATE             # Environment variables template
```

## Prerequisites

- Python 3.7 or higher
- MongoDB server (local or remote)
- Internet connection for API access

## Installation and Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
git checkout -b your-branch-name
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root and configure the following variables:

```bash
# Copy the example and modify as needed
cp ENV_TEMPLATE .env
```

Required environment variables:
- `API_BASE_URL`: Base URL for CISA (default: https://www.cisa.gov)
- `API_ENDPOINT`: KEV catalog endpoint (default: /sites/default/files/feeds/known_exploited_vulnerabilities.json)
- `MONGO_URI`: MongoDB connection string (default: mongodb://localhost:27017/)
- `MONGO_DATABASE`: Database name (default: etl_database)
- `MONGO_COLLECTION`: Collection name (default: cisa_kev_raw)
- `RATE_LIMIT_DELAY`: Delay between API calls in seconds (default: 2.0)

### 5. Start MongoDB
Ensure MongoDB is running on your system:
```bash
# For local MongoDB installation
mongod

# Or use MongoDB Atlas cloud service
```

## Usage

### Run the ETL Pipeline
```bash
python etl_connector.py
```

### Expected Output
The script will:
1. Connect to MongoDB
2. Extract KEV data from CISA catalog (complete dataset)
3. Transform and validate the vulnerability data
4. Load data into MongoDB with proper indexing
5. Display pipeline statistics

### Example Log Output

```
2024-08-14 10:30:00,123 - INFO - Starting CISA KEV ETL pipeline execution
2024-08-14 10:30:01,456 - INFO - Successfully connected to MongoDB: etl_database.cisa_kev_raw
2024-08-14 10:30:02,789 - INFO - Extracting KEV data from: https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json
2024-08-14 10:30:03,012 - INFO - CISA KEV Catalog Version: 2024.08.14
2024-08-14 10:30:03,234 - INFO - Successfully extracted 1000 KEV records
2024-08-14 10:30:03,567 - INFO - Successfully transformed 1000 KEV records
2024-08-14 10:30:04,890 - INFO - Data load completed: 1000 inserted, 0 updated
2024-08-14 10:30:04,890 - INFO - ETL pipeline completed successfully in 4.77 seconds
```

## Data Schema

### Transformed Document Structure
```json
{
  "_id": "ObjectId",
  "original_data": {
    "cveID": "CVE-2024-XXXX",
    "vendorProject": "Microsoft",
    "product": "Windows",
    "vulnerabilityName": "Remote Code Execution",
    "dateAdded": "2024-01-01",
    "shortDescription": "...",
    "requiredAction": "Apply updates...",
    "dueDate": "2024-02-01",
    "knownRansomwareCampaignUse": "Known"
  },
  "etl_metadata": {
    "ingestion_timestamp": "2024-08-14T10:30:03.234Z",
    "source": "cisa_kev_catalog",
    "version": "1.0",
    "record_id": "CVE-2024-XXXX",
    "data_quality_score": 1.0
  },
  "cve_id": "CVE-2024-XXXX",
  "vendor_project": "Microsoft",
  "product": "Windows",
  "vulnerability_name": "Remote Code Execution",
  "short_description": "Description...",
  "required_action": "Apply updates...",
  "date_added": "2024-01-01",
  "due_date": "2024-02-01",
  "known_ransomware_use": "Known",
  "is_recent_addition": true,
  "is_overdue": false,
  "risk_level": "CRITICAL",
  "days_since_added": 14,
  "days_until_due": 17,
  "catalog_version": "2024.08.14"
}
```

### MongoDB Indexes
- `etl_metadata.ingestion_timestamp`: For time-based queries
- `cve_id`: Unique index for duplicate prevention
- `risk_level`: For risk-based filtering
- `known_ransomware_use`: For ransomware campaign analysis
- `is_overdue`: For compliance tracking
- `date_added`: For temporal analysis

## Error Handling

The connector handles various error scenarios:
- Network connectivity issues
- API rate limiting (429 responses)
- Invalid JSON responses
- MongoDB connection failures
- Data validation errors
- Individual record processing failures

## Security Features

- Environment variables for sensitive configuration
- .env file excluded from version control
- Secure MongoDB connection handling
- Input validation and sanitization
- Proper session management

## Testing and Validation

### Manual Testing
```bash
# Test MongoDB connection
python -c "from etl_connector import CISAKEVETLConnector; CISAKEVETLConnector().connect_to_mongodb()"

# Test API connectivity
curl https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json
```

### Data Validation
The pipeline includes automatic validation for:
- CVE ID presence and format
- Vendor and product information completeness
- Date format validation and parsing
- Required action field presence
- Risk level assessment accuracy
- Ransomware campaign usage flags

## Monitoring and Logging

- Comprehensive logging to both file and console
- Pipeline execution statistics
- Data quality metrics
- Risk assessment analytics
- Error tracking and reporting

## Troubleshooting

### Common Issues

**MongoDB Connection Error**
- Ensure MongoDB is running
- Check connection string in .env
- Verify network connectivity

**API Request Failures**
- Check internet connectivity
- Verify CISA API endpoint URL
- Review rate limiting settings

**Import Errors**
- Ensure all dependencies are installed
- Check Python version compatibility
- Activate virtual environment

### Debug Mode
Set `LOG_LEVEL=DEBUG` in .env for detailed logging.

## Performance Considerations

- Efficient MongoDB operations with proper indexing
- Connection pooling for API requests
- Memory-efficient data processing
- Configurable rate limiting
- Optimized data transformation algorithms

## KEV Data Insights

This connector processes CISA's authoritative list of Known Exploited Vulnerabilities, providing:

- **Critical Threat Intelligence**: Real vulnerabilities actively exploited in the wild
- **Risk Assessment**: Automated risk level calculation based on ransomware usage and other factors
- **Compliance Tracking**: Due date monitoring for required remediation actions
- **Temporal Analysis**: Recent additions and historical trend tracking
- **Vendor Intelligence**: Comprehensive vendor and product vulnerability mapping

## What Your Pipeline Successfully Does

1. **Extract**: Connects to CISA KEV Catalog with proper rate limiting
2. **Transform**: 
   - Processes known exploited vulnerability data
   - Adds risk assessment and compliance metadata
   - Creates derived fields (risk levels, overdue status, days calculations)
   - Handles complex date parsing and validation
3. **Load**: 
   - Stores data in MongoDB with comprehensive indexing
   - Handles duplicates with upsert operations
   - Maintains audit trails with timestamps

## Future Enhancements

- Support for historical KEV catalog versions
- Real-time vulnerability monitoring alerts
- Integration with vulnerability scanners
- Advanced risk analytics and reporting
- Automated compliance reporting
- Cross-reference with CVE databases

## Dependencies

- `requests`: HTTP library for API calls
- `pymongo`: MongoDB Python driver
- `python-dotenv`: Environment variable management
- `datetime`: Date/time processing for KEV analysis

## Contributing

1. Create a feature branch from main
2. Implement changes with proper testing
3. Update documentation as needed
4. Submit pull request with descriptive commit message

## License

This project is created for educational purposes as part of the Software Architecture course at SSN CSE through Kyureeus EdTech.

---

**Submission Details**  
Student: Rohith Arumugam S 
Roll Number: 3122225001110
Branch: RohithArumugamS_3122225001110_CSE_B 
Submission Date: August 14, 2025  
Data Source: CISA Known Exploited Vulnerabilities Catalog (Entry #16)