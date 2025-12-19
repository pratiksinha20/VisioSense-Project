# VisioSense - Complete Setup

## ✅ Features Integrated

- ✓ Hand Gesture Recognition (MediaPipe)
- ✓ Facial Expression Detection (MediaPipe)
- ✓ Object Detection (YOLOv8)
- ✓ Beautiful Web UI
- ✓ Single Camera (No conflicts)

---

## 🚀 How to Run

### Step 1: Install Dependencies (First Time Only)

```powershell
pip install -r requirements.txt
pip install ultralytics
```

### Step 2: Run the App

```powershell
python app.py
```

### Step 3: Open in Browser

Open your web browser and go to:
```
http://localhost:5001
```

---

## 📱 Using the Web Interface

1. **Click START** - Activates camera and all detection features
2. **View Live Stream** - See your camera feed with:
   - Object detection boxes (green boxes around detected objects)
   - Hand gestures displayed
   - Facial expressions shown

3. **Settings Panel** (Right side):
   - Toggle **Object Detection** on/off
   - View detected objects in real-time
   - Adjust gesture sensitivity and smoothing
   - Enable/disable drawing mode

4. **Click STOP** - Stops all detection and releases camera

---

## 🎯 What Gets Detected

### Objects (YOLOv8)
- Pen, Bottle, Remote, Mobile/Phone
- Cup, Laptop, Mouse, Keyboard
- Person, Dog, Cat, Car, and 80+ more

### Gestures (Hand Detection)
- Fist, Open Hand, Peace Sign
- Pinch, Index Pointing, Scroll

### Facial Expressions
- Smile, Serious, Neutral
- Head Pose/Angle

---

## 🔧 Troubleshooting

### Camera Not Opening
- Check if another app is using camera
- Try unplugging and replugging camera

### Slow Performance
- Close other apps
- Disable Object Detection temporarily (uncheck in Settings)
- Use smaller window size

### Models Not Loading
- First run will download YOLOv8 (~6MB) - normal, just wait
- Check internet connection

---

## 📝 File Structure

```
Python Project/
├── app.py                  ← Main file (Run this!)
├── visiosense.py          ← Hand gesture detection
├── requirements.txt       ← Dependencies
├── QUICK_START.md         ← This file
└── templates/
    └── index.html         ← Web UI
```

---

## 💡 Tips

- **First Run**: YOLOv8 model downloads ~6MB (automatic)
- **Performance**: Use `yolov8n` (nano) for fast detection
- **Multiple Features**: All run on single camera without conflicts
- **Browser**: Works on any modern browser (Chrome, Firefox, Edge)

---

**Enjoy your VisioSense experience!** 🎉
