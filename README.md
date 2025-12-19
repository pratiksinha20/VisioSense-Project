# VisioSense – Hand Gesture Control System

VisioSense is a real-time computer vision system that uses **hand gestures, facial expressions, and object detection** to control and interact with a computer using a webcam.  
The project combines **MediaPipe**, **OpenCV**, and **YOLOv8 (pre-trained model with TensorFlow support)** for intelligent, hands-free interaction.

---

## Quick Setup

1. **Install Python 3.8+** (if not already installed)

2. **Install required libraries:**
```bash
pip install -r requirements.txt
Run the application:
python visiosense.py


## Features

### Gesture Control (via MediaPipe Hands)

- **Fist** → Enter Mouse Mode  
- **Open Hand** → Exit Mouse Mode  
- **Pinch (thumb + index)** → Single click on release  
- **Long Pinch (>0.6s)** → Drag & Drop  
- **Two-Finger Scroll (index + middle)** → Scroll up/down  
- **Index Pointing** → Draw on screen (Whiteboard mode)  
- **Open Hand (in standard mode)** → Clear canvas  
- **Namaskar (2 hands close)** → Exit program  



### Mouse Mode
- Cursor moves smoothly using **index finger**.
- **Click, drag, and scroll** operations are handled **only in mouse mode**.
- Prevents accidental clicks while drawing.

### Virtual Whiteboard
- Draw directly on screen using **index finger**.
- Clear canvas using **open-hand gesture**.
- Ideal for **demos and presentations**.

### Object Detection (YOLOv8 + TensorFlow)
- Real-time object detection using **YOLOv8 pre-trained model**.
- Integrated with **live webcam feed**.
- Detects common real-world objects.
- Runs simultaneously with **hand gesture recognition**.
- Uses **TensorFlow-based deep learning inference**.

---

## Technology Stack
- **MediaPipe Hands** – Hand gesture recognition
- **OpenCV** – Webcam feed handling and image processing
- **YOLOv8** – Object detection
- **TensorFlow** – Deep learning inference
- **Python** – Core programming language

---

## Usage
1. Run the main Python script:
   ```bash
   python main.py

# Gesture & Object Detection System – Extended Features

This project combines **hand gesture recognition** and **real-time object detection**, providing smooth interaction with your computer through gestures and intelligent detection of objects in your environment.

---

## Stability Features
- Uses **deque-based history** to stabilize gestures.
- **Smooth cursor movement** using interpolation.
- **Click debounce** to prevent accidental clicks (minimum 0.3s interval).

---

## Error Handling
- Displays a **friendly message** if the camera is not detected.
- Press **Q** or **ESC** to exit the application safely.

---

## Usage
1. Start the application.
2. Make a **Fist** to enter **Mouse Mode**.
3. Use **Pinch gestures** to click and drag.
4. Use **Two-Finger Scroll** for scrolling.
5. Make **Open Hand** to exit Mouse Mode and enter drawing mode.
6. Use **Index Pointing** to draw on the screen.
7. Make **Namaskar gesture** to exit the program.

---

## Tech Stack
- **Python**
- **OpenCV**
- **MediaPipe**
- **TensorFlow**
- **YOLOv8 (Pre-trained Model)**
- **NumPy**
- **PyAutoGUI**

---

## Requirements
- **Windows 10 / 11**
- **Webcam**
- **Python 3.8+**
- Required libraries (see `requirements.txt`)

---

## Troubleshooting
- Ensure **webcam is connected** and not used by other applications.
- Use **proper lighting** for accurate gesture detection.
- Adjust **detection thresholds** if required.

---

## Future Enhancements
- **Smart glove–based sign language translation**
- **Voice feedback** for gestures
- **Custom gesture configuration**
- **Mobile and IoT integration**

---

## Author
**Pratik Kumar Sinha**  
B.E. Computer Science & Engineering

---

## Demo Video
(https://www.linkedin.com/in/pratik-kumar-sinha-9305a0334/)

