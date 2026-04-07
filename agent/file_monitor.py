import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sender import send_log
from config import USERNAME, WATCH_DIRECTORY

class FileHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_triggered = {}

    def should_throttle(self, path):
        """Prevents duplicate logs for the same file within 1 second."""
        now = time.time()
        if path in self.last_triggered and (now - self.last_triggered[path] < 1):
            return True
        self.last_triggered[path] = now
        return False

    def on_modified(self, event):
        if not event.is_directory:
            # Ignore common temp/hidden files
            if any(x in event.src_path for x in ['.tmp', '.swp', '~', '.git']):
                return
            
            if self.should_throttle(event.src_path):
                return

            data = {
                "user": USERNAME,
                "event_type": "file_modified",
                "value": event.src_path
            }
            send_log(data)

    def on_created(self, event):
        if not event.is_directory:
            data = {
                "user": USERNAME,
                "event_type": "file_created",
                "value": event.src_path
            }
            send_log(data)

def start_file_monitor():
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIRECTORY, recursive=True)
    observer.start()
    return observer
