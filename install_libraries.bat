@echo off
echo VisioSense - Library Installation Script
echo ========================================
echo.

echo Installing core libraries...
pip install opencv-python==4.12.0.88
pip install mediapipe==0.10.14
pip install numpy==2.2.6
pip install pyautogui==0.9.54
pip install scipy==1.16.2

echo.
echo Installing voice recognition libraries...
pip install SpeechRecognition==3.10.0

echo.
echo Installing PyAudio (this may require additional setup)...
pip install PyAudio==0.2.11

if %errorlevel% neq 0 (
    echo.
    echo PyAudio installation failed. This is common on Windows.
    echo Please install PyAudio manually:
    echo 1. Download PyAudio wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
    echo 2. Install with: pip install PyAudio-0.2.11-cp311-cp311-win_amd64.whl
    echo.
    echo Voice commands will be disabled until PyAudio is installed.
)

echo.
echo Installation complete!
echo.
echo Testing installation...
python test_installation.py

echo.
echo Starting VisioSense...
python visiosense.py

pause
