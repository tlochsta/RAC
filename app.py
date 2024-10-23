import os
import platform
import subprocess
import cv2
import pyautogui
import numpy as np
from flask import Flask, render_template, request, send_file, jsonify, Response
from PIL import ImageGrab

app = Flask(__name__)


# RAC Configuration

port = 5000
debugMode = True
webhost = '0.0.0.0'

# End RAC Configuration

@app.route('/')
def home():
    return render_template('rac.html')

@app.route('/shutdown', methods=['POST'])
def shutdown():
    if platform.system() == 'Windows':
        os.system('shutdown /s /t 1')
    elif platform.system() == 'Linux':
        os.system('shutdown now')
    return "Shutting down..."

@app.route('/restart', methods=['POST'])
def restart():
    if platform.system() == 'Windows':
        os.system('shutdown /r /t 1')
    elif platform.system() == 'Linux':
        os.system('reboot')
    return "Restarting..."

@app.route('/lock', methods=['POST'])
def lock():
    if platform.system() == 'Windows':
        os.system('rundll32.exe user32.dll,LockWorkStation')
    elif platform.system() == 'Linux':
        os.system('gnome-screensaver-command -l')
    return "Locking system..."

@app.route('/screenshot', methods=['POST'])
def screenshot():
    screenshot = ImageGrab.grab()
    screenshot.save("screenshot.png")
    return send_file("screenshot.png", mimetype='image/png')

@app.route('/run-command', methods=['POST'])
def run_command():
    data = request.get_json()
    command = data['command']
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        return output
    except subprocess.CalledProcessError as e:
        return str(e.output)
@app.route('/video_feed')
def video_feed():
    return Response(generate_live_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_live_feed():
    while True:
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

if __name__ == '__main__':
    app.run(host=webhost, port=port, debug=debugMode)
