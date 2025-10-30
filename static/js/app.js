document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const minimizeBtn = document.getElementById('minimizeBtn');
    const currentMode = document.getElementById('currentMode');
    const currentGesture = document.getElementById('currentGesture');
    const fingerCount = document.getElementById('fingerCount');
    
    // Settings elements
    const smoothingSlider = document.getElementById('smoothing');
    const sensitivitySlider = document.getElementById('sensitivity');
    const drawingEnabled = document.getElementById('drawingEnabled');
    
    // WebSocket connection for real-time updates
    let ws = null;
    
    function connectWebSocket() {
        ws = new WebSocket('ws://' + window.location.host + '/ws');
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateUI(data);
        };
        
        ws.onclose = function() {
            setTimeout(connectWebSocket, 1000);
        };
    }
    
    function updateUI(data) {
        // Update status indicators
        currentMode.textContent = data.mode;
        currentGesture.textContent = data.gesture;
        fingerCount.textContent = data.fingers;
        
        // Update mode styling
        currentMode.className = '';
        currentMode.classList.add(data.mode.toLowerCase().replace(' ', '-'));
        
        // Update gesture visualization
        updateGestureVisualization(data.gesture);
    }
    
    function updateGestureVisualization(gesture) {
        const gestureCards = document.querySelectorAll('.gesture-card');
        gestureCards.forEach(card => {
            card.classList.remove('active');
            if (card.querySelector('h4').textContent.toLowerCase() === gesture.toLowerCase()) {
                card.classList.add('active');
            }
        });
    }
    
    // Button Event Listeners
    startBtn.addEventListener('click', async () => {
        try {
            await fetch('/start', { method: 'POST' });
            startBtn.disabled = true;
            stopBtn.disabled = false;
        } catch (error) {
            console.error('Failed to start:', error);
        }
    });
    
    stopBtn.addEventListener('click', async () => {
        try {
            await fetch('/stop', { method: 'POST' });
            startBtn.disabled = false;
            stopBtn.disabled = true;
        } catch (error) {
            console.error('Failed to stop:', error);
        }
    });
    
    minimizeBtn.addEventListener('click', async () => {
        try {
            await fetch('/minimize', { method: 'POST' });
        } catch (error) {
            console.error('Failed to minimize:', error);
        }
    });
    
    // Settings Event Listeners
    smoothingSlider.addEventListener('input', async (e) => {
        try {
            await fetch('/update-settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    smoothing: e.target.value
                })
            });
        } catch (error) {
            console.error('Failed to update smoothing:', error);
        }
    });
    
    sensitivitySlider.addEventListener('input', async (e) => {
        try {
            await fetch('/update-settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sensitivity: e.target.value
                })
            });
        } catch (error) {
            console.error('Failed to update sensitivity:', error);
        }
    });
    
    drawingEnabled.addEventListener('change', async (e) => {
        try {
            await fetch('/update-settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    drawingEnabled: e.target.checked
                })
            });
        } catch (error) {
            console.error('Failed to update drawing mode:', error);
        }
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === 'q' || e.key === 'Q') {
            stopBtn.click();
        } else if (e.key === 'm' || e.key === 'M') {
            minimizeBtn.click();
        }
    });
    
    // Initialize WebSocket connection
    connectWebSocket();
    
    // Initial state
    stopBtn.disabled = true;
});