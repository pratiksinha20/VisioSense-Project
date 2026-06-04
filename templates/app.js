/* ==========================================================================
   VisioSense Frontend JavaScript Controller
   ========================================================================== */

// --- Global Application State ---
let socket = null;
let isRunning = false;
let backendUrl = "http://localhost:5001";
let settingsDebounceTimeout = null;

// --- DOM Element References ---
const elements = {
    // Connection Pill
    connectionStatus: document.getElementById('connectionStatus'),
    statusText: document.querySelector('#connectionStatus .status-text'),
    
    // Video Streams
    cameraOffline: document.getElementById('cameraFeedOffline'),
    streamWrapper: document.getElementById('videoStreamContainer'),
    
    // Buttons
    btnStart: document.getElementById('btnStart'),
    btnStop: document.getElementById('btnStop'),
    
    // Telemetry display fields
    telemetryMode: document.getElementById('telemetryMode'),
    telemetryGesture: document.getElementById('telemetryGesture'),
    telemetryFingers: document.getElementById('telemetryFingers'),
    telemetryExpression: document.getElementById('telemetryExpression'),
    telemetryHeadAngle: document.getElementById('telemetryHeadAngle'),
    angleBar: document.getElementById('angleBar'),
    compassIcon: document.getElementById('compassIcon'),
    metricModeIcon: document.getElementById('metricModeIcon'),
    
    // Settings inputs
    inputBackendUrl: document.getElementById('inputBackendUrl'),
    rangeSmoothing: document.getElementById('rangeSmoothing'),
    rangeSensitivity: document.getElementById('rangeSensitivity'),
    valSmoothing: document.getElementById('valSmoothing'),
    valSensitivity: document.getElementById('valSensitivity'),
    checkDrawingMode: document.getElementById('checkDrawingMode'),
    
    // Logger Console
    consoleLog: document.getElementById('consoleLog')
};

// --- Initialisation on Page Load ---
document.addEventListener("DOMContentLoaded", () => {
    // 1. Retrieve configured backend endpoint or set default
    const savedBackend = localStorage.getItem("visiosense_backend_url");
    if (savedBackend) {
        backendUrl = savedBackend;
    } else {
        // Fallback to local origin if page is served from same server
        const currentOrigin = window.location.origin;
        if (!currentOrigin.includes("vercel") && !currentOrigin.includes("github.io")) {
            backendUrl = currentOrigin;
        }
    }
    elements.inputBackendUrl.value = backendUrl;
    logToConsole('system', `Loaded API backend configuration: ${backendUrl}`);

    // 2. Establish Real-time Socket Connection
    connectSocket();

    // 3. Register Settings UI Listeners
    setupSettingsListeners();
});

// --- Console Logger Utility ---
function logToConsole(type, message) {
    const timestamp = new Date().toLocaleTimeString();
    let typeClass = 'system-msg';
    let prefix = '[SYSTEM]';

    switch(type) {
        case 'info':
            typeClass = 'info-msg';
            prefix = '[INFO]';
            break;
        case 'success':
            typeClass = 'success-msg';
            prefix = '[SUCCESS]';
            break;
        case 'warn':
            typeClass = 'warn-msg';
            prefix = '[WARNING]';
            break;
        case 'error':
            typeClass = 'error-msg';
            prefix = '[ERROR]';
            break;
    }

    const logLine = document.createElement('div');
    logLine.className = `console-line ${typeClass}`;
    logLine.textContent = `[${timestamp}] ${prefix} ${message}`;
    
    elements.consoleLog.appendChild(logLine);
    
    // Auto Scroll to bottom
    elements.consoleLog.scrollTop = elements.consoleLog.scrollHeight;
}

function clearConsoleLog() {
    elements.consoleLog.innerHTML = '';
    logToConsole('system', 'Console cleared.');
}

// --- Backend Endpoint Configuration ---
function saveBackendEndpoint() {
    let urlInput = elements.inputBackendUrl.value.trim();
    
    // Remove trailing slash if present
    if (urlInput.endsWith('/')) {
        urlInput = urlInput.slice(0, -1);
    }

    if (!urlInput) {
        logToConsole('error', 'Backend URL cannot be empty.');
        return;
    }

    try {
        // Simple validation check
        new URL(urlInput);
        
        backendUrl = urlInput;
        localStorage.setItem("visiosense_backend_url", backendUrl);
        logToConsole('success', `Saved new backend URL endpoint: ${backendUrl}`);
        
        // Reconnect socket to new URL
        connectSocket();
    } catch(err) {
        logToConsole('error', 'Invalid URL format. Please include protocol (e.g. http:// or https://)');
    }
}

// --- Socket.io Real-time Telemetry Client ---
function connectSocket() {
    // Disconnect old socket if active
    if (socket) {
        socket.disconnect();
        logToConsole('info', 'Closing existing socket connection...');
    }

    logToConsole('info', `Attempting connection to telemetry stream at: ${backendUrl}`);
    
    // Initialise socket.io connection
    socket = io(backendUrl, {
        reconnectionAttempts: 5,
        timeout: 10000,
        transports: ['websocket', 'polling']
    });

    // Connection Events
    socket.on('connect', () => {
        setConnectionState('connected');
        logToConsole('success', `Telemetry stream connected to backend: ${backendUrl}`);
    });

    socket.on('disconnect', (reason) => {
        setConnectionState('disconnected');
        logToConsole('error', `Disconnected from backend telemetry stream. Reason: ${reason}`);
    });

    socket.on('connect_error', (error) => {
        setConnectionState('connecting');
        logToConsole('warn', `Telemetry socket connection error: ${error.message}. Checking server availability...`);
    });

    // Custom Telemetry Event handler
    socket.on('status_update', (data) => {
        updateTelemetryView(data);
    });
}

function setConnectionState(state) {
    // Reset classes
    elements.connectionStatus.className = 'status-pill';
    
    if (state === 'connected') {
        elements.connectionStatus.classList.add('status-connected');
        elements.statusText.textContent = 'Connected';
    } else if (state === 'connecting') {
        elements.connectionStatus.classList.add('status-connecting');
        elements.statusText.textContent = 'Connecting';
    } else {
        elements.connectionStatus.classList.add('status-disconnected');
        elements.statusText.textContent = 'Disconnected';
        // Reset telemetry fields when offline
        resetTelemetryData();
    }
}

// --- Update UI Telemetry Data ---
function updateTelemetryView(data) {
    if (!data) return;

    // 1. Mode Telemetry Update
    if (data.mode) {
        elements.telemetryMode.textContent = data.mode;
        if (data.mode.toLowerCase().includes('mouse')) {
            elements.metricModeIcon.className = 'fas fa-mouse-pointer';
            elements.telemetryMode.style.color = 'var(--color-primary)';
        } else if (data.mode.toLowerCase().includes('whiteboard') || data.mode.toLowerCase().includes('draw')) {
            elements.metricModeIcon.className = 'fas fa-chalkboard';
            elements.telemetryMode.style.color = 'var(--color-accent)';
        }
    }

    // 2. Gesture Telemetry Update
    if (data.gesture) {
        elements.telemetryGesture.textContent = data.gesture;
        if (data.gesture !== "No Gesture" && data.gesture !== "None") {
            elements.telemetryGesture.style.color = 'hsl(290, 100%, 70%)';
        } else {
            elements.telemetryGesture.style.color = '';
        }
    }

    // 3. Fingers Tracked
    if (data.fingers !== undefined) {
        elements.telemetryFingers.textContent = data.fingers;
    }

    // 4. Expression
    if (data.expression) {
        elements.telemetryExpression.textContent = data.expression;
        if (data.expression.toLowerCase() === 'happy') {
            elements.telemetryExpression.style.color = 'var(--color-accent)';
        } else if (data.expression.toLowerCase() === 'sad') {
            elements.telemetryExpression.style.color = 'var(--color-danger)';
        } else {
            elements.telemetryExpression.style.color = '';
        }
    }

    // 5. Head Tilt Angle
    if (data.head_angle !== undefined) {
        const angle = parseFloat(data.head_angle);
        elements.telemetryHeadAngle.textContent = `${angle.toFixed(1)}°`;
        
        // Rotate compass icon
        elements.compassIcon.style.transform = `rotate(${angle}deg)`;
        
        // Adjust head angle progress display (ranges roughly -90 to +90 degrees)
        // Normalise value to 0% - 100% (where 0 is -90deg, 50% is 0deg, 100% is +90deg)
        const normalisedPercent = Math.min(Math.max(((angle + 90) / 180) * 100, 0), 100);
        elements.angleBar.style.width = `${normalisedPercent}%`;

        if (Math.abs(angle) > 25) {
            elements.angleBar.style.background = 'var(--color-danger)';
        } else {
            elements.angleBar.style.background = '';
        }
    }
}

function resetTelemetryData() {
    elements.telemetryMode.textContent = "Offline";
    elements.telemetryMode.style.color = "";
    elements.telemetryGesture.textContent = "None";
    elements.telemetryGesture.style.color = "";
    elements.telemetryFingers.textContent = "0";
    elements.telemetryExpression.textContent = "Normal";
    elements.telemetryExpression.style.color = "";
    elements.telemetryHeadAngle.textContent = "0.0°";
    elements.angleBar.style.width = "50%";
    elements.compassIcon.style.transform = "rotate(0deg)";
    elements.metricModeIcon.className = "fas fa-mouse-pointer";
}

// --- Controller Actions & Fetch Endpoints ---
function startCamera() {
    logToConsole('info', 'Sending camera startup signal...');
    elements.btnStart.disabled = true;

    fetch(`${backendUrl}/start`, { 
        method: 'POST',
        headers: { 'Accept': 'application/json' }
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    })
    .then(data => {
        if (data.status === 'success' || data.status === 'already running') {
            isRunning = true;
            logToConsole('success', 'Camera started. Fetching video stream...');
            
            // Switch display wrappers
            elements.cameraOffline.classList.add('hidden');
            elements.streamWrapper.classList.remove('hidden');
            
            // Inject JPEG stream url
            elements.streamWrapper.innerHTML = `<img src="${backendUrl}/video_feed" alt="Webcam Stream" id="videoElement">`;
            
            elements.btnStop.disabled = false;
        } else {
            elements.btnStart.disabled = false;
            logToConsole('error', `Failed to start camera: ${data.status}`);
        }
    })
    .catch(err => {
        elements.btnStart.disabled = false;
        logToConsole('error', `Connection error: Unable to reach start endpoint. ${err.message}`);
    });
}

function stopCamera() {
    logToConsole('info', 'Sending camera shutdown signal...');
    elements.btnStop.disabled = true;

    fetch(`${backendUrl}/stop`, { 
        method: 'POST',
        headers: { 'Accept': 'application/json' }
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    })
    .then(data => {
        if (data.status === 'success' || data.status === 'not running') {
            isRunning = false;
            logToConsole('success', 'Camera stopped. Feed deactivated.');
            
            // Reset display wrappers
            elements.streamWrapper.classList.add('hidden');
            elements.streamWrapper.innerHTML = '';
            elements.cameraOffline.classList.remove('hidden');
            
            elements.btnStart.disabled = false;
        } else {
            elements.btnStop.disabled = false;
            logToConsole('error', `Failed to stop camera: ${data.status}`);
        }
    })
    .catch(err => {
        elements.btnStop.disabled = false;
        logToConsole('error', `Connection error: Unable to reach stop endpoint. ${err.message}`);
    });
}

function minimizeWindow() {
    logToConsole('info', 'Sending window minimise request...');
    fetch(`${backendUrl}/minimize`, { method: 'POST' })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            logToConsole('success', 'Minimise command executed successfully.');
        } else {
            logToConsole('error', 'Backend failed to minimise camera window.');
        }
    })
    .catch(err => {
        logToConsole('error', `Network error during window operation: ${err.message}`);
    });
}

// --- Settings Listeners and Sync ---
function setupSettingsListeners() {
    // 1. Text Indicators updates
    elements.rangeSmoothing.addEventListener('input', (e) => {
        elements.valSmoothing.textContent = `${e.target.value}%`;
        debounceSettingsUpdate();
    });

    elements.rangeSensitivity.addEventListener('input', (e) => {
        elements.valSensitivity.textContent = `${e.target.value}%`;
        debounceSettingsUpdate();
    });

    elements.checkDrawingMode.addEventListener('change', () => {
        debounceSettingsUpdate();
    });
}

function debounceSettingsUpdate() {
    // Debounce updates so we don't spam fetch requests during slider movement
    clearTimeout(settingsDebounceTimeout);
    settingsDebounceTimeout = setTimeout(sendSettingsUpdate, 350);
}

function sendSettingsUpdate() {
    const payload = {
        smoothing: parseFloat(elements.rangeSmoothing.value),
        sensitivity: parseFloat(elements.rangeSensitivity.value),
        drawingMode: elements.checkDrawingMode.checked
    };

    logToConsole('info', `Updating settings: Smoothing: ${payload.smoothing}%, Sensitivity: ${payload.sensitivity}%, Drawing Mode: ${payload.drawingMode}`);

    fetch(`${backendUrl}/update-settings`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            logToConsole('success', 'Settings synced successfully on python backend.');
        } else {
            logToConsole('warn', 'Settings received but backend reported unsuccessful sync.');
        }
    })
    .catch(err => {
        logToConsole('error', `Failed to sync settings with backend: ${err.message}`);
    });
}
