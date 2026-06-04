@echo off
title VisioSense Launcher
echo ===================================================
echo   VisioSense - Starting Python Backend Server...
echo ===================================================
echo.

:: Launch the default web browser to the interface
start "" "http://localhost:5001"

:: Start the Python backend using the virtual environment
.venv\Scripts\python.exe app.py

pause
