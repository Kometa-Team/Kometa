#!/bin/bash

# Test runner script for Kometa
# Usage: ./run_tests.sh [options]

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Running Kometa Tests${NC}"
echo "======================================"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Install it with: pip install pytest pytest-cov pytest-mock"
    exit 1
fi

# Parse arguments
COVERAGE=false
VERBOSE=false
SPECIFIC_TEST=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -t|--test)
            SPECIFIC_TEST="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: ./run_tests.sh [options]"
            echo ""
            echo "Options:"
            echo "  -c, --coverage    Run with coverage report"
            echo "  -v, --verbose     Run with verbose output"
            echo "  -t, --test FILE   Run specific test file"
            echo "  -h, --help        Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Build pytest command
CMD="pytest"

if [ "$VERBOSE" = true ]; then
    CMD="$CMD -v"
fi

if [ "$COVERAGE" = true ]; then
    CMD="$CMD --cov=modules --cov-report=term --cov-report=html"
fi

if [ -n "$SPECIFIC_TEST" ]; then
    CMD="$CMD $SPECIFIC_TEST"
else
    CMD="$CMD tests/"
fi

# Run tests
echo -e "${YELLOW}Executing: $CMD${NC}"
echo ""

$CMD

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ All tests passed!${NC}"
    
    if [ "$COVERAGE" = true ]; then
        echo -e "${YELLOW}Coverage report generated in htmlcov/index.html${NC}"
    fi
else
    echo ""
    echo -e "${RED}✗ Tests failed${NC}"
    exit 1
fi
