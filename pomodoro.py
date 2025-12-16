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