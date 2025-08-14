# NVD CVE ETL Data Connector

A robust Python ETL (Extract, Transform, Load) pipeline for extracting Common Vulnerabilities and Exposures (CVE) data from the National Vulnerability Database (NVD) API and storing it in MongoDB.

## 🎯 Project Overview

This ETL connector fetches CVE vulnerability data from the NVD API, transforms it for MongoDB compatibility, and loads it into a MongoDB collection with proper deduplication and metadata tracking.

## 🏗️ Architecture

The project follows a modular ETL architecture:

- **Extract**: Connects to NVD API and retrieves CVE data
- **Transform**: Sanitizes data for MongoDB compatibility and adds metadata
- **Load**: Stores data in MongoDB with upsert operations for deduplication

## 📋 Features

- ✅ **Robust Error Handling**: Retry logic with exponential backoff for API failures
- ✅ **Rate Limiting**: Automatic handling of NVD API rate limits
- ✅ **Data Deduplication**: Uses hash-based keys to prevent duplicate entries
- ✅ **MongoDB Sanitization**: Automatically sanitizes field names for MongoDB compatibility
- ✅ **Metadata Tracking**: Tracks ingestion timestamps and source information
- ✅ **Environment Configuration**: Secure credential management via environment variables
- ✅ **Type Safety**: Full type hints for better code maintainability

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MongoDB instance
- NVD API access (optional API key for higher rate limits)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd custom-python-etl-data-connector-PaulAndrew7
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp ENV_TEMPLATE .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   # MongoDB settings
   MONGODB_URI=mongodb://localhost:27017/
   MONGODB_DB=vulnerability_db
   MONGODB_COLLECTION=nvd_cve_raw

   # NVD API settings
   API_BASE_URL=https://services.nvd.nist.gov/rest/json/cves/2.0
   API_KEY=your_api_key_here  # Optional
   RESULTS_PER_PAGE=10
   START_INDEX=0
   ```

4. **Run the ETL pipeline**
   ```bash
   python etl_connector.py
   ```

## 📊 Data Structure

### Extracted CVE Data Fields

The connector extracts the following fields from each CVE:

- `id`: CVE identifier (e.g., "CVE-2023-1234")
- `sourceIdentifier`: Source of the vulnerability report
- `published`: Publication date
- `lastModified`: Last modification date
- `descriptions`: Array of vulnerability descriptions
- `metrics`: CVSS scores and metrics
- `weaknesses`: CWE identifiers and descriptions
- `configurations`: Affected software configurations
- `references`: External references and links

### MongoDB Document Structure

Each document includes:

```json
{
  "_id": "ObjectId",
  "id": "CVE-2023-1234",
  "sourceIdentifier": "example@example.com",
  "published": "2023-01-01T00:00:00.000Z",
  "lastModified": "2023-01-02T00:00:00.000Z",
  "descriptions": [...],
  "metrics": {...},
  "weaknesses": [...],
  "configurations": [...],
  "references": [...],
  "_metadata": {
    "ingested_at": "2023-12-01T10:30:00.000Z",
    "source": "nvd_cve_2_0"
  },
  "hash_key": "sha256_hash_of_document"
}
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MONGODB_URI` | MongoDB connection string | - | Yes |
| `MONGODB_DB` | Target database name | - | Yes |
| `MONGODB_COLLECTION` | Target collection name | - | Yes |
| `API_BASE_URL` | NVD API base URL | - | Yes |
| `API_KEY` | NVD API key (optional) | - | No |
| `RESULTS_PER_PAGE` | Number of results per API call | 10 | No |
| `START_INDEX` | Starting index for pagination | 0 | No |

### API Configuration

- **Base URL**: `https://services.nvd.nist.gov/rest/json/cves/2.0`
- **Authentication**: Optional API key for higher rate limits
- **Rate Limits**: 5 requests per 30 seconds without API key, 50 requests per 30 seconds with API key

## 🛡️ Error Handling & Resilience

### Retry Logic

The connector implements robust retry logic with:
- **Exponential backoff**: 1s to 30s delays between retries
- **Maximum attempts**: 5 retry attempts
- **Rate limit handling**: Automatic sleep on 429 responses
- **Network error recovery**: Handles connection timeouts and network issues

### Data Validation

- **JSON validation**: Ensures API responses are valid JSON
- **Field validation**: Checks for required fields in API responses
- **MongoDB sanitization**: Automatically sanitizes field names and values

## 📈 Performance Considerations

### Optimization Features

- **Bulk operations**: Uses MongoDB bulk write operations for efficiency
- **Upsert strategy**: Prevents duplicate data insertion
- **Hash-based deduplication**: Uses SHA256 hashes for reliable duplicate detection
- **Connection pooling**: Reuses HTTP connections for API calls



### Validation Checklist

- [✅] API credentials are valid
- [✅] MongoDB connection is successful
- [✅] Data extraction works without errors
- [✅] Data transformation preserves all fields
- [✅] MongoDB insertion completes successfully
- [✅] No duplicate data is inserted
- [✅] Metadata is properly attached



## 📚 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pymongo` | ≥4.7.0 | MongoDB driver |
| `python-dotenv` | ≥1.0.1 | Environment variable management |
| `requests` | ≥2.32.0 | HTTP client for API calls |
| `pydantic` | ≥2.8.2 | Data validation (future use) |
| `tenacity` | ≥9.0.0 | Retry logic implementation |


## 👨‍💻 Author

**Paul Andrew** - Custom Python ETL Data Connector Implementation

---

