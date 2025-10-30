#!/usr/bin/env python3
"""
VisioSense Dependency Installation Script
=========================================
This script installs all required dependencies for VisioSense.
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("VisioSense - Dependency Installation")
    print("=" * 40)
    
    # Core packages
    core_packages = [
        "opencv-python==4.12.0.88",
        "mediapipe==0.10.14", 
        "numpy==2.2.6",
        "pyautogui==0.9.54",
        "scipy==1.16.2"
    ]
    
    # Voice recognition packages
    voice_packages = [
        "SpeechRecognition==3.10.0",
        "PyAudio==0.2.11"
    ]
    
    print("Installing core packages...")
    for package in core_packages:
        print(f"Installing {package}...")
        if install_package(package):
            print(f"✅ {package} installed successfully")
        else:
            print(f"❌ Failed to install {package}")
    
    print("\nInstalling voice recognition packages...")
    voice_success = True
    for package in voice_packages:
        print(f"Installing {package}...")
        if install_package(package):
            print(f"✅ {package} installed successfully")
        else:
            print(f"❌ Failed to install {package}")
            voice_success = False
    
    if not voice_success:
        print("\n⚠️  Voice recognition packages failed to install.")
        print("This is common on Windows. You can:")
        print("1. Install PyAudio manually from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
        print("2. Or run VisioSense without voice commands (they will be disabled)")
    
    print("\n" + "=" * 40)
    print("Installation complete!")
    print("Run 'python visiosense.py' to start VisioSense")
    
    # Test installation
    print("\nTesting installation...")
    try:
        import cv2
        import mediapipe
        import numpy
        import pyautogui
        import scipy
        print("✅ Core packages working correctly")
        
        try:
            import speech_recognition
            print("✅ Voice recognition available")
        except ImportError:
            print("⚠️  Voice recognition not available")
            
    except ImportError as e:
        print(f"❌ Installation test failed: {e}")

if __name__ == "__main__":
    main()
