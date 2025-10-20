# SSL Labs API ETL Connector

A Python-based ETL (Extract, Transform, Load) tool that analyzes SSL/TLS configurations of domains using the SSL Labs API and stores the results in MongoDB.

## Features

- Fetches SSL/TLS analysis data from SSL Labs API
- Analyzes multiple domains from a text file
- Retrieves detailed endpoint information including grades and server details
- Stores structured analysis results in MongoDB
- Includes retry logic for API requests
- Handles API rate limiting with automatic waiting

## Prerequisites

- Python 3.7+
- MongoDB instance (local or remote)
- SSL Labs API access (free, no API key required)

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd <your-repo-name>
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root according to ENV_TEMPLATE:


## Dependencies

Create a `requirements.txt` file with the following:
```
requests>=2.31.0
pymongo>=4.6.0
python-dotenv>=1.0.0
```

## Usage

1. Create a text file with domains to analyze (one domain per line):
```
example.com
google.com
github.com
```

2. Run the ETL script:
```bash
python etl_connector.py domains.txt
```

## Output

The script will:
1. Display API version information
2. Analyze each domain in the input file
3. Store the following data in MongoDB:
   - Domain name
   - IP address
   - SSL grade (A+, A, B, C, etc.)
   - Status message
   - Server name
   - Detailed endpoint information
   - Timestamp of analysis

## MongoDB Schema

Each document stored in MongoDB has the following structure:
```json
{
  "domain": "example.com",
  "ipAddress": "93.184.216.34",
  "grade": "A+",
  "statusMessage": "Ready",
  "serverName": "example.com",
  "details": {
    // Detailed SSL/TLS configuration data
  },
  "timestamp": "2025-10-20T10:30:00.000Z"
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SSL_LABS_BASE_URL` | SSL Labs API base URL | `https://api.ssllabs.com/api/v3` |
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017/` |
| `MONGO_DB` | Database name | `ssllabs_db` |
| `MONGO_COLLECTION` | Collection name | `ssl_analysis` |

## API Rate Limits

SSL Labs API has the following rate limits:
- Maximum 25 assessments per 24 hours per server
- Maximum 25 concurrent assessments

The script includes a 10-second polling interval to check analysis status and avoid rate limiting issues.

## Error Handling

- Retries failed API requests up to 3 times with 2-second delays
- Handles timeout errors (20-second timeout per request)
- Gracefully handles missing or invalid data
- Provides detailed error messages for debugging

## Example Output

```
Fetching API info...
SSL Labs API version: 2.2.6

Analyzing domain: example.com
Status: IN_PROGRESS... waiting 10s
Status: READY
Fetching endpoint data for example.com - 93.184.216.34
Inserted 1 records into MongoDB.
```

## Troubleshooting

### MongoDB Connection Issues
- Verify MongoDB is running: `mongod --version`
- Check the `MONGO_URI` in your `.env` file
- Ensure network connectivity to MongoDB instance

### API Request Failures
- Check internet connectivity
- Verify SSL Labs API status at https://www.ssllabs.com/
- Ensure the domain format is correct (no http://, https://, or trailing slashes)

### File Not Found
- Verify the path to the domains file is correct
- Use absolute paths if relative paths cause issues

## License

MIT License

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgments

- [SSL Labs API Documentation](https://github.com/ssllabs/ssllabs-scan/blob/master/ssllabs-api-docs-v3.md)
- [Qualys SSL Labs](https://www.ssllabs.com/)

## Support

For issues and questions, please open an issue on GitHub.
