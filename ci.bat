@echo off
REM CI script for Windows
REM Called from GitHub Actions workflow: install -> build -> run hello -> unit tests

echo === Installing dependencies ===
call npm ci
if %ERRORLEVEL% neq 0 (
    echo ERROR: npm ci failed
    exit /b %ERRORLEVEL%
)

echo === Building executable ===
call npm run build
if %ERRORLEVEL% neq 0 (
    echo ERROR: build failed
    exit /b %ERRORLEVEL%
)

echo === Smoke test: running build\hello\hello.cmd ===
call build\hello\hello.cmd > hello-output.txt
if %ERRORLEVEL% neq 0 (
    echo ERROR: hello executable failed
    exit /b %ERRORLEVEL%
)
set /p HELLO_OUT=<hello-output.txt
echo %HELLO_OUT%
if not "%HELLO_OUT%"=="Hello, World!" (
    echo ERROR: unexpected output from hello executable
    exit /b 1
)
del hello-output.txt

echo === Running unit tests (with coverage) ===
call npm run test:coverage
if %ERRORLEVEL% neq 0 (
    echo ERROR: npm test failed
    exit /b %ERRORLEVEL%
)

echo === CI script completed successfully ===
