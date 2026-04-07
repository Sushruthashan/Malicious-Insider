import psutil
from sender import send_log
from config import USERNAME

SUSPICIOUS = ["scp", "ftp", "wget", "curl", "zip", "tar"]

def check_processes():
    for proc in psutil.process_iter(['name']):
        try:
            name = proc.info['name']
            if name in SUSPICIOUS:
                data = {
                    "user": USERNAME,
                    "event_type": "suspicious_process",
                    "value": name
                }
                send_log(data)
        except:
            pass
