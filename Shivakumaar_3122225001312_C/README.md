# MalShare API ETL Connector

**Student Name**: [Shivakumaar]  
**Roll Number**: [3122225001312]  
**Course**: Software Architecture - Kyureeus EdTech Program  
**Institution**: SSN College of Engineering

## 📋 Overview

This ETL (Extract, Transform, Load) connector integrates with the MalShare API to extract malware intelligence data, transform it for compatibility, and load it into a MongoDB collection for analysis and storage.

MalShare is a free community-driven public malware repository that provides access to malware samples and associated metadata for security research and analysis.

## 🚀 Features

- **Secure Authentication**: Uses environment variables for API key management
- **Robust Error Handling**: Implements retry logic, rate limiting, and comprehensive error handling
- **Data Transformation**: Standardizes and enriches raw API data
- **MongoDB Integration**: Efficiently stores data with proper indexing
- **Logging**: Comprehensive logging for monitoring and debugging
- **Data Quality**: Includes completeness scoring and validation

## 🏗️ Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   MalShare  │───▶│  ETL Script  │───▶│  MongoDB    │
│   API       │    │              │    │ Collection  │
└─────────────┘    └──────────────┘    └─────────────┘
                           │
                           ▼
                   ┌──────────────┐
                   │   Logging    │
                   │   System     │
                   └──────────────┘
```

## 📁 Project Structure

```
malshare-etl-connector/
├── etl_connector.py      # Main ETL script
├── .env                  # Environment configuration (not committed)
├── requirements.txt      # Python dependencies
├── README.md            # This documentation
├── .gitignore           # Git ignore rules
├── setup.py             # Setup script
└── test_connector.py    # Unit tests
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8 or higher
- MongoDB server (local or remote)
- MalShare API key (free registration at https://malshare.com)

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd malshare-etl-connector

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Environment Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` file with your credentials:
```bash
# MalShare API Configuration
MALSHARE_API_KEY=your_actual_api_key_here
MALSHARE_BASE_URL=https://malshare.com

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=malware_intelligence

# ETL Configuration
SAMPLE_LIMIT=25
RATE_LIMIT_DELAY=1.0
MAX_RETRIES=3
REQUEST_TIMEOUT=30
```

### Step 3: MongoDB Setup

Ensure MongoDB is running and accessible. The connector will automatically:
- Create the database if it doesn't exist
- Create the collection `malshare_raw`
- Set up appropriate indexes

## 🔧 Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `MALSHARE_API_KEY` | Your MalShare API key | Required |
| `MALSHARE_BASE_URL` | MalShare API base URL | `https://malshare.com` |
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/` |
| `MONGODB_DATABASE` | Target database name | `malware_intelligence` |
| `SAMPLE_LIMIT` | Max samples to process per run | `25` |
| `RATE_LIMIT_DELAY` | Delay between API requests (seconds) | `1.0` |
| `MAX_RETRIES` | Maximum retry attempts | `3` |
| `REQUEST_TIMEOUT` | Request timeout (seconds) | `30` |

## 🚀 Usage

### Basic Usage

Run the ETL pipeline with default settings:

```bash
python etl_connector.py
```

### Advanced Usage

Customize the number of samples to process:

```bash
# Set environment variable
export SAMPLE_LIMIT=100
python etl_connector.py
```

### Programmatic Usage

```python
from etl_connector import MalShareETLConnector

# Initialize connector
connector = MalShareETLConnector()

# Run ETL pipeline
connector.run_etl_pipeline(sample_limit=50)

# Get collection statistics
stats = connector.get_collection_stats()
print(f"Total documents: {stats['total_documents']}")
```

## 🔍 API Endpoints Used

The connector utilizes the following MalShare API endpoints:

| Endpoint | Purpose | Parameters |
|----------|---------|------------|
| `/api.php?action=getlist` | Get list of recent samples | `api_key` |
| `/api.php?action=details` | Get sample details | `api_key`, `hash` |

### Sample API Response Structure

```json
{
  "MD5": "d41d8cd98f00b204e9800998ecf8427e",
  "SHA1": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
  "SHA256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "SSDEEP": "3::",
  "F_TYPE": "PE32 executable",
  "SOURCES": ["source1", "source2"],
  "ADDED": "2024-01-15 10:30:00"
}
```

## 📊 Data Transformation

The ETL process transforms raw API data as follows:

### Input (Raw API Data)
```json
{
  "MD5": "abc123...",
  "SHA1": "def456...",
  "F_TYPE": "PE32 executable",
  "ADDED": "2024-01-15 10:30:00"
}
```

### Output (Transformed Data)
```json
{
  "sha256": "sample_hash",
  "ingestion_timestamp": "2024-01-15T10:30:00Z",
  "source": "malshare_api",
  "connector_version": "1.0",
  "md5": "abc123...",
  "sha1": "def456...",
  "file_type": "PE32 executable",
  "date_added_parsed": "2024-01-15T10:30:00",
  "sample_type": "executable",
  "data_completeness": 0.8,
  "raw_response": { /* original response */ }
}
```

## 🗃️ MongoDB Schema

### Collection: `malshare_raw`

| Field | Type | Description |
|-------|------|-------------|
| `_id` | ObjectId | MongoDB document ID |
| `sha256` | String | Sample SHA256 hash (unique) |
| `ingestion_timestamp` | Date | When data was ingested |
| `source` | String | Data source identifier |
| `connector_version` | String | Connector version |
| `md5` | String | Sample MD5 hash |
| `sha1` | String | Sample SHA1 hash |
| `file_type` | String | File type information |
| `sample_type` | String | Categorized sample type |
| `data_completeness` | Number | Data quality score (0-1) |
| `raw_response` | Object | Original API response |

### Indexes

- `sha256`: Unique index for deduplication
- `ingestion_timestamp`: For time-based queries
- `sample_type`: For filtering by sample type

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest test_connector.py -v

# Run with coverage
python -m pytest test_connector.py --cov=etl_connector

# Run specific test
python -m pytest test_connector.py::test_extract_sample_list -v
```

## 📝 Logging

The connector provides comprehensive logging:

- **Console Output**: Real-time progress information
- **Log File**: `etl_connector.log` with detailed information
- **Log Levels**: INFO, WARNING, ERROR, DEBUG

### Sample Log Output

```
2024-01-15 10:30:00,123 - etl_connector - INFO - MalShare ETL Connector initialized successfully
2024-01-15 10:30:01,456 - etl_connector - INFO - Starting MalShare ETL pipeline
2024-01-15 10:30:02,789 - etl_connector - INFO - === EXTRACT PHASE ===
2024-01-15 10:30:03,012 - etl_connector - INFO - Extracted 25 sample hashes
```

## 🛡️ Error Handling

The connector implements robust error handling for:

- **Network Issues**: Retry logic with exponential backoff
- **Rate Limiting**: Automatic delays and retry
- **Authentication Errors**: Clear error messages
- **Data Validation**: Comprehensive input validation
- **Database Errors**: Connection and insertion error handling

## 🔒 Security Best Practices

- **Environment Variables**: All credentials stored in `.env`
- **Input Validation**: All API inputs validated
- **Error Handling**: No sensitive data in error messages
- **Logging**: Sensitive information filtered from logs

## 📈 Performance Considerations

- **Rate Limiting**: Configurable delays between requests
- **Batch Processing**: Efficient data processing
- **Database Optimization**: Proper indexing strategy
- **Memory Management**: Efficient data handling

## 🐛 Troubleshooting

### Common Issues

1. **API Key Invalid**
   ```
   Error: Authentication failed
   Solution: Verify MALSHARE_API_KEY in .env file
   ```

2. **MongoDB Connection Failed**
   ```
   Error: Failed to connect to MongoDB
   Solution: Check MONGODB_URI and ensure MongoDB is running
   ```

3. **Rate Limited**
   ```
   Warning: Rate limited. Waiting X seconds...
   Solution: Increase RATE_LIMIT_DELAY in .env file
   ```

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python etl_connector.py
```

## 🔄 Continuous Integration

The project includes:
- Automated testing with pytest
- Code quality checks with flake8
- Type checking with mypy
- Code formatting with black

## 📚 Additional Resources

- [MalShare API Documentation](https://malshare.com/doc.php)
- [MongoDB Python Driver Documentation](https://pymongo.readthedocs.io/)
- [Python Requests Documentation](https://docs.python-requests.org/)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is part of the SSN CSE Software Architecture course and is intended for educational purposes.

## 👥 Support

For questions or issues:
- Create an issue in the repository
- Contact: [Your Email]
- Course: Software Architecture - Kyureeus EdTech Program

---

**Note**: Remember to replace placeholder values (API keys, names, etc.) with your actual information before running the connector.