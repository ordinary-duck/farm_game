@echo off
chcp 65001 >nul 2>&1
cls
echo ========================================
echo   Farm Game - Game Start
echo ========================================
echo.
echo Starting game...
echo.

cd /d "%~dp0"
python main.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo Game Error!
    echo ========================================
    echo.
    echo Please check:
    echo 1. Python 3.7+ installed
    echo 2. Dependencies installed: pip install -r requirements.txt
    echo 3. Database config in config.py is correct
    echo 4. SQL Server is running
    echo.
    pause

    
) else (
    echo.
    echo Game closed normally.
    pause
)

