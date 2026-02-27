@echo off
setlocal EnableDelayedExpansion

:: ============================================================
::  SQLBridgeMCP - Setup Script Template
::
::  HOW TO USE:
::    1. Copy this file and rename it to: setup_mcp.bat
::    2. Fill in your database credentials in the section below
::    3. Double-click setup_mcp.bat (or run it from a terminal)
::    4. Restart Claude Code completely
::
::  NOTE: setup_mcp.bat is in .gitignore so your real credentials
::        will never be committed to the repository.
:: ============================================================

:: Auto-detect project root (works from any folder on any machine)
set "PROJECT_DIR=%~dp0"
if "%PROJECT_DIR:~-1%"=="\" set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

set "PYTHON_EXE=%PROJECT_DIR%\venv\Scripts\python.exe"
set "MAIN_PY=%PROJECT_DIR%\main.py"

echo.
echo  SQLBridgeMCP Setup
echo  ==================
echo  Project dir : %PROJECT_DIR%
echo  Python      : %PYTHON_EXE%
echo  Main script : %MAIN_PY%
echo.

:: ============================================================
::  STEP 1: Verify Python is installed
:: ============================================================

python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found in PATH.
    echo Download it from: https://www.python.org/downloads/
    pause & exit /b 1
)

:: ============================================================
::  STEP 2: Create venv if it doesn't exist
:: ============================================================

if not exist "%PYTHON_EXE%" (
    echo [INFO] Creating virtual environment...
    python -m venv "%PROJECT_DIR%\venv"
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create venv.
        pause & exit /b 1
    )
    echo [OK] Venv created.
    echo.
)

:: ============================================================
::  STEP 3: Install dependencies
:: ============================================================

echo [INFO] Installing dependencies...
"%PYTHON_EXE%" -m pip install -r "%PROJECT_DIR%\requirements.txt" --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] pip install failed. Check requirements.txt.
    pause & exit /b 1
)
echo [OK] Dependencies installed.
echo.

:: ============================================================
::  STEP 4: Verify main.py exists
:: ============================================================

if not exist "%MAIN_PY%" (
    echo [ERROR] main.py not found at: %MAIN_PY%
    pause & exit /b 1
)

:: ============================================================
::  STEP 5: Fill in your database credentials below
:: ============================================================

set "DB_TYPE=sqlserver"
set "DB_HOST=your-server.database.windows.net"
set "DB_PORT=1433"
set "DB_NAME=your-database-name"
set "DB_USER=your-username"
set "DB_PASSWORD=your-password"

:: ============================================================

echo [INFO] Registering MCP server in Claude Code...
echo.

claude mcp add sql-bridge "%PYTHON_EXE%" "%MAIN_PY%" -s user ^
  -e DB_TYPE=%DB_TYPE% ^
  -e DB_HOST=%DB_HOST% ^
  -e DB_PORT=%DB_PORT% ^
  -e DB_NAME=%DB_NAME% ^
  -e DB_USER=%DB_USER% ^
  -e DB_PASSWORD=%DB_PASSWORD%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] MCP server registered successfully!
    echo.
    echo Next steps:
    echo   1. Restart Claude Code completely ^(close and reopen^)
    echo   2. Look for the MCP plug icon in Claude Code
    echo   3. Test it by asking: "What MCP tools are available?"
) else (
    echo.
    echo [ERROR] Registration failed.
    echo.
    echo Possible causes:
    echo   - 'claude' CLI is not installed or not in PATH
    echo   - Download Claude Code from: https://claude.ai/download
)

echo.
pause
