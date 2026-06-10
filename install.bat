@echo off
REM install.bat - Install dependencies for free-ai-router

echo ====================================
echo  free-ai-router - Install Dependencies
echo ====================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+ first.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/2] Installing dependencies...
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo [2/2] Setup complete!
echo.
echo Next steps:
echo   1. Copy router_config.example.json to router_config.json
echo   2. Add your API keys (see README.md for details)
echo   3. Run: python smart_router.py --status
echo.
pause
