@echo off
REM CI script for Windows
REM Викликається з GitHub Actions workflow

echo === Installing dependencies ===
call npm install
if %ERRORLEVEL% neq 0 (
    echo ERROR: npm install failed
    exit /b %ERRORLEVEL%
)

echo === Running tests ===
call npm test
if %ERRORLEVEL% neq 0 (
    echo ERROR: npm test failed
    exit /b %ERRORLEVEL%
)

echo === CI script completed successfully ===
