from flask import Flask, render_template, Response, jsonify, request
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
socketio = SocketIO(app)

# Global variables
camera = None
camera_thread = None
running = False

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>VisioSense</title>
        <style>
            :root {
                --primary-color: #4385f5;
                --accent-color: #00ff9d;
                --background-dark: #0a0b1a;
                --card-background: #141428;
                --text-color: #ffffff;
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: var(--background-dark);
                color: var(--text-color);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
            }
            
            header {
                text-align: center;
                margin-bottom: 40px;
            }
            
            .logo {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                margin-bottom: 10px;
            }
            
            .logo h1 {
                font-size: 2.5em;
                color: var(--text-color);
            }
            
            .subtitle {
                color: var(--primary-color);
                font-size: 1.2em;
            }
            
            .main-content {
                display: grid;
                grid-template-columns: 1fr 300px;
                gap: 20px;
            }
            
            .camera-section {
                background: var(--card-background);
                border-radius: 15px;
                padding: 20px;
                position: relative;
            }
            
            #camera-feed {
                width: 100%;
                aspect-ratio: 16/9;
                background: #000;
                border-radius: 10px;
                overflow: hidden;
                margin-bottom: 20px;
            }
            
            #camera-feed img {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
            
            .fps-overlay {
                position: absolute;
                top: 30px;
                left: 30px;
                background: rgba(0, 0, 0, 0.7);
                padding: 5px 10px;
                border-radius: 5px;
            }
            
            .status-panel {
                background: var(--card-background);
                border-radius: 15px;
                padding: 20px;
            }
            
            .status-section {
                margin-bottom: 30px;
            }
            
            .status-section h2 {
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 20px;
                color: var(--accent-color);
            }
            
            .status-item {
                background: rgba(255, 255, 255, 0.05);
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 10px;
            }
            
            .controls {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
                margin-top: 20px;
            }
            
            .btn {
                padding: 12px;
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                transition: transform 0.2s;
            }
            
            .btn:hover {
                transform: translateY(-2px);
            }
            
            .btn-start { background-color: #00c853; }
            .btn-stop { background-color: #ff3d00; }
            .btn-minimize { background-color: #ffd600; }
            .btn-settings { background-color: var(--primary-color); }
            
            .gesture-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin-top: 30px;
            }
            
            .gesture-card {
                background: rgba(255, 255, 255, 0.05);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }
            
            .gesture-card i {
                font-size: 2em;
                color: var(--primary-color);
                margin-bottom: 10px;
            }
            
            .settings-panel {
                margin-top: 20px;
            }
            
            .slider-container {
                margin: 15px 0;
            }
            
            .slider-container label {
                display: block;
                margin-bottom: 5px;
            }
            
            input[type="range"] {
                width: 100%;
                background: var(--primary-color);
            }
            
            .checkbox-container {
                display: flex;
                align-items: center;
                gap: 10px;
                margin: 15px 0;
            }
        </style>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    </head>
    <body>
        <div class="container">
            <header>
                <div class="logo">
                    <i class="fas fa-hand-paper fa-2x"></i>
                    <h1>VisioSense</h1>
                </div>
                <p class="subtitle">ADVANCED HAND GESTURE CONTROL SYSTEM</p>
            </header>

            <div class="main-content">
                <div class="camera-section">
                    <div id="camera-feed"></div>
                    <div class="fps-overlay">
                        FPS: <span id="fpsCounter">0</span> | Resolution: <span id="resolution">-</span>
                    </div>
                    <div class="controls">
                        <button class="btn btn-start" onclick="startCamera()">
                            <i class="fas fa-play"></i> START
                        </button>
                        <button class="btn btn-stop" onclick="stopCamera()">
                            <i class="fas fa-stop"></i> STOP
                        </button>
                        <button class="btn btn-minimize" onclick="minimizeWindow()">
                            <i class="fas fa-window-minimize"></i> MINIMIZE
                        </button>
                        <button class="btn btn-settings" onclick="toggleSettings()">
                            <i class="fas fa-cog"></i> SETTINGS
                        </button>
                    </div>
                </div>

                <div class="status-panel">
                    <div class="status-section">
                        <h2><i class="fas fa-info-circle"></i> Status</h2>
                        <div class="status-item">
                            <div>Mode: <span id="currentMode">Mouse Mode</span></div>
                        </div>
                        <div class="status-item">
                            <div>Gesture: <span id="currentGesture">No Gesture</span></div>
                        </div>
                        <div class="status-item">
                            <div>Fingers: <span id="fingerCount">0</span></div>
                        </div>
                    </div>

                    <div class="settings-panel">
                        <h2><i class="fas fa-sliders"></i> Settings</h2>
                        <div class="slider-container">
                            <label>Cursor Smoothing</label>
                            <input type="range" id="smoothing" min="0" max="100" value="40">
                        </div>
                        <div class="slider-container">
                            <label>Gesture Sensitivity</label>
                            <input type="range" id="sensitivity" min="0" max="100" value="70">
                        </div>
                        <div class="checkbox-container">
                            <input type="checkbox" id="drawingMode" checked>
                            <label for="drawingMode">Enable Drawing Mode</label>
                        </div>
                    </div>
                </div>
            </div>

            <div class="gesture-grid">
                <div class="gesture-card">
                    <i class="fas fa-hand-fist"></i>
                    <h4>Fist</h4>
                    <p>Mouse Mode</p>
                </div>
                <div class="gesture-card">
                    <i class="fas fa-hand"></i>
                    <h4>Open Hand</h4>
                    <p>Draw Mode</p>
                </div>
                <div class="gesture-card">
                    <i class="fas fa-hand-point-up"></i>
                    <h4>Point</h4>
                    <p>Click</p>
                </div>
                <div class="gesture-card">
                    <i class="fas fa-hand-peace"></i>
                    <h4>Peace</h4>
                    <p>Scroll</p>
                </div>
            </div>
        </div>

        <script>
            let isRunning = false;
            
            function startCamera() {
                if (!isRunning) {
                    fetch('/start', { method: 'POST' })
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === 'success') {
                                isRunning = true;
                                const feed = document.getElementById('camera-feed');
                                feed.innerHTML = '<img src="/video_feed">';
                                document.querySelector('.btn-start').disabled = true;
                                document.querySelector('.btn-stop').disabled = false;
                            }
                        });
                }
            }
            
            function stopCamera() {
                if (isRunning) {
                    fetch('/stop', { method: 'POST' })
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === 'success') {
                                isRunning = false;
                                const feed = document.getElementById('camera-feed');
                                feed.innerHTML = '';
                                document.querySelector('.btn-start').disabled = false;
                                document.querySelector('.btn-stop').disabled = true;
                            }
                        });
                }
            }
            
            function minimizeWindow() {
                fetch('/minimize', { method: 'POST' });
            }
            
            function updateSettings() {
                const settings = {
                    smoothing: document.getElementById('smoothing').value,
                    sensitivity: document.getElementById('sensitivity').value,
                    drawingMode: document.getElementById('drawingMode').checked
                };
                
                fetch('/update-settings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(settings)
                });
            }
            
            // Initialize
            document.querySelector('.btn-stop').disabled = true;
            
            // Add event listeners for settings
            document.getElementById('smoothing').addEventListener('change', updateSettings);
            document.getElementById('sensitivity').addEventListener('change', updateSettings);
            document.getElementById('drawingMode').addEventListener('change', updateSettings);
            
            // Optional: WebSocket connection for real-time updates
            const socket = io();
            socket.on('status_update', function(data) {
                document.getElementById('currentMode').textContent = data.mode;
                document.getElementById('currentGesture').textContent = data.gesture;
                document.getElementById('fingerCount').textContent = data.fingers;
            });
        </script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    </body>
    </html>
    '''

def gen_frames():
    global running
    while running:
        if camera:
            success, frame = camera.read()
            if success:
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start', methods=['POST'])
def start():
    global camera, camera_thread, running
    if not running:
        running = True
        camera = cv2.VideoCapture(0)
        camera_thread = threading.Thread(target=visiosense_main)
        camera_thread.start()
        return jsonify({"status": "success"})
    return jsonify({"status": "already running"})

@app.route('/stop', methods=['POST'])
def stop():
    global camera, running
    if running:
        running = False
        if camera:
            camera.release()
            camera = None
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
    settings = request.get_json()
    # Update your visiosense settings here
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