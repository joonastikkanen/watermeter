import os
from time import sleep
from picamera2 import Picamera2, Preview
from flask import Flask, render_template_string, send_file, redirect, url_for
import cv2
import pytesseract
import blinkt

# CONFIGURATION
class Config(object):
    PICAMERA_IMAGE_PATH = os.getenv('PICAMERA_IMAGE_PATH', '/run/shm/watermeter_last.jpg'),
    PICAMERA_CONFIG = os.getenv('PICAMERA_CONFIG', '{"size": (1920, 1080)}'),
    TESSERACT_PATH = os.getenv('TESSERACT_PATH', '/usr/bin/tesseract'),
    TESSERACT_CONFIG = os.getenv('TESSERACT_CONFIG', '--psm 6 -c tessedit_char_whitelist=0123456789'),
    WATERMETER_LAST_VALUE_FILE = os.getenv('WATERMETER_LAST_VALUE_FILE', '/run/shm/watermeter_last_value.txt'),
    DEBUG = False

# APP
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    return app

app = create_app()

# LED ON
def led_on():
    blinkt.set_clear_on_exit(False)
    blinkt.set_all(255, 255, 255, 1.0)
    blinkt.show()

# LED OFF
def led_off():
    blinkt.clear()
    blinkt.show()

# TAKE PICTURE
def take_picture():
    PICAMERA_CONFIG = app.config['PICAMERA_CONFIG']
    PICAMERA_IMAGE_PATH = app.config['PICAMERA_IMAGE_PATH']
    camera = Picamera2()
    preview_config = camera.create_preview_configuration(main=PICAMERA_CONFIG)
    camera.configure(PICAMERA_CONFIG)
    # Turn on LED
    led_on
    # Turn on Camera and allow to adjust to brightness
    camera.start_preview(Preview.NULL)
    camera.start()
    sleep(1)
    # Take an image. I put in in /run/shm to not wear the SD card
    camera.capture_file(PICAMERA_IMAGE_PATH)
    camera.close()
    led_off
    return True

# READ IMAGE
def read_image():
    TESSERACT_PATH = app.config['TESSERACT_PATH']
    TESSERACT_CONFIG = app.config['TESSERACT_CONFIG']
    PICAMERA_IMAGE_PATH = app.config['PICAMERA_IMAGE_PATH']
    WATERMETER_LAST_VALUE_FILE = app.config['WATERMETER_LAST_VALUE_FILE']
    # Set the path to the tesseract executable
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

    # Load the image from file
    image = cv2.imread(PICAMERA_IMAGE_PATH)

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use Tesseract to do OCR on the image
    sensor_data = pytesseract.image_to_string(gray_image, config=tesseract_config)
    # Wire sensor data to file
    with open(WATERMETER_LAST_VALUE_FILE, 'w') as f:
        f.write(str(sensor_data))

    # Print the text
    print(sensor_data)
    return sensor_data

# LOAD SENSOR DATA
def load_sensor_data():
    WATERMETER_LAST_VALUE_FILE = app.config['WATERMETER_LAST_VALUE_FILE']
    try:

        with open(WATERMETER_LAST_VALUE_FILE, 'r') as f:
            sensor_data = int(f.read())
    except FileNotFoundError:
        print(f"Info: The last value file {WATERMETER_LAST_VALUE_FILE} is not found. Running reader function.")
        take_picture()
        read_image()

    return sensor_data

# ROUTES
@app.route('/')
def home():
    sensor_data = load_sensor_data()
    return sensor_data

@app.route('/read_image')
def read_image():
    read_image = read_image()
    return read_image

@app.route('/take_new_picture', methods=['POST'])
def take_new_picture():
    take_picture()
    return redirect(url_for('preview'))

@app.route('/last_image')
def last_image():
    PICAMERA_IMAGE_PATH = app.config['PICAMERA_IMAGE_PATH']
    try:
        return send_file(PICAMERA_IMAGE_PATH, mimetype='image/jpeg')
    except FileNotFoundError:
        return "No image found", 404

@app.route('/preview')
def preview():
    try:
        return render_template_string("""
            <img src="{{ url_for('last_image') }}" alt="Last image">
            <form action="{{ url_for('take_new_picture') }}" method="post">
                <button type="submit">Take New Picture</button><br>
                Sensor data: {{ url_for('home') }} <br><br>
                <a href="read_image">Read Image</a><br>
            </form>
        """)
    except FileNotFoundError:
        return "No image found", 404
