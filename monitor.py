import pygetwindow as gw 
import requests 
import tkinter as tk
import time

API_URL ="http://127.0.0.1:8000/status"
GRACE_PERIOD_SECS = 10 
BLACKLIST = [
    "YouTube", 
    "Instagram", 
    "Facebook", 
    "TikTok", 
    "Netflix", 
    "Hulu", 
    "Disney+", 
    "Prime Video",  
    "Reddit", 
    " / X ",        
    " on X ",       
    "Twitter"       
]
class HUDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro BOT")
        self.is_blocking = False

        self.violation_start_time = None
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.bg_color_work = "#468347"   # Green  (FOCUS WORK!)
        self.bg_color_break = "#9b59b6"  # Purple (SET BREAK)
        self.bg_color_block = "#5c5c5c"  # Grey block (DISTRACTED!)
        self.bg_color_warning = "#f85205" # OrangeRED (WARNING!)

        self.label_time = tk.Label(
            root, text="Loading...", font=("Times Roman", 24, "bold"),
            bg=self.bg_color_work, fg="white", padx=20, pady=10
        )
        self.label_time.pack(expand=True, fill='both')
        self.btn_unlock = tk.Button(
            root, text="I PROMISE TO WORK", font=("Times Roman", 14, "bold"),
            command=self.reset_to_work, bg="white", fg="black"
        )
        
        # Start in Mini Mode
        self.mode_mini_timer()
        self.check_status()

    def mode_mini_timer(self):
        """Sets window to a small HUD box."""
        self.is_blocking = False
        self.btn_unlock.pack_forget()
        self.violation_start_time = None 
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 220
        window_height = 60
        
        x_pos = screen_width - window_width - 20
        y_pos = screen_height - window_height - 50
        self.root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
        self.label_time.config(font=("Helvetica", 20, "bold"), wraplength=0)

    def mode_full_block(self, app_name):
        """Sets window to full screen blockage."""
        if self.is_blocking:
            return 
            
        self.is_blocking = True
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        self.root.configure(bg=self.bg_color_block)
        self.label_time.config(
            text=f" ACCESS DENIED!!\n\nYou are on {app_name}\nGet back to work!",
            bg=self.bg_color_block, 
            fg="#f85205",
            font=("Times Roman", 40, "bold"),
            wraplength=800
        )
        self.btn_unlock.pack(pady=50)
    
    def reset_to_work(self):
        """User clicked the promise button."""
        self.mode_mini_timer()
    def check_status(self):
        try:
            try:
                response = requests.get(API_URL, timeout=0.5)
                data = response.json()
                state = data.get("state", "IDLE")
                formatted_time = data.get("formatted_time", "00:00")
            except:
                state = "OFFLINE"
                formatted_time = "--:--"

            violation_found = None
            
            if state == "WORK":
                active_window = gw.getActiveWindow()
                if active_window:
                    title = active_window.title
                    violation_found = next((site for site in BLACKLIST if site.lower() in title.lower()), None)

            if violation_found:
                if self.violation_start_time is None:
                    
                    self.violation_start_time = time.time()
                
              
                elapsed = time.time() - self.violation_start_time
                remaining_grace = GRACE_PERIOD_SECS - elapsed

                if remaining_grace <= 0:
                    self.mode_full_block(violation_found)
                elif not self.is_blocking:
                    self.label_time.config(
                        bg=self.bg_color_warning, 
                        text=f"ohno {int(remaining_grace)}s..."
                    )
                    self.root.configure(bg=self.bg_color_warning)
            
            else:
                self.violation_start_time = None 

                if not self.is_blocking:
                    if state == "WORK":
                        self.label_time.config(bg=self.bg_color_work, text=f"🍅 {formatted_time}")
                        self.root.configure(bg=self.bg_color_work)
                    elif "BREAK" in state:
                        self.label_time.config(bg=self.bg_color_break, text=f"☕ {formatted_time}")
                        self.root.configure(bg=self.bg_color_break)
                    else:
                        self.label_time.config(bg="#7f8c8d", text=f"💤 {formatted_time}")
                        self.root.configure(bg="#7f8c8d")

        except Exception as e:
            print(f"Error: {e}")  

        self.root.after(1000, self.check_status)

if __name__ == "__main__":
    root = tk.Tk()
    app = HUDApp(root)
    root.mainloop()  



