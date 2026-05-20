from pynput import mouse
from sender import send_log
from config import USERNAME
import time

click_count = 0
move_count = 0

def on_click(x, y, button, pressed):
    global click_count
    if pressed:
        click_count += 1

def on_move(x, y):
    global move_count
    move_count += 1

def start_listener():
    listener = mouse.Listener(on_click=on_click, on_move=on_move)
    listener.start()

def report_activity():
    global click_count, move_count

    while True:
        time.sleep(10)

        send_log({
            "user": USERNAME,
            "event_type": "mouse_activity",
            "value": f"clicks:{click_count},moves:{move_count}"
        })

        click_count = 0
        move_count = 0
