import subprocess
from sender import send_log
from config import USERNAME

def check_login():
    try:
        output = subprocess.check_output("who", shell=True).decode()
        for line in output.split("\n"):
            if line:
                data = {
                    "user": USERNAME,
                    "event_type": "login_activity",
                    "value": line
                }
                send_log(data)
    except:
        pass
