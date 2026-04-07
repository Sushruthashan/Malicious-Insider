import time
from login_monitor import check_login
from process_monitor import check_processes
from network_monitor import check_connections
from file_monitor import start_file_monitor
from config import CHECK_INTERVAL

observer = start_file_monitor()

while True:
    check_login()
    check_processes()
    check_connections()
    time.sleep(CHECK_INTERVAL)
