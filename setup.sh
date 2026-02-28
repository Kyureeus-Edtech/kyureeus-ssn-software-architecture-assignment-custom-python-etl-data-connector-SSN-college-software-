#!/bin/bash

# CERT.at Threat Intelligence Pipeline Setup Script
# This script sets up the complete environment

set -e

echo "=============================================================================="
echo "  CERT.at Threat Intelligence Pipeline - Setup Script"
echo "=============================================================================="
echo

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo -e "${RED}✗ Python 3.8 or higher is required (found $PYTHON_VERSION)${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"
echo

# Create virtual environment
echo "Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment already exists, skipping...${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi
echo

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓ pip upgraded${NC}"
echo

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo

# Create directories
echo "Creating required directories..."
mkdir -p data
mkdir -p logs
mkdir -p scripts
echo -e "${GREEN}✓ Directories created${NC}"
echo

# Setup environment file
echo "Setting up environment configuration..."
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env file already exists, skipping...${NC}"
else
    cp .env.template .env
    echo -e "${GREEN}✓ Created .env from template${NC}"
    echo -e "${YELLOW}⚠ Please edit .env file with your MongoDB connection details${NC}"
fi
echo

# Check MongoDB
echo "Checking MongoDB connection..."
if command -v mongosh &> /dev/null; then
    if mongosh --eval "db.runCommand({ ping: 1 })" --quiet > /dev/null 2>&1; then
        echo -e "${GREEN}✓ MongoDB is running and accessible${NC}"
    else
        echo -e "${YELLOW}⚠ MongoDB is not accessible (this is OK if you'll start it later)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ MongoDB shell (mongosh) not found${NC}"
    echo "  Install MongoDB from: https://www.mongodb.com/try/download/community"
    echo "  Or use Docker: docker run -d -p 27017:27017 --name mongodb mongo:latest"
fi
echo

# Generate sample data
echo "Would you like to generate sample CSV data for testing? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Generating sample data..."
    python scripts/generate_sample_data.py
    echo
fi

# Summary
echo "=============================================================================="
echo -e "${GREEN}  Setup Complete!${NC}"
echo "=============================================================================="
echo
echo "Next Steps:"
echo "  1. Edit .env file with your MongoDB connection string"
echo "  2. Start MongoDB if not already running"
echo "  3. Run the pipeline:"
echo "     ./run.sh                          # Run complete pipeline"
echo "     ./run.sh --csv-only              # Run only CSV pipeline"
echo "     ./run.sh --rss-only              # Run only RSS pipeline"
echo
echo "For more information, see README.md"
echo "=============================================================================="