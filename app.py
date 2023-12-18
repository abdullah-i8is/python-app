from flask import Flask, jsonify, render_template
from flask_cors import CORS
from pynput import mouse, keyboard
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import win32gui

app = Flask(__name__)
CORS(app)

lock = threading.Lock()
activityIncrement = 0
active_window_name = ""

def increment_activity():
    global activityIncrement
    current_activity_increment = activityIncrement
    activityIncrement = 0
    return current_activity_increment

def get_active_window_name():
    global active_window_name
    try:
        active_window_handle = win32gui.GetForegroundWindow()
        active_window_name = win32gui.GetWindowText(active_window_handle)
    except Exception as e:
        active_window_name = ""

def on_mouse_activity(x, y, button, pressed):
    with lock:
        global activityIncrement
        activityIncrement += 1
        get_active_window_name()

def on_mouse_move(x, y):
    with lock:
        global activityIncrement
        activityIncrement += 1
        get_active_window_name()

def on_keyboard_activity(key):
    with lock:
        global activityIncrement
        activityIncrement += 1
        get_active_window_name()

mouse_listener = mouse.Listener(on_click=on_mouse_activity)
keyboard_listener = keyboard.Listener(on_press=on_keyboard_activity)

# Add on_move handler for mouse move activity
mouse_listener.on_move = on_mouse_move

def reset_activity_count():
    while True:
        time.sleep(10)  # Adjust the time interval as needed
        with lock:
            increment_activity()

def run_listeners():
    mouse_listener.start()
    keyboard_listener.start()

    # Schedule active window name check every 2 seconds
    threading.Timer(2.0, get_active_window_name).start()

    # Start the thread to reset activity count
    threading.Thread(target=reset_activity_count).start()

@app.route('/get-activity', methods=['GET'])
def get_activity():
    with lock:
        current_activity_increment = increment_activity()

    total_possible_events = 10000  # Arbitrary number for total possible events
    activity_percentage = (current_activity_increment / total_possible_events) * 100

    return jsonify({"percentage": activity_percentage, "active_window_name": active_window_name})

@app.route('/')
def runHtm():
    return render_template("index.html")
if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(run_listeners)
        app.run(port=5000)
