#!/bin/bash

# CERT.at Threat Intelligence Pipeline Runner
# Convenience script for running the ETL pipeline

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Parse arguments
CSV_ONLY=false
RSS_ONLY=false
HELP=false

for arg in "$@"
do
    case $arg in
        --csv-only)
            CSV_ONLY=true
            shift
            ;;
        --rss-only)
            RSS_ONLY=true
            shift
            ;;
        --help|-h)
            HELP=true
            shift
            ;;
        *)
            ;;
    esac
done

# Show help
if [ "$HELP" = true ]; then
    echo "CERT.at Threat Intelligence Pipeline Runner"
    echo
    echo "Usage: ./run.sh [OPTIONS]"
    echo
    echo "Options:"
    echo "  --csv-only    Run only the CSV threat intelligence pipeline"
    echo "  --rss-only    Run only the RSS security feeds pipeline"
    echo "  --help, -h    Show this help message"
    echo
    echo "Examples:"
    echo "  ./run.sh                 # Run both pipelines"
    echo "  ./run.sh --csv-only      # Run only CSV pipeline"
    echo "  ./run.sh --rss-only      # Run only RSS pipeline"
    echo
    exit 0
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}✗ Error: .env file not found${NC}"
    echo "Please run setup.sh first or copy .env.template to .env"
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Error: Virtual environment not found${NC}"
    echo "Please run setup.sh first"
    exit 1
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Modify .env based on flags
if [ "$CSV_ONLY" = true ]; then
    echo -e "${YELLOW}Running CSV pipeline only${NC}"
    export RUN_CSV_PIPELINE=true
    export RUN_RSS_PIPELINE=false
elif [ "$RSS_ONLY" = true ]; then
    echo -e "${YELLOW}Running RSS pipeline only${NC}"
    export RUN_CSV_PIPELINE=false
    export RUN_RSS_PIPELINE=true
else
    echo -e "${GREEN}Running both CSV and RSS pipelines${NC}"
fi

echo
echo "=============================================================================="
echo "  Starting CERT.at Threat Intelligence Pipeline"
echo "=============================================================================="
echo

# Run the pipeline
python threat_intel_pipeline/etl_orchestrator.py

# Check exit code
EXIT_CODE=$?

echo
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}=============================================================================="
    echo -e "  Pipeline Completed Successfully!"
    echo -e "==============================================================================${NC}"
else
    echo -e "${RED}=============================================================================="
    echo -e "  Pipeline Failed (Exit Code: $EXIT_CODE)"
    echo -e "  Check the logs in logs/ directory for details"
    echo -e "==============================================================================${NC}"
fi

exit $EXIT_CODE