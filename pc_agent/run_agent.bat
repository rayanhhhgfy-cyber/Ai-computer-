@echo off
setlocal enabledelayedexpansion
:: Change directory to the script's location
cd /d "%~dp0"

echo ==========================================
echo    Peak Reasoning AI Agent - Startup
echo ==========================================

:: 1. Find Python
set PY_CMD=
for %%P in (python, py, python3) do (
    where %%P >nul 2>&1
    if !errorlevel! equ 0 (
        set PY_CMD=%%P
        goto :found_python
    )
)

:found_python
if "!PY_CMD!"=="" (
    echo [!] Python not found. Attempting to install Python 3.12 via winget...
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    if !errorlevel! neq 0 (
        echo [!] Automatic installation failed. Please install Python 3.12 from python.org
        pause
        exit /b 1
    )
    set PY_CMD=python
)

echo Using: !PY_CMD!
!PY_CMD! --version

:: 2. Upgrade pip
echo Upgrading pip...
!PY_CMD! -m pip install --upgrade pip

:: 3. Install dependencies
echo Installing dependencies...
:: Use --only-binary to avoid building from source where possible
!PY_CMD! -m pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu --only-binary=:all:
!PY_CMD! -m pip install -r pc_requirements.txt

:: 4. Launch Application
echo.
echo Launching UI...
!PY_CMD! ui/main.py
if !errorlevel! neq 0 (
    echo.
    echo [!] The application crashed.
    echo If you see 'ModuleNotFoundError', try running this script as Administrator.
    pause
)
pause
