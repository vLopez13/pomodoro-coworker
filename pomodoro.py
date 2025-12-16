# pomodoro.py
from fastapi import FastAPI
from enum import Enum
import time

app = FastAPI()

class TimerState(str, Enum):
    WORK = "WORK"
    SHORT_BREAK = "SHORT_BREAK"
    LONG_BREAK = "LONG_BREAK"
    IDLE = "IDLE"

# Configuration (Seconds)
CONFIG = {
    TimerState.WORK: 60 * 60,         # 60 Minutes
    TimerState.SHORT_BREAK: 5 * 60,   # 5 Minutes
    TimerState.LONG_BREAK: 15 * 60    # 15 Minutes
}

current_session = {
    "state": TimerState.IDLE,
    "start_time": None,
    "end_time": None,
    "work_cycles_completed": 0
}
HTML_DASHBOARD = """
<!DOCTYPE html>
<html>
<head>
    <title>Pomodoro Garden</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=Quicksand:wght@400;600&display=swap');

        body {
            background-color: #fdf6f0; /* Creamy White */
            background-image: radial-gradient(#ffe4e1 20%, transparent 20%),
                              radial-gradient(#f0fff0 20%, transparent 20%);
            background-size: 50px 50px;
            background-position: 0 0, 25px 25px;
            font-family: 'Quicksand', sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            color: #5d5d5d;
        }

        .container {
            background: rgba(255, 255, 255, 0.9);
            padding: 40px 60px;
            border-radius: 30px;
            box-shadow: 0 10px 30px rgba(233, 189, 189, 0.4);
            text-align: center;
            border: 2px solid #ffe4e1;
            max-width: 400px;
        }

        h1 {
            font-family: 'Lora', serif;
            font-size: 2.5rem;
            color: #d48c98; /* Dusty Pink */
            margin: 0;
            font-style: italic;
        }

        .subtitle {
            font-size: 1rem;
            color: #88b04b; /* Sage Green */
            margin-bottom: 20px;
            letter-spacing: 2px;
            text-transform: uppercase;
        }

        #timer {
            font-size: 5rem;
            font-weight: 600;
            color: #5d5d5d;
            margin: 20px 0;
            font-variant-numeric: tabular-nums;
        }

        .button-group {
            display: flex;
            gap: 15px;
            justify-content: center;
        }

        button {
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-family: 'Quicksand', sans-serif;
            font-weight: bold;
            font-size: 1rem;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        button:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .btn-work {
            background-color: #ffb7b2; /* Salmon Pink */
            color: white;
        }

        .btn-break {
            background-color: #a8e6cf; /* Mint Green */
            color: #4a6fa5;
        }

        .btn-stop {
            background-color: #e2f0cb; /* Pastel Yellow/Green */
            color: #555;
        }

        .flower-decor {
            font-size: 2rem;
            margin-top: 20px;
            opacity: 0.8;
        }
        
        /* Floating animation for flowers */
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0px); }
        }
        .floating {
            display: inline-block;
            animation: float 3s ease-in-out infinite;
        }
    </style>
</head>
<body>

    <div class="container">
        <h1>Focus Garden</h1>
        <div id="status-text" class="subtitle">Ready to grow?</div>
        
        <div id="timer">00:00</div>
        
        <div class="button-group">
            <button class="btn-work" onclick="control('start')">🌸 Focus</button>
            <button class="btn-break" onclick="control('break')">☕ Rest</button>
            <button class="btn-stop" onclick="control('stop')">🍃 Stop</button>
        </div>

        <div class="flower-decor">
            <span class="floating" style="animation-delay: 0s;">🌷</span>
            <span class="floating" style="animation-delay: 1s;">✨</span>
            <span class="floating" style="animation-delay: 0.5s;">🌿</span>
        </div>
    </div>

    <script>
        async function control(action) {
            await fetch('/' + action, { method: 'POST' });
            updateStatus();
        }

        async function updateStatus() {
            const response = await fetch('/status');
            const data = await response.json();
            
            document.getElementById('timer').innerText = data.formatted_time;
            
            const statusLabel = document.getElementById('status-text');
            const body = document.body;
            
            // Dynamic Aesthetics
            if(data.state === "WORK") {
                statusLabel.innerText = "Growing Time...";
                statusLabel.style.color = "#ff6f61"; // Coral
            } else if(data.state.includes("BREAK")) {
                statusLabel.innerText = "Blossoming Break";
                statusLabel.style.color = "#4a90e2"; // Blue
            } else {
                statusLabel.innerText = "Garden is Sleeping";
                statusLabel.style.color = "#88b04b"; // Sage
            }
        }

        setInterval(updateStatus, 1000);
        updateStatus();
    </script>
</body>
</html>
"""
@app.get("/")
def home():
    return {"message": "Focus Timer API is Running"}

@app.post("/start-work")
def start_work():
    current_session["state"] = TimerState.WORK
    current_session["start_time"] = time.time()
    current_session["end_time"] = time.time() + CONFIG[TimerState.WORK]
    current_session["work_cycles_completed"] = 0
    return {"status": "Work session started", "duration_minutes": 60}

@app.get("/status")
def get_status():
    """Check how much time is left and what the current state is."""
    if current_session["state"] == TimerState.IDLE:
        return {"state": "IDLE", "time_left": 0}

    time_left = current_session["end_time"] - time.time()
    
    # If time is up, rotate the state automatically
    if time_left <= 0:
        return handle_timer_expiry()

    return {
        "state": current_session["state"],
        "time_left_seconds": int(time_left),
        "formatted_time": f"{int(time_left // 60)}:{int(time_left % 60):02d}"
    }

def handle_timer_expiry():
    """Logic to rotate breaks automatically."""
    prev_state = current_session["state"]
    
    # If we just finished working, determine which break to take
    if prev_state == TimerState.WORK:
        current_session["work_cycles_completed"] += 1
        
        # Every 4th work cycle (just an example) could be a long break, 
        # or stick to your logic: alternating.
        # Your logic: If cycles is even number -> Long Break
        if current_session["work_cycles_completed"] % 2 == 0:
             next_state = TimerState.LONG_BREAK
        else:
             next_state = TimerState.SHORT_BREAK
    
    # If we just finished a break, go back to work
    else:
        next_state = TimerState.WORK

    # Set new timers
    current_session["state"] = next_state
    current_session["start_time"] = time.time()
    current_session["end_time"] = time.time() + CONFIG[next_state]
    
    return {
        "alert": "TIMER_FINISHED",
        "next_state": next_state,
        "message": f"Switched to {next_state}"
    }