#!/usr/bin/env python3
"""
VisioSense - Hand Gesture Control System
==================================================

A complete Python project for real-time hand gesture recognition and control.

Quick Setup:
1. Install required libraries: pip install -r requirements.txt
2. Run: python visiosense.py
3. Make gestures in front of your webcam!

Features:
- Gesture Control via MediaPipe Hands
- Mouse Mode and Whiteboard Mode
- Drawing capabilities
- Smooth cursor movement
- Cheating detection
- Voice commands

Requirements: opencv-python, mediapipe, numpy, pyautogui
Works on Windows webcam in real time.
"""

import cv2
import mediapipe as mp
import math
import collections
import time
import numpy as np
import pyautogui
import sys
import os
import threading
import webbrowser
from scipy.spatial import distance as dist
from ultralytics import YOLO

# Try to import speech recognition, if not available, disable voice features
try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    print("⚠️  SpeechRecognition module not found. Voice commands will be disabled.")
    SPEECH_AVAILABLE = False
    sr = None

# Disable pyautogui failsafe for better gesture control
pyautogui.FAILSAFE = False

# ===== SETUP =====
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh

# Load YOLOv8 model globally
try:
    print("Loading YOLOv8 model...")
    yolo_model = YOLO('yolov8n.pt')
    print("✓ YOLOv8 model loaded!")
    OBJECT_DETECTION_AVAILABLE = True
except Exception as e:
    print(f"⚠️  YOLOv8 model not available: {e}")
    yolo_model = None
    OBJECT_DETECTION_AVAILABLE = False

# ===== UTILITY FUNCTIONS =====
def dist(a, b):
    """Calculate Euclidean distance between two points."""
    return math.hypot(a.x - b.x, a.y - b.y)

def count_fingers(hand_landmarks, handedness_label):
    """Count extended fingers and return both count and finger states."""
    lm = hand_landmarks.landmark
    fingers = []
    
    # Thumb (account for handedness)
    if handedness_label == "Right":
        fingers.append(1 if lm[mp_hands.HandLandmark.THUMB_TIP].x < lm[mp_hands.HandLandmark.THUMB_IP].x else 0)
    else:
        fingers.append(1 if lm[mp_hands.HandLandmark.THUMB_TIP].x > lm[mp_hands.HandLandmark.THUMB_IP].x else 0)
    
    # Other fingers (index, middle, ring, pinky)
    tips = [mp_hands.HandLandmark.INDEX_FINGER_TIP,
            mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
            mp_hands.HandLandmark.RING_FINGER_TIP,
            mp_hands.HandLandmark.PINKY_TIP]
    pips = [mp_hands.HandLandmark.INDEX_FINGER_PIP,
            mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
            mp_hands.HandLandmark.RING_FINGER_PIP,
            mp_hands.HandLandmark.PINKY_PIP]
    
    for tip, pip in zip(tips, pips):
        fingers.append(1 if lm[tip].y < lm[pip].y else 0)
    
    return sum(fingers), fingers

def detect_gesture(bits, landmarks):
    """Detect specific gestures based on finger states and landmark positions."""
    total = sum(bits)
    d_thumb_index = dist(landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP],
                        landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP])
    
    # Gesture detection logic
    if total == 0:
        return "Fist"
    elif d_thumb_index < 0.04 and sum(bits[2:]) == 0:
        return "Pinch"
    elif total == 1 and bits[1] == 1:
        return "Index Pointing"
    elif total == 2 and bits[1] == 1 and bits[2] == 1:
        d_idx_mid = dist(landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP],
                        landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP])
        if d_idx_mid < 0.08:
            return "Two-Finger Scroll"
        return "Peace"
    elif total == 5:
        return "Open Hand"
    else:
        return f"{total} Fingers"

def detect_namaskar(hand1, hand2):
    """Detect Namaskar gesture when two hands are close together."""
    wrist_distance = dist(hand1.landmark[0], hand2.landmark[0])
    return wrist_distance < 0.15

def majority(sequence):
    """Find the most common element in a sequence."""
    if not sequence:
        return None
    return collections.Counter(sequence).most_common(1)[0][0]

def calculate_face_angle(landmarks):
    """Calculate head rotation angle from face landmarks."""
    nose_tip = landmarks[1]
    left_ear = landmarks[234]
    right_ear = landmarks[454]
    
    ear_center_x = (left_ear.x + right_ear.x) / 2
    ear_center_y = (left_ear.y + right_ear.y) / 2
    
    angle = math.atan2(nose_tip.y - ear_center_y, nose_tip.x - ear_center_x)
    angle_degrees = math.degrees(angle)
    
    return angle_degrees

def detect_facial_expression(landmarks):
    """Detect facial expression based on key facial landmarks."""
    left_mouth = landmarks[61]
    right_mouth = landmarks[291]
    mouth_center = landmarks[13]
    
    mouth_height = abs(mouth_center.y - (left_mouth.y + right_mouth.y) / 2)
    
    if mouth_height > 0.02:
        return "Happy"
    elif mouth_height < 0.005:
        return "Sad"
    else:
        return "Normal"

def process_object_detection(frame):
    """Run YOLOv8 object detection and draw results on frame."""
    detected_objects = []
    
    if not OBJECT_DETECTION_AVAILABLE or yolo_model is None:
        return frame, detected_objects
    
    try:
        # Run YOLO inference
        results = yolo_model(frame, conf=0.5)
        
        # Draw detections on frame
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                confidence = box.conf[0]
                class_id = int(box.cls[0])
                class_name = result.names[class_id]
                
                # Store detected object
                detected_objects.append({
                    'name': class_name,
                    'confidence': float(confidence)
                })
                
                # Draw bounding box (cyan color)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
                
                # Prepare label
                label = f"{class_name}: {confidence:.2f}"
                label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                label_y = y1 - 10 if y1 - 10 > 20 else y1 + 25
                
                # Draw label background
                cv2.rectangle(frame, (x1, label_y - label_size[1] - 4), 
                             (x1 + label_size[0] + 4, label_y + 4), (255, 255, 0), -1)
                
                # Draw label text
                cv2.putText(frame, label, (x1, label_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    except Exception as e:
        print(f"Error in object detection: {e}")
    
    return frame, detected_objects

def voice_command_handler():
    """Handle voice commands in a separate thread."""
    if not SPEECH_AVAILABLE:
        return
    
    try:
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
        
        while True:
            try:
                with microphone as source:
                    audio = recognizer.listen(source, timeout=1, phrase_time_limit=3)
                
                try:
                    command = recognizer.recognize_google(audio).lower()
                    print(f"Voice command: {command}")
                    
                    if "open youtube" in command:
                        webbrowser.open("https://youtube.com")
                    elif "open google" in command:
                        webbrowser.open("https://google.com")
                    elif "open whatsapp" in command:
                        webbrowser.open("https://web.whatsapp.com")
                        
                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    pass
                    
            except sr.WaitTimeoutError:
                pass
                
    except Exception as e:
        print(f"Voice recognition error: {e}")

def check_camera():
    """Check if camera is available and working."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return False, None
    
    ret, frame = cap.read()
    if not ret:
        cap.release()
        return False, None
    
    cap.release()
    return True, frame.shape

# ===== MAIN APPLICATION =====
def main(web_mode=False):
    """Main application function."""
    if not web_mode:
        print("VisioSense - Hand Gesture Control System")
        print("========================================")
    
    # Check camera availability
    camera_available, frame_shape = check_camera()
    if not camera_available:
        print("❌ Error: Camera not found or not accessible!")
        input("Press Enter to exit...")
        return
    
    print("✅ Camera detected successfully!")
    print("\nGesture Controls:")
    print("- Fist → Mouse Mode (cursor control)")
    print("- Open Hand → Whiteboard Mode (drawing)")
    print("- Index Finger Only → Draw on screen")
    print("- Index + Middle Finger → Scroll and Click")
    print("- Pinch → Click (hold for drag)")
    print("- Namaskar (both hands close) → Exit")
    print("- Press 'q' or ESC to exit")
    print("\nStarting VisioSense...")
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Failed to open camera!")
        return
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Screen size for pyautogui mapping
    screen_w, screen_h = pyautogui.size()
    
    # State variables
    canvas = None
    GESTURE_HISTORY = collections.deque(maxlen=8)
    
    # Mouse control variables
    prev_mouse_x, prev_mouse_y = screen_w // 2, screen_h // 2
    mouse_mode = False
    whiteboard_mode = False
    
    # Pinch/click state
    pinch_down = False
    pinch_start = 0.0
    drag_active = False
    last_click_time = 0.0
    min_click_interval = 0.3
    pinch_threshold = 0.04
    
    # Scroll state
    prev_mid_y = None
    scroll_accum = 0.0
    
    # Namaskar detection
    namaskar_counter = 0
    close_app = False
    
    # Drawing state
    last_draw_pos = None
    last_clear_time = 0.0
    
    # Cheating detection
    head_movement_count = 0
    last_head_movement_time = 0.0
    
    # Start voice recognition thread if available
    if SPEECH_AVAILABLE:
        voice_thread = threading.Thread(target=voice_command_handler, daemon=True)
        voice_thread.start()
        print("🎤 Voice recognition started!")
    else:
        print("🎤 Voice recognition disabled.")
    
    # Initialize MediaPipe solutions
    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    ) as hands, \
    mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    ) as face_mesh:
        
        print("🎯 VisioSense is running! Make gestures in front of the camera.")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read frame from camera")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            
            # Initialize canvas for drawing
            if canvas is None:
                canvas = np.zeros_like(frame)
            
            # Convert BGR to RGB for MediaPipe
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            hand_results = hands.process(rgb)
            face_results = face_mesh.process(rgb)
            
            # Run object detection
            frame, detected_objects = process_object_detection(frame)
            
            # Get hand landmarks and handedness
            multi_hand_landmarks = hand_results.multi_hand_landmarks
            multi_handedness = hand_results.multi_handedness
            
            # Initialize variables
            current_expression = None
            head_angle = 0
            total_fingers = 0
            cheating_detected = False
            stable_gesture = None
            finger_count = 0
            
            # Face detection and expression analysis
            if face_results.multi_face_landmarks:
                face_landmarks = face_results.multi_face_landmarks[0]
                
                # Detect facial expression
                current_expression = detect_facial_expression(face_landmarks.landmark)
                
                # Calculate head angle for cheating detection
                head_angle = calculate_face_angle(face_landmarks.landmark)
                
                # Cheating detection: head movement < 20 degrees or equal to 0
                if abs(head_angle) < 20 or abs(head_angle) == 0:
                    # Count head movements within 5 seconds
                    if time.time() - last_head_movement_time < 5.0:
                        head_movement_count += 1
                    else:
                        head_movement_count = 1
                    
                    last_head_movement_time = time.time()
                    
                    # Detect cheating if more than 2 head movements
                    if head_movement_count > 2:
                        cheating_detected = True
                        cv2.putText(frame, "CHEATING DETECTED!", (w//2 - 150, h//2 - 50), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                        cv2.rectangle(frame, (w//2 - 200, h//2 - 80), (w//2 + 200, h//2 + 20), (0, 0, 255), 3)
            
            if multi_hand_landmarks:
                # Check for Namaskar gesture (both hands close)
                if len(multi_hand_landmarks) == 2 and detect_namaskar(multi_hand_landmarks[0], multi_hand_landmarks[1]):
                    namaskar_counter += 1
                    if namaskar_counter > 20:
                        close_app = True
                else:
                    namaskar_counter = 0
                
                # Process all hands for finger counting and gesture detection
                total_fingers = 0
                
                for i, hand_landmarks in enumerate(multi_hand_landmarks):
                    handedness = multi_handedness[i].classification[0].label if multi_handedness else "Right"
                    count, finger_bits = count_fingers(hand_landmarks, handedness)
                    total_fingers += count
                    
                    gesture = detect_gesture(finger_bits, hand_landmarks)
                    
                    # Use first hand for primary gesture detection
                    if i == 0:
                        finger_count = count
                        if gesture:
                            GESTURE_HISTORY.append(gesture)
                
                stable_gesture = majority(GESTURE_HISTORY)
                
                # Mode detection
                if stable_gesture == "Fist":
                    mouse_mode = True
                    whiteboard_mode = False
                elif stable_gesture == "Open Hand":
                    whiteboard_mode = True
                    mouse_mode = False
                else:
                    # Default to whiteboard mode for drawing and scrolling
                    whiteboard_mode = True
                    mouse_mode = False
                
                # Draw hand landmarks
                for hand_landmarks in multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                        mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                    )
            else:
                # Clear gesture history when no hands detected
                GESTURE_HISTORY.clear()
                namaskar_counter = 0
                prev_mid_y = None
                scroll_accum = 0.0
                last_draw_pos = None
            
            # Overlay canvas (drawing) on frame
            frame = cv2.add(frame, canvas)
            
            # Process gestures and actions
            if stable_gesture and multi_hand_landmarks:
                primary_hand = multi_hand_landmarks[0]
                landmarks = primary_hand.landmark
                
                # Get key landmark positions
                index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
                
                # Calculate distances
                d_thumb_index = dist(thumb_tip, index_tip)
                mid_y = (index_tip.y + middle_tip.y) / 2.0
                
                # MOUSE MODE - Handle mouse operations (Fist gesture)
                if mouse_mode:
                    # Map index fingertip to screen coordinates with margins
                    margin = 0.15
                    raw_x = np.interp(index_tip.x, [margin, 1 - margin], [0, screen_w])
                    raw_y = np.interp(index_tip.y, [margin, 1 - margin], [0, screen_h])
                    
                    # Smooth cursor movement
                    mouse_x = prev_mouse_x + (raw_x - prev_mouse_x) * 0.4
                    mouse_y = prev_mouse_y + (raw_y - prev_mouse_y) * 0.4
                    
                    try:
                        pyautogui.moveTo(mouse_x, mouse_y)
                    except Exception:
                        pass
                    
                    prev_mouse_x, prev_mouse_y = mouse_x, mouse_y
                    
                    # Pinch handling - Click and Drag
                    pinch_now = (d_thumb_index < pinch_threshold)
                    
                    # Start pinch
                    if pinch_now and not pinch_down:
                        pinch_down = True
                        pinch_start = time.time()
                    
                    # Release pinch
                    if not pinch_now and pinch_down:
                        if drag_active:
                            try:
                                pyautogui.mouseUp()
                            except Exception:
                                pass
                            drag_active = False
                        else:
                            # Click on release with debouncing
                            if time.time() - last_click_time > min_click_interval:
                                try:
                                    pyautogui.click()
                                except Exception:
                                    pass
                                last_click_time = time.time()
                        pinch_down = False
                    
                    # Long pinch -> start drag
                    if pinch_now and pinch_down and not drag_active:
                        if time.time() - pinch_start > 0.6:
                            try:
                                pyautogui.mouseDown()
                                drag_active = True
                            except Exception:
                                drag_active = False
                    
                    # Visual feedback for mouse mode
                    px, py = int(index_tip.x * w), int(index_tip.y * h)
                    if pinch_down:
                        color = (0, 0, 255) if drag_active else (0, 255, 255)
                        cv2.circle(frame, (px, py), 20, color, 3)
                        if drag_active:
                            cv2.putText(frame, "DRAGGING", (px + 25, py), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    else:
                        cv2.circle(frame, (px, py), 10, (255, 0, 255), -1)
                
                # WHITEBOARD MODE - Handle drawing and scrolling (Open Hand gesture)
                elif whiteboard_mode:
                    # Two-Finger scroll (index + middle fingers) - scroll and click
                    if stable_gesture == "Two-Finger Scroll":
                        if prev_mid_y is not None:
                            dy = prev_mid_y - mid_y
                            scroll_accum += dy * 1000
                            if abs(scroll_accum) > 50:
                                try:
                                    pyautogui.scroll(int(scroll_accum))
                                except Exception:
                                    pass
                                scroll_accum = 0.0
                        prev_mid_y = mid_y
                        
                        # Also handle clicking with two fingers
                        if d_thumb_index < pinch_threshold:
                            if time.time() - last_click_time > min_click_interval:
                                try:
                                    pyautogui.click()
                                except Exception:
                                    pass
                                last_click_time = time.time()
                        
                        # Visual feedback for scrolling and clicking
                        cv2.putText(frame, "SCROLLING & CLICKING", (10, 150), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    else:
                        prev_mid_y = None
                        scroll_accum = 0.0
                    
                    # Index pointing -> draw on canvas (ONLY single index finger)
                    if stable_gesture == "Index Pointing":
                        ix, iy = int(index_tip.x * w), int(index_tip.y * h)
                        cv2.circle(frame, (ix, iy), 12, (0, 0, 255), cv2.FILLED)
                        
                        # Draw on canvas
                        if last_draw_pos is None:
                            last_draw_pos = (ix, iy)
                        cv2.line(canvas, last_draw_pos, (ix, iy), (0, 0, 255), 8)
                        last_draw_pos = (ix, iy)
                        
                        # Visual feedback for drawing
                        cv2.putText(frame, "DRAWING", (10, 150), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    else:
                        last_draw_pos = None
                    
                    # Clear canvas with Open Hand (debounced)
                    if stable_gesture == "Open Hand":
                        if time.time() - last_clear_time > 1.0:
                            canvas[:] = 0
                            last_clear_time = time.time()
            
            # Draw status overlay
            mode_text = "Mouse Mode" if mouse_mode else "Whiteboard Mode"
            mode_color = (0, 255, 0) if mouse_mode else (255, 0, 255)
            cv2.putText(frame, f"Mode: {mode_text}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, mode_color, 2)
            cv2.putText(frame, f"Gesture: {stable_gesture or 'None'}", (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.putText(frame, f"Fingers: {finger_count}", (10, 90), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            if total_fingers > 0:
                cv2.putText(frame, f"Total Fingers: {total_fingers}/10", (10, 120), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            if current_expression:
                expression_color = (0, 255, 0) if current_expression == "Happy" else (0, 0, 255) if current_expression == "Sad" else (255, 255, 255)
                cv2.putText(frame, f"Expression: {current_expression}", (w - 200, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, expression_color, 2)
            
            cv2.putText(frame, f"Head Angle: {head_angle:.1f}°", (w - 200, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Show closing message
            if namaskar_counter > 1:
                cv2.putText(frame, "Namaskar detected - Closing...", 
                           (w//2 - 200, h//2), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            
            # Display frame
            cv2.imshow("VisioSense - Hand Gesture Control", frame)
            
            # Set window to be always on top
            cv2.setWindowProperty("VisioSense - Hand Gesture Control", cv2.WND_PROP_TOPMOST, 1)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('m'):  # Press 'm' to minimize
                cv2.setWindowProperty("VisioSense - Hand Gesture Control", cv2.WND_PROP_FULLSCREEN, 
                                   cv2.WINDOW_MINIMIZED)
            elif key in (27, ord('q')) or close_app:
                break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("👋 VisioSense closed successfully!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 VisioSense interrupted by user")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        cv2.destroyAllWindows()