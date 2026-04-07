from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sender import send_log
from config import USERNAME, WATCH_DIRECTORY

class FileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
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
