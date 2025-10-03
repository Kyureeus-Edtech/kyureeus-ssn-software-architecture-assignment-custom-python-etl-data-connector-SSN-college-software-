# Custom Python ETL Data Connector

## Project Overview

This repository contains a comprehensive ETL (Extract, Transform, Load) data pipeline solution that integrates multiple cybersecurity data sources into MongoDB databases. The project is organized into two main categories, each focusing on different types of security intelligence data collection and storage.

## Repository Structure

```
custom-python-etl-data-connector/
├── Cat1_All_Endpoints/          # Shodan API Integration
│   ├── shodan_connector.py      # Main Shodan ETL connector
│   ├── shodan_README.md         # Shodan-specific documentation
│   └── shodan_requirements.txt  # Shodan dependencies
├── Cat2_All_Endpoints/          # MITRE ATT&CK TAXII Integration
│   ├── MittreTaxiAPI_connector.py  # MITRE TAXII ETL connector
│   ├── MittreTaxi_README.md        # MITRE TAXII documentation
│   └── requirements.txt            # MITRE TAXII dependencies
├── ENV_TEMPLATE                 # Environment variables template
└── README.md                   # This file
```

## Categories Overview

### Cat1_All_Endpoints: Shodan Security Intelligence

Purpose: Collects network security intelligence data from Shodan, the world's first search engine for Internet-connected devices.

Key Features:
- Device Discovery: Searches for IoT devices, servers, and network infrastructure
- Vulnerability Scanning: Identifies exposed services and potential security risks
- Geolocation Data: Maps device locations and network topology
- Service Fingerprinting: Identifies running services, software versions, and configurations
- Rate Limiting: Implements proper API rate limiting to respect Shodan's usage policies

Data Sources:
- Shodan REST API endpoints
- Real-time device scanning results
- Historical vulnerability data
- Network service information

MongoDB Storage: Stores results in configurable databases with timestamped entries for tracking device exposure over time.

### Cat2_All_Endpoints: MITRE ATT&CK Threat Intelligence

Purpose: Extracts structured threat intelligence from the MITRE ATT&CK framework via TAXII 2.1 protocol.

Key Features:
- Attack Patterns: Collects detailed information about adversary tactics and techniques
- Threat Actor Profiles: Gathers intelligence on known threat groups and their methods
- Mitigation Strategies: Provides defensive measures and detection methods
- STIX Object: Processes standardized threat intelligence objects
- Version Tracking: Maintains historical versions of threat intelligence data

Data Sources:
- MITRE ATT&CK TAXII 2.1 API
- Collections, manifests, objects, and versions
- Structured threat intelligence in STIX format
- Real-time updates from MITRE's threat research

MongoDB Storage: Organizes threat intelligence into structured collections with relationship mapping and temporal tracking.

## Unified MongoDB Integration

Both connectors implement a robust MongoDB storage strategy:

### Database Architecture
- Separate Databases: Each connector uses dedicated databases to prevent data conflicts
- Timestamped Records: All entries include ingestion timestamps for audit trails
- Structured Collections: Data is organized into logical collections based on source and type
- Error Handling: Comprehensive error recovery and connection management

## Getting Started

### Prerequisites
- Python 3.7 or higher
- MongoDB (local or remote instance)
- API keys for respective services
- Internet connectivity for API access

### Quick Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd custom-python-etl-data-connector
```

2. Set up environment variables:
```bash
cp ENV_TEMPLATE .env
# Edit .env with your actual API keys and MongoDB settings
```

3. Install dependencies for both categories:
```bash
# For Shodan connector
cd Cat1_All_Endpoints
pip install -r shodan_requirements.txt

# For MITRE TAXII connector
cd ../Cat2_All_Endpoints
pip install -r requirements.txt
```

4. Configure MongoDB:
   - Ensure MongoDB is running on your system
   - Update connection strings in `.env` file
   - Create appropriate databases and collections

### Environment Configuration

The project uses the following environment variables:

#### Cat1 (Shodan) Configuration:
```env
SHODAN_API_KEY=your_shodan_api_key
MONGO_URI=mongodb://localhost:27017
DB_NAME_shodan=securitydb
COLLECTION_NAME_shodan=shodan_results
```

#### Cat2 (MITRE TAXII) Configuration:
```env
MONGO_URI_taxii=mongodb://localhost:27017/taxii_db
TAXII_API="https://attack-taxii.mitre.org/api/v21"
ACCEPT_HEADER="application/taxii+json;version=2.1"
```

## Usage

### Running Individual Connectors

Shodan Connector:
```bash
cd Cat1_All_Endpoints
python shodan_connector.py
```

MITRE TAXII Connector:
```bash
cd Cat2_All_Endpoints
python MittreTaxiAPI_connector.py
```