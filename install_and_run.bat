@echo off
echo VisioSense - Hand Gesture Control System
echo ========================================
echo.

echo Installing required libraries...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo Error installing libraries. Please check your Python installation.
    pause
    exit /b 1
)

echo.
echo Installation complete! Starting VisioSense...
echo.

python visiosense.py

pause
