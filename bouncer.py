import time
import pygetwindow as gw
import requests
import tkinter as tk
from threading import Thread

# --- CONFIGURATION ---
API_URL = "http://127.0.0.1:8000/status"

# The "Forbidden Zones"
BLACKLIST = [
    "YouTube", 
    "Instagram", 
    "Facebook", 
    "TikTok", 
    "Netflix", 
    "Hulu", 
    "Disney+", 
    "Prime Video",  # Amazon Prime often uses this
    "Reddit", 
    " / X ",        # Catches "Home / X" 
    " on X ",       # Catches "Post on X"
    "Twitter"       # Many windows still say Twitter
]

# State variable to track if bouncer is currently active
bouncer_active = False
root = None  # To hold the tkinter window

def show_bouncer_overlay(app_name):
    """
    Creates a full-screen window that acts as the 'Bouncer'.
    It forces the user to acknowledge they are off-task.
    """
    global bouncer_active, root
    
    if bouncer_active:
        return

    bouncer_active = True
    
    # Create the blocking window
    root = tk.Tk()
    root.title("SECURITY BOUNCER")
    
    # Make it full screen and always on top
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.configure(bg="black")

    # The "Actor" Text
    label_title = tk.Label(
        root, 
        text="⛔ ACCESS DENIED ⛔", 
        font=("Helvetica", 40, "bold"), 
        fg="red", 
        bg="black"
    )
    label_title.pack(pady=(200, 20))

    label_msg = tk.Label(
        root, 
        text=f"I see you are on {app_name}.\nThis is not authorized work behavior.", 
        font=("Helvetica", 20), 
        fg="white", 
        bg="black"
    )
    label_msg.pack(pady=20)

    # Button to dismiss (The promise to go back to work)
    btn = tk.Button(
        root, 
        text="I WILL GO BACK TO WORK", 
        font=("Helvetica", 15, "bold"), 
        bg="white", 
        fg="black",
        command=close_bouncer
    )
    btn.pack(pady=50)

    # Start the GUI loop
    root.mainloop()

def close_bouncer():
    """Closes the overlay."""
    global bouncer_active, root
    if root:
        root.destroy()
    bouncer_active = False

def monitor_loop():
    """
    Background thread that constantly checks what the user is doing.
    """
    print("👀 WORK BESTIE is watching...")
    
    while True:
        try:
            # 1. Ask API: Are we in a WORK session?
            try:
                response = requests.get(API_URL)
                state_data = response.json()
                is_work_time = state_data.get("state") == "WORK"
            except:
                # If API is down, assume we are NOT working to avoid annoying blocks
                is_work_time = False

            if is_work_time:
                # 2. Check the active window title
                active_window = gw.getActiveWindow()
                if active_window:
                    title = active_window.title
                    
                    # 3. Check against the Blacklist
                    # We check if any 'bad word' is in the window title
                    violation = next((site for site in BLACKLIST if site.lower() in title.lower()), None)
                    
                    if violation:
                        print(f"🚨 VIOLATION DETECTED: {violation}")
                        if not bouncer_active:
                            pass 

                        if not bouncer_active:
                            show_bouncer_overlay(violation)

            time.sleep(2) # Check every 2 seconds

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # We run the monitor logic in a separate thread so the GUI doesn't freeze
    # However, Tkinter must run in the main thread.
    
    # So we reverse it: Monitor runs in background thread, Tkinter runs in main.
    monitor_thread = Thread(target=monitor_loop)
    monitor_thread.daemon = True # Kills thread when app closes
    monitor_thread.start()
    
    # Keep the main script alive to allow the thread to run
    # and to handle the Tkinter loop when it pops up
    while True:
        time.sleep(1)