# VisioSense Setup Guide

## Quick Start (Windows)

### Method 1: Automatic Installation
1. Double-click `install_and_run.bat`
2. The script will automatically install all required libraries
3. VisioSense will start automatically

### Method 2: Manual Installation
1. Open Command Prompt or PowerShell
2. Navigate to the project folder
3. Run: `pip install -r requirements.txt`
4. Run: `python visiosense.py`

## Testing Installation
Run the test script to verify everything is working:
```bash
python test_installation.py
```

## Troubleshooting

### Camera Issues
- **Camera not found**: Make sure your webcam is connected and not used by other applications
- **Permission denied**: Run as administrator or check camera permissions
- **Poor detection**: Ensure good lighting and clean background

### Library Issues
- **Import errors**: Make sure you're using Python 3.8 or higher
- **Installation fails**: Try upgrading pip: `python -m pip install --upgrade pip`
- **Version conflicts**: Create a virtual environment: `python -m venv visiosense_env`

### Performance Issues
- **Laggy cursor movement**: Close other applications using the camera
- **Gesture detection issues**: Ensure good lighting and make gestures clearly
- **High CPU usage**: Reduce camera resolution in the code if needed

## Gesture Reference

| Gesture | Action |
|---------|--------|
| Fist | Enter Mouse Mode |
| Open Hand | Exit Mouse Mode / Clear Canvas |
| Pinch | Click (hold for drag) |
| Long Pinch (>0.6s) | Drag & Drop |
| Two-Finger Scroll | Scroll up/down |
| Index Pointing | Draw on screen |
| Namaskar (both hands close) | Exit program |

## System Requirements
- Windows 10/11
- Python 3.8+
- Webcam
- 4GB+ RAM recommended
- Good lighting for gesture recognition
