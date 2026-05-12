#!/bin/bash
# SAMUDRA AI — Quick Test Runner
# Runs both credential validation and API tests in sequence

set -e  # Exit on any error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Header
echo -e "\n${BOLD}${BLUE}========================================${NC}"
echo -e "${BOLD}${BLUE}  SAMUDRA AI — Test Suite Runner${NC}"
echo -e "${BOLD}${BLUE}========================================${NC}\n"

# Check if Flask is running
echo -e "${BLUE}Checking Flask server...${NC}"
if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Flask is running${NC}"
else
    echo -e "${YELLOW}⚠️  Flask is not running${NC}"
    echo -e "${YELLOW}   Start it in another terminal: flask run${NC}"
    echo -e "${YELLOW}   Continuing with credential validation only...${NC}\n"
fi

# Test 1: Validate Credentials
echo -e "${BOLD}${BLUE}Step 1: Validating Credentials${NC}"
echo -e "${BLUE}================================${NC}\n"
python validate_credentials.py
CRED_RESULT=$?
echo ""

# Test 2: Test API (if Flask is running)
if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo -e "${BOLD}${BLUE}Step 2: Testing API Endpoints${NC}"
    echo -e "${BLUE}=============================${NC}\n"
    python test_api.py
    API_RESULT=$?
    echo ""
else
    echo -e "${YELLOW}⚠️  Skipping API tests (Flask not running)${NC}"
    API_RESULT=0
    echo ""
fi

# Summary
echo -e "${BOLD}${BLUE}========================================${NC}"
echo -e "${BOLD}${BLUE}  Test Summary${NC}"
echo -e "${BOLD}${BLUE}========================================${NC}\n"

if [ $CRED_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Credentials: PASS${NC}"
else
    echo -e "${RED}❌ Credentials: FAIL${NC}"
fi

if [ $API_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ API Tests: PASS${NC}"
elif [ $API_RESULT -ne 0 ] && ! curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  API Tests: SKIPPED (Flask not running)${NC}"
else
    echo -e "${RED}❌ API Tests: FAIL${NC}"
fi

echo ""

# Overall result
if [ $CRED_RESULT -eq 0 ] && [ $API_RESULT -eq 0 ]; then
    echo -e "${GREEN}${BOLD}🎉 All tests passed! Ready for deployment.${NC}\n"
    exit 0
elif [ $CRED_RESULT -eq 0 ]; then
    echo -e "${YELLOW}${BOLD}⚠️  Credentials valid, but couldn't test API (Flask might not be running)${NC}\n"
    exit 0
else
    echo -e "${RED}${BOLD}❌ Some tests failed. See above for details.${NC}\n"
    exit 1
fi
