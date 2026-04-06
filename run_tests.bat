@echo off
REM SAMUDRA AI — Quick Test Runner for Windows
REM Runs both credential validation and API tests in sequence

setlocal enabledelayedexpansion

REM Colors (Windows 10+)
for /F %%A in ('echo prompt $H ^| cmd') do set "BS=%%A"

echo.
echo ========================================
echo   SAMUDRA AI — Test Suite Runner
echo ========================================
echo.

REM Check if Flask is running
echo Checking Flask server...
curl -s http://localhost:5000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Flask is running
) else (
    echo [WARNING] Flask is not running
    echo   Start it in another terminal: flask run
    echo   Continuing with credential validation only...
    echo.
)

REM Test 1: Validate Credentials
echo.
echo Step 1: Validating Credentials
echo ================================
echo.
python validate_credentials.py
set CRED_RESULT=%errorlevel%
echo.

REM Test 2: Test API (if Flask is running)
curl -s http://localhost:5000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo Step 2: Testing API Endpoints
    echo =============================
    echo.
    python test_api.py
    set API_RESULT=%errorlevel%
) else (
    echo [WARNING] Skipping API tests (Flask not running)
    set API_RESULT=0
)
echo.

REM Summary
echo.
echo ========================================
echo   Test Summary
echo ========================================
echo.

if %CRED_RESULT% equ 0 (
    echo [OK] Credentials: PASS
) else (
    echo [FAIL] Credentials: FAIL
)

if %API_RESULT% equ 0 (
    echo [OK] API Tests: PASS
) else (
    curl -s http://localhost:5000/api/health >nul 2>&1
    if !errorlevel! neq 0 (
        echo [WARNING] API Tests: SKIPPED (Flask not running)
    ) else (
        echo [FAIL] API Tests: FAIL
    )
)

echo.

REM Overall result
if %CRED_RESULT% equ 0 (
    if %API_RESULT% equ 0 (
        echo All tests passed! Ready for deployment.
        exit /b 0
    ) else (
        echo Credentials valid, but couldn't test API (Flask might not be running)
        exit /b 0
    )
) else (
    echo Some tests failed. See above for details.
    exit /b 1
)
