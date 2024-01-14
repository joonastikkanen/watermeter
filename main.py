import os
from time import sleep
from picamera2 import Picamera2, Preview
from flask import Flask, render_template_string, send_file, redirect, url_for
import cv2
import pytesseract

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

    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app

app = create_app()

# TAKE PICTURE
def take_picture():
    picamera_config = app.config['PICAMERA_CONFIG']
    picamera_image_path = app.config['PICAMERA_IMAGE_PATH']
    camera = Picamera2()
    preview_config = camera.create_preview_configuration(main=picamera_config)
    camera.configure(preview_config)
    # Turn on LED
    #led.on()
    # Turn on Camera and allow to adjust to brightness
    camera.start_preview(Preview.NULL)
    camera.start()
    sleep(1)
    # Take an image. I put in in /run/shm to not wear the SD card
    camera.capture_file(picamera_image_path)
    camera.close()
    #led.off()
    return True

# READ IMAGE
def read_image():
    tesseract_path = app.config['TESSERACT_PATH']
    tesseract_config = app.config['TESSERACT_CONFIG']
    picamera_image_path = app.config['PICAMERA_IMAGE_PATH']
    watermeter_last_value_file = app.config['WATERMETER_LAST_VALUE_FILE']
    # Set the path to the tesseract executable
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    # Load the image from file
    image = cv2.imread(picamera_image_path)

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use Tesseract to do OCR on the image
    sensor_data = pytesseract.image_to_string(gray_image, config=tesseract_config)
    # Wire sensor data to file
    with open(watermeter_last_value_file, 'w') as f:
        f.write(str(sensor_data))

    # Print the text
    print(sensor_data)
    return sensor_data

# LOAD SENSOR DATA
def load_sensor_data():
    watermeter_last_value_file = app.config['WATERMETER_LAST_VALUE_FILE']
    try:
        with open(watermeter_last_value_file, 'r') as f:
            sensor_data = int(f.read())
    except FileNotFoundError:
        print(f"Info: The last value file {watermeter_last_value_file} is not found. Running reader function.")
        take_picture()
        read_image()

    return sensor_data

# ROUTES
@app.route('/')
def home():
    sensor_data = load_sensor_data()
    return sensor_data

@app.route('/take_new_picture', methods=['POST'])
def take_new_picture():
    take_picture()
    return redirect(url_for('preview'))

@app.route('/last_image')
def last_image():
    picamera_image_path = app.config['picamera_image_path']
    try:
        return send_file(picamera_image_path, mimetype='image/jpeg')
    except FileNotFoundError:
        return "No image found", 404

@app.route('/preview')
def preview():
    take_picture()
    read_image()
    try:
        return render_template_string("""
            <img src="{{ url_for('last_image') }}" alt="Last image">
            <form action="{{ url_for('take_new_picture') }}" method="post">
                <button type="submit">Take New Picture</button><br>
                Sensor data: {{ url_for('root') }}
            </form>
        """)
    except FileNotFoundError:
        return "No image found", 404
