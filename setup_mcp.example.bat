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

:: Verify venv exists
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python venv not found.
    echo.
    echo Please run these commands first:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

:: Verify main.py exists
if not exist "%MAIN_PY%" (
    echo [ERROR] main.py not found at: %MAIN_PY%
    pause
    exit /b 1
)

:: ============================================================
::  STEP 1: Fill in your database credentials below
:: ============================================================

set "DB_TYPE=sqlserver"
set "DB_HOST=your-server.database.windows.net"
set "DB_PORT=1433"
set "DB_NAME=your-database-name"
set "DB_USER=your-username"
set "DB_PASSWORD=your-password"

:: ============================================================

echo Registering MCP server in Claude Code...
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
