from flask import Flask, render_template, Response, jsonify, request
import cv2
import threading
from flask_socketio import SocketIO
import json
from visiosense import main as visiosense_main

app = Flask(__name__)
socketio = SocketIO(app)

# Global variables
camera = None
camera_thread = None
running = False

@app.route('/')
def index():
    return render_template('index.html')

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
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
