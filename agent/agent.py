import time
import os
import threading

from login_monitor import check_login
from process_monitor import check_processes
from network_monitor import check_connections
from file_monitor import start_file_monitor
from config import CHECK_INTERVAL

observer = start_file_monitor()

if os.environ.get("DISPLAY"):
    from mouse_monitor import report_activity
    import threading
    threading.Thread(target=report_activity, daemon=True).start()

while True:
    check_login()
    check_processes()
    check_connections()
    time.sleep(CHECK_INTERVAL)
