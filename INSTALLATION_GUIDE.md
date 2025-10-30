# VisioSense Installation Guide

## Quick Installation

### Method 1: Automatic Installation (Recommended)
```bash
python install_dependencies.py
```

### Method 2: Manual Installation
```bash
pip install -r requirements.txt
```

### Method 3: Windows Batch File
Double-click `install_libraries.bat`

## Troubleshooting

### SpeechRecognition Module Error
If you get "no module named 'speech_recognition'" error:

1. **Install SpeechRecognition:**
   ```bash
   pip install SpeechRecognition
   ```

2. **Install PyAudio (Windows):**
   ```bash
   pip install PyAudio
   ```
   
   If PyAudio fails to install on Windows:
   - Download PyAudio wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
   - Install with: `pip install PyAudio-0.2.11-cp311-cp311-win_amd64.whl`

### Common Issues

1. **Camera not found:**
   - Ensure webcam is connected and not used by other applications
   - Check camera permissions

2. **PyAudio installation fails:**
   - This is common on Windows
   - Voice commands will be disabled but other features work
   - Use the manual PyAudio installation method above

3. **Permission errors:**
   - Run as administrator
   - Check Python and pip permissions

## Testing Installation
```bash
python test_installation.py
```

## Running VisioSense
```bash
python visiosense.py
```

## Features Available
- ✅ Hand gesture recognition
- ✅ Facial expression detection
- ✅ Cheating detection
- ✅ Finger counting
- ✅ Voice commands (if SpeechRecognition and PyAudio installed)

## Voice Commands (Optional)
- "open YouTube"
- "open Google"
- "open WhatsApp"
- "open Facebook"
- "open Instagram"
