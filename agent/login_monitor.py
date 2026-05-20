import subprocess
import time
from sender import send_log
from config import USERNAME

LOG_FILE = "/var/log/auth.log"

# Track sessions
last_seen_sessions = set()

# Track file read position
last_position = 0


def check_successful_logins():
    global last_seen_sessions
    try:
        output = subprocess.check_output("who", shell=True).decode().strip()
        current_sessions = set(line.strip() for line in output.split("\n") if line)

        new_sessions = current_sessions - last_seen_sessions

        for session in new_sessions:
            actual_sys_user = session.split()[0]

            data = {
                "user": actual_sys_user,  # 🔥 FIXED (no more constant employee1)
                "event_type": "login_activity",
                "value": f"Session started: {session}"
            }

            send_log(data)
            print(f"[LOGIN] Success: {actual_sys_user}")

        last_seen_sessions = current_sessions

    except Exception as e:
        print(f"Login monitor error (success): {e}")


def check_failed_logins():
    global last_position

    try:
        with open(LOG_FILE, "r") as f:
            f.seek(last_position)
            lines = f.readlines()
            last_position = f.tell()

        for line in lines:
            if "Failed password" in line:
                data = {
                    "user": USERNAME,
                    "event_type": "failed_login",
                    "value": line.strip()
                }

                send_log(data)
                print("[LOGIN] Failed attempt detected")

    except Exception as e:
        print(f"Login monitor error (failed): {e}")


def check_login():
    check_successful_logins()
    check_failed_logins()


if __name__ == "__main__":
    while True:
        check_login()
        time.sleep(5)
