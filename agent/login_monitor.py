import subprocess
import time
from sender import send_log
from config import USERNAME

# Track sessions to avoid duplicate logs
last_seen_sessions = set()

def check_login():
    global last_seen_sessions
    try:
        # 'who' shows current users. 'last -1' could also be used for the very latest.
        output = subprocess.check_output("who", shell=True).decode().strip()
        current_sessions = set(line.strip() for line in output.split("\n") if line)

        # Find only the NEW sessions
        new_sessions = current_sessions - last_seen_sessions

        for session in new_sessions:
            # We use the actual username from the system log, 
            # or your USERNAME from config if you want to override it.
            actual_sys_user = session.split()[0] 
            
            data = {
                "user": USERNAME, # Or use actual_sys_user
                "event_type": "login_activity",
                "value": f"Session started: {session}"
            }
            send_log(data)
            print(f"[SENSOR] New login detected: {actual_sys_user}")

        last_seen_sessions = current_sessions
    except Exception as e:
        print(f"Login monitor error: {e}")

if __name__ == "__main__":
    while True:
        check_login()
        time.sleep(10) # Check every 10 seconds
