import subprocess
import os
from sender import send_log
from config import USERNAME

# ===============================
# LOG FILE SELECTION
# ===============================
AUTH_LOG_PATHS = [
    "/var/log/auth.log",   # Ubuntu/Debian
    "/var/log/secure"      # RHEL/CentOS
]

LOG_FILE = None
for path in AUTH_LOG_PATHS:
    if os.path.exists(path):
        LOG_FILE = path
        break

if LOG_FILE is None:
    raise Exception("No auth log file found")

# ===============================
# STATE TRACKING
# Persist last file position across calls to avoid
# re-processing old lines on each check_login() call.
# ===============================
last_seen_sessions = set()
seen_failed_lines  = set()

# Seek to end of log on startup so we only process NEW lines
with open(LOG_FILE, "r") as _f:
    _f.seek(0, 2)
    last_position = _f.tell()

# ===============================
# SUCCESSFUL LOGINS
# ===============================
def check_successful_logins():
    global last_seen_sessions

    try:
        output = subprocess.check_output("who", shell=True).decode().strip()
        current_sessions = set()

        for line in output.split("\n"):
            if not line.strip():
                continue

            parts = line.split()
            if len(parts) < 5:
                continue

            actual_user = parts[0]
            terminal   = parts[1]
            login_time = " ".join(parts[2:5])
            session_id = f"{actual_user}:{terminal}:{login_time}"

            current_sessions.add(session_id)

        new_sessions = current_sessions - last_seen_sessions

        for session in new_sessions:
            # Always use USERNAME from config so it matches the baseline key.
            # actual_user from 'who' may differ (e.g. root vs configured user).
            send_log({
                "user":       USERNAME,
                "event_type": "login_activity",
                "value": {
                    "type":    "login_success",
                    "session": session
                }
            })
            print(f"[LOGIN] Success: {session}")

        last_seen_sessions = current_sessions

    except Exception as e:
        print(f"[LOGIN ERROR] success check: {e}")

# ===============================
# FAILED LOGINS
# ===============================
def check_failed_logins():
    global last_position, seen_failed_lines

    try:
        with open(LOG_FILE, "r") as f:
            f.seek(last_position)
            lines = f.readlines()
            last_position = f.tell()

        for line in lines:
            line_lower = line.lower()

            if not (
                "failed password"        in line_lower or
                "authentication failure" in line_lower or
                "failed login"           in line_lower
            ):
                continue

            line_hash = hash(line)

            if line_hash in seen_failed_lines:
                continue

            seen_failed_lines.add(line_hash)

            send_log({
                "user":       USERNAME,
                "event_type": "failed_login",
                "value": {
                    "type": "login_failure",
                    "raw":  line.strip()
                }
            })
            print("[LOGIN] Failed attempt detected")

        # Prevent seen_failed_lines from growing forever
        if len(seen_failed_lines) > 1000:
            seen_failed_lines.clear()

    except Exception as e:
        print(f"[LOGIN ERROR] failed check: {e}")

# ===============================
# MAIN FUNCTION
# ===============================
def check_login():
    check_successful_logins()
    check_failed_logins()

# ===============================
# RUN DIRECTLY
# ===============================
if __name__ == "__main__":
    import time
    while True:
        check_login()
        time.sleep(5)
