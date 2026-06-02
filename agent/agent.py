import time
import threading
import signal
import sys

from login_monitor   import check_login
from process_monitor import check_processes
from network_monitor import check_connections
from file_monitor    import start_file_monitor
from config          import CHECK_INTERVAL

# ===============================
# START FILE OBSERVER
# ===============================
observer = start_file_monitor()

# ===============================
# GRACEFUL SHUTDOWN
# ===============================
def shutdown(signum, frame):
    print("\n[AGENT] Shutting down...")
    observer.stop()
    observer.join()
    sys.exit(0)

signal.signal(signal.SIGINT,  shutdown)
signal.signal(signal.SIGTERM, shutdown)

# ===============================
# RUN A MONITOR IN ITS OWN THREAD
# so a slow/hung check doesn't block the others
# ===============================
def run_threaded(target, label):
    def wrapper():
        try:
            target()
        except Exception as e:
            print(f"[{label} ERROR] {e}")
    t = threading.Thread(target=wrapper, daemon=True)
    t.start()
    return t

# ===============================
# MAIN LOOP
# ===============================
print("[AGENT] Monitoring started.")

while True:
    threads = [
        run_threaded(check_login,       "LOGIN"),
        run_threaded(check_processes,   "PROCESS"),
        run_threaded(check_connections, "NETWORK"),
    ]

    # Wait for all monitors to finish before sleeping,
    # but cap the wait so a hung thread doesn't stall the loop
    for t in threads:
        t.join(timeout=CHECK_INTERVAL * 0.8)

    time.sleep(CHECK_INTERVAL)
