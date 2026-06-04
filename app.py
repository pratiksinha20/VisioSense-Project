from flask import Flask, render_template, Response, jsonify, request, send_from_directory
import cv2
import threading
from flask_socketio import SocketIO
import json
import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from visiosense import main as visiosense_main

app = Flask(__name__, 
    template_folder=os.path.join(current_dir, 'templates'),
    static_folder=os.path.join(current_dir, 'static'))
socketio = SocketIO(app, cors_allowed_origins="*")

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

import time
import visiosense

# Shared latest frame and state
latest_frame = None

def handle_new_frame(frame):
    global latest_frame
    latest_frame = frame

def handle_status_update(mode, gesture, fingers, expression, head_angle):
    socketio.emit('status_update', {
        'mode': mode,
        'gesture': gesture,
        'fingers': fingers,
        'expression': expression,
        'head_angle': head_angle
    })

# Register callback bindings on visiosense module
visiosense.frame_callback = handle_new_frame
visiosense.status_callback = handle_status_update

# Global variables
camera_thread = None
running = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory(app.template_folder, path)

def gen_frames():
    global running, latest_frame
    while running:
        if latest_frame is not None:
            ret, buffer = cv2.imencode('.jpg', latest_frame)
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.03)  # limit stream to ~30 FPS

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start', methods=['POST'])
def start():
    global camera_thread, running
    if not running:
        running = True
        visiosense.web_running = True
        # Start visiosense_main in a background thread passing web_mode=True
        camera_thread = threading.Thread(target=visiosense_main, args=(True,))
        camera_thread.start()
        return jsonify({"status": "success"})
    return jsonify({"status": "already running"})

@app.route('/stop', methods=['POST'])
def stop():
    global running, latest_frame
    if running:
        running = False
        visiosense.web_running = False
        latest_frame = None
        return jsonify({"status": "success"})
    return jsonify({"status": "not running"})

@app.route('/minimize', methods=['POST'])
def minimize():
    cv2.setWindowProperty("VisioSense - Hand Gesture Control", 
                         cv2.WND_PROP_FULLSCREEN, 
                         cv2.WINDOW_MINIMIZED)
    return jsonify({"status": "success"})

@app.route('/update-settings', methods=['POST'])
def update_settings():
    data = request.get_json()
    if data:
        visiosense.settings['smoothing'] = float(data.get('smoothing', 40))
        visiosense.settings['sensitivity'] = float(data.get('sensitivity', 70))
        visiosense.settings['drawingMode'] = bool(data.get('drawingMode', True))
    return jsonify({"status": "success"})

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def update_client_status(mode, gesture, fingers):
    socketio.emit('status_update', {
        'mode': mode,
        'gesture': gesture,
        'fingers': fingers
    })

if __name__ == '__main__':
    # Ensure templates and static directories exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    if not os.path.exists('static'):
        os.makedirs('static')
    
    PORT = 5001
    print("Starting VisioSense Web Interface...")
    print(f"Open your web browser and go to: http://localhost:{PORT}")
    socketio.run(app, debug=True, host='0.0.0.0', port=PORT)