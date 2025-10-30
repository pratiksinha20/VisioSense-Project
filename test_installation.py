#!/usr/bin/env python3
"""
VisioSense Installation Test Script
===================================
This script tests if all required libraries are properly installed.
"""

def test_imports():
    """Test if all required libraries can be imported."""
    print("Testing VisioSense installation...")
    print("=" * 40)
    
    # Test OpenCV
    try:
        import cv2
        print(f"✅ OpenCV: {cv2.__version__}")
    except ImportError as e:
        print(f"❌ OpenCV: Failed to import - {e}")
        return False
    
    # Test MediaPipe
    try:
        import mediapipe as mp
        print(f"✅ MediaPipe: {mp.__version__}")
    except ImportError as e:
        print(f"❌ MediaPipe: Failed to import - {e}")
        return False
    
    # Test NumPy
    try:
        import numpy as np
        print(f"✅ NumPy: {np.__version__}")
    except ImportError as e:
        print(f"❌ NumPy: Failed to import - {e}")
        return False
    
    # Test PyAutoGUI
    try:
        import pyautogui
        print(f"✅ PyAutoGUI: {pyautogui.__version__}")
    except ImportError as e:
        print(f"❌ PyAutoGUI: Failed to import - {e}")
        return False
    
    # Test SpeechRecognition
    try:
        import speech_recognition
        print(f"✅ SpeechRecognition: {speech_recognition.__version__}")
    except ImportError as e:
        print(f"⚠️  SpeechRecognition: Not installed - {e}")
        print("   Voice commands will be disabled")
    
    # Test PyAudio
    try:
        import pyaudio
        print(f"✅ PyAudio: Available")
    except ImportError as e:
        print(f"⚠️  PyAudio: Not installed - {e}")
        print("   Voice commands will be disabled")
    
    # Test camera access
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("✅ Camera: Accessible")
            else:
                print("⚠️  Camera: Connected but cannot read frames")
        else:
            print("⚠️  Camera: Not accessible (may be in use by another application)")
        cap.release()
    except Exception as e:
        print(f"⚠️  Camera: Error testing - {e}")
    
    print("=" * 40)
    print("Installation test completed!")
    return True

if __name__ == "__main__":
    test_imports()
    input("Press Enter to exit...")
