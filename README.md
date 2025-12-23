# YOUR WORK POMODORO TIMER AND PARTNER

A Python-based productivity tool that acts as your "Digital Accountability Co-worker." It combines a Pomodoro timer API with a screen-monitoring "Bouncer" that physically blocks your screen if you visit some distracting websites such as Facebook, Youtube, Tiktok, or anything deemed entertainment during your peak work hours.

HOW IT WORKS ---> The Brain (`pomodoro.py`):  IT IS A FastAPI backend that manages Pomodoro states such as: Work, Short Break, Long Break Time.
AGENT BOT JUMPS IN NAMED: The Bouncer (`bouncer.py`): THIS happens in the background a process that monitors your active window titles, and area of work.
   - If you are in "Work Mode" and open a black-listed site (YouTube, TikTok, etc.), a full-screen overlay blocks your view.
   - You must click "I PROMISE TO GO BACK TO WORK" to dismiss it.
   - It intelligently detects browser tabs (e.g., PRIME VIDEO AMAZON, OUTLOOK, DOCS GOOGLE)

## HOW TO DO Installation

1. Clone the repo:
   ```bash
   git clone [https://github.com/vLopez13/pomodoro-coworker.git](https://github.comvLopez13/pomodoro-coworker.git)
   <div align="center">
  <img src="/Animation.gif" width="600" alt="Project Demo">
  <p><i>A short description of what is happening in this demo.</i></p>
</div>
