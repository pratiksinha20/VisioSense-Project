# VisioSense - Hand Gesture Control System

A complete Python project for real-time hand gesture recognition and control using computer vision.

## Quick Setup

1. **Install Python 3.8+** (if not already installed)

2. **Install required libraries:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python visiosense.py
   ```

## Features

### Gesture Control (via MediaPipe Hands)
- **Fist** → Enter Mouse Mode  
- **Open Hand** → Exit Mouse Mode  
- **Pinch (thumb+index)** → Single click on release  
- **Long Pinch (>0.6s)** → Drag & Drop  
- **Two-Finger Scroll (index+middle)** → Scroll up/down  
- **Index Pointing** → Draw on screen (whiteboard mode)  
- **Open Hand (in standard mode)** → Clear canvas  
- **Namaskar (2 hands close)** → Exit program  

### Mouse Mode
- Cursor moves smoothly with index finger
- Click/drag/scroll all handled in mouse mode only
- Prevent accidental clicks while drawing

### Display Features
- Show "Mouse Mode" or "Standard Mode"
- Show gesture name and finger count
- Show colored indicators (drag = red circle)
- Show "Closing..." on Namaskar gesture

### Stability Features
- Use deque history to stabilize gestures
- Use interpolation for smooth cursor movement
- Debounce clicks (0.3s min interval)

### Error Handling
- If camera not found, show friendly message
- Press `q` or `ESC` to exit

## Usage

1. Start the application
2. Make a **Fist** to enter Mouse Mode
3. Use **Pinch** gestures to click and drag
4. Use **Two-Finger Scroll** for scrolling
5. Make **Open Hand** to exit Mouse Mode and enter drawing mode
6. Use **Index Pointing** to draw on screen
7. Make **Namaskar** (bring both hands close together) to exit

## Requirements

- Windows 10/11
- Webcam
- Python 3.8+
- Required libraries (see requirements.txt)

## Troubleshooting

- If camera is not detected, ensure your webcam is connected and not being used by other applications
- Make sure you have proper lighting for gesture recognition
- Adjust gesture detection sensitivity if needed
