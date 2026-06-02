import os
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from sender import send_log
from config import USERNAME, WATCH_DIRECTORY

# ===============================
# FILE FILTERS
# ===============================
IGNORED_EXTENSIONS = {
    ".tmp", ".swp", ".cache", ".log",
    ".bak", ".part", ".pyc"
}

IGNORED_DIRECTORIES = {
    ".git", "__pycache__", ".cache",
    ".config/google-chrome", ".mozilla", "node_modules"
}

THROTTLE_SECONDS = 2

# Map watchdog event types → anomaly_detector event types
# All mapped to types the detector actually checks
EVENT_TYPE_MAP = {
    "file_create": "file_modify",   # treated as a write-class event
    "file_modify": "file_modify",
    "file_delete": "file_delete",
    "file_move":   "file_modify",
    "file_access": "file_access",
}

# ===============================
# FILE HANDLER
# ===============================
class FileHandler(FileSystemEventHandler):

    def __init__(self):
        self.last_triggered = {}

    # ===============================
    # NORMALIZE PATH
    # ===============================
    def normalize_path(self, path):
        return os.path.abspath(path)

    # ===============================
    # SHOULD IGNORE
    # ===============================
    def should_ignore(self, path):
        normalized = self.normalize_path(path)
        filename = os.path.basename(normalized)

        if filename.startswith("."):
            return True

        _, ext = os.path.splitext(filename)
        if ext.lower() in IGNORED_EXTENSIONS:
            return True

        for ignored in IGNORED_DIRECTORIES:
            if ignored in normalized:
                return True

        return False

    # ===============================
    # THROTTLE
    # ===============================
    def should_throttle(self, path):
        normalized = self.normalize_path(path)
        now = time.time()

        if normalized in self.last_triggered:
            if (now - self.last_triggered[normalized]) < THROTTLE_SECONDS:
                return True

        self.last_triggered[normalized] = now

        # Cleanup stale entries to prevent memory growth
        if len(self.last_triggered) > 500:
            cutoff = now - THROTTLE_SECONDS * 10
            self.last_triggered = {
                k: v for k, v in self.last_triggered.items()
                if v > cutoff
            }

        return False

    # ===============================
    # SEND EVENT
    # ===============================
    def send_event(self, event_type, path, display_value=None):
        if self.should_ignore(path):
            return

        if self.should_throttle(path):
            return

        # Map to detector-compatible event type
        detector_event_type = EVENT_TYPE_MAP.get(event_type, event_type)

        send_log({
            "user":       USERNAME,
            "event_type": detector_event_type,
            "value":      display_value or self.normalize_path(path)
        })

        print(f"[FILE] {event_type.upper():<15} {display_value or path}")

    # ===============================
    # FILE CREATED
    # ===============================
    def on_created(self, event):
        if event.is_directory:
            return
        self.send_event("file_create", event.src_path)

    # ===============================
    # FILE MODIFIED
    # ===============================
    def on_modified(self, event):
        if event.is_directory:
            return
        self.send_event("file_modify", event.src_path)

    # ===============================
    # FILE DELETED
    # ===============================
    def on_deleted(self, event):
        if event.is_directory:
            return
        self.send_event("file_delete", event.src_path)

    # ===============================
    # FILE MOVED / RENAMED
    # Fix: pass src_path to ignore/throttle logic,
    # but send full move info as display value
    # ===============================
    def on_moved(self, event):
        if event.is_directory:
            return
        display = f"{event.src_path} -> {event.dest_path}"
        self.send_event("file_move", event.src_path, display_value=display)

# ===============================
# START MONITOR
# ===============================
def start_file_monitor():
    event_handler = FileHandler()
    observer = Observer()

    observer.schedule(
        event_handler,
        WATCH_DIRECTORY,
        recursive=True
    )

    observer.start()
    print(f"[FILE MONITOR] Watching: {WATCH_DIRECTORY}")
    return observer
