@echo off
setlocal
echo ==========================================
echo    Peak Reasoning AI Agent - Startup
echo ==========================================

echo Ensuring dependencies are met...

:: First, install llama-cpp-python using pre-built wheels to avoid "Long Path" errors and C++ build requirements
echo Installing core AI components (this may take a minute)...
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

:: Then install the rest
pip install -r pc_requirements.txt

echo.
echo Launching UI...
python ui/main.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The application failed to start.
    echo Please ensure you have Python 3.10 or newer installed.
)
pause
