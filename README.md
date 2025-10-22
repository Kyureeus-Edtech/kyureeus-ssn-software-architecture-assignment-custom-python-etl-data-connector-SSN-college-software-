### CIRCL Passive DNS ETL Connector (Python → CIRCL API → MongoDB)

A production-grade ETL connector that queries the CIRCL Passive DNS API, transforms DNS records by adding metadata and classifications, and loads them into MongoDB. This connector demonstrates how to work with NDJSON responses and handle DNS-specific data structures.

### Quickstart (Windows PowerShell)

- Create and activate a virtual environment
```powershell
py -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

- Install dependencies
```powershell
pip install -r requirements.txt
```

- Configure environment
  - Copy `env_example.txt` to `.env` and modify as needed
  - The connector is pre-configured for CIRCL Passive DNS API

- Run the connector
```powershell
python etl_connector.py
```

### Configuration (.env)

The connector uses environment variables for configuration. Example `.env`:

```ini
# CIRCL Passive DNS API Configuration
API_BASE_URL=https://www.circl.lu/pdns/query
API_ENDPOINTS=circl.lu,8.8.8.8,example.com

# Authentication (CIRCL API doesn't require auth for public queries)
API_KEY=
API_AUTH_HEADER=
API_AUTH_PREFIX=

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017
MONGO_DB=etl2
MONGO_COLLECTION=datalist
```

### Three Endpoint Examples

The connector demonstrates three different types of DNS queries:

1. **Domain Query**: `circl.lu` - Retrieves all DNS records associated with the circl.lu domain
2. **IP Query**: `8.8.8.8` - Performs reverse DNS lookup for Google's public DNS server
3. **Another Domain**: `example.com` - Queries DNS records for example.com

### Data Transformation

The connector enriches DNS records with:

- **ETL Metadata**: `ingested_at`, `query_value`, `source_api`
- **Time Conversion**: Converts Unix timestamps to datetime objects (`time_first_datetime`, `time_last_datetime`)
- **Record Classification**: Categorizes DNS record types (`basic`, `security`, `other`)
- **Query Classification**: Identifies query type (`domain`, `ipv4`, `ipv6`, `unknown`)

### MongoDB Storage

- **Database**: `etl2` (configurable via `MONGO_DB`)
- **Collection**: `datalist` (configurable via `MONGO_COLLECTION`)
- **Documents**: Each DNS record is stored as a separate document with enriched metadata

### API Response Handling

The connector handles CIRCL's NDJSON (Newline Delimited JSON) response format:

```json
{"rrtype": "A", "rrname": "185.194.93.14", "rdata": "circl.lu", "count": "19", "time_first": "1696798385", "time_last": "1697890824"}
{"rrtype": "AAAA", "rrname": "2a00:5980:93::14", "rdata": "circl.lu", "count": "18", "time_first": "1696798385", "time_last": "1697890824"}
```

### Error Handling

- **Rate Limiting**: Handles 429 responses with retry logic
- **NDJSON Parsing**: Gracefully handles malformed JSON lines
- **API Errors**: Captures and logs CIRCL-specific error headers (`x-dribble-errors`)
- **Pagination**: Supports CIRCL's pagination headers (`x-dribble-cursor`)

### Debug Output

- **Log File**: `etl_connector.log` with detailed processing information
- **JSON Files**: Individual files in `etl_output/` directory for each query
- **MongoDB**: All records stored with full metadata for analysis

### Testing & Validation

- ✅ Handles NDJSON responses from CIRCL API
- ✅ Transforms DNS records with proper metadata
- ✅ Classifies record types and query types
- ✅ Stores enriched data in MongoDB
- ✅ Provides comprehensive logging and debug output
- ✅ Handles API errors and rate limiting gracefully

### Use Cases

This connector is ideal for:

- **Security Research**: Analyzing DNS patterns and historical data
- **Threat Intelligence**: Tracking domain and IP associations
- **DNS Forensics**: Investigating suspicious domains or IPs
- **Data Science**: Building datasets for DNS analysis

### Notes

- The CIRCL Passive DNS API is free for public use and doesn't require authentication
- Access to the full API may require registration for higher volume usage
- The connector demonstrates best practices for working with NDJSON APIs
- All timestamps are converted to UTC for consistency
