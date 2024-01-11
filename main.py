#!/usr/bin/python3
from time import sleep
from picamera2 import Picamera2, Preview
from libcamera import controls
from flask import Flask, send_file, render_template_string, url_for, redirect
import cv2
import pytesseract
import requests
import os

picamera_image_path = os.getenv('PICAMERA_IMAGE_PATH', '/run/shm/watermeter_last.jpg')
picamera_config = os.getenv('PICAMERA_CONFIG', '{"size": (1920, 1080)}')
tesseract_path = os.getenv('TESSERACT_PATH', '/usr/bin/tesseract')
tesseract_config = os.getenv('TESSERACT_CONFIG', '--psm 6 -c tessedit_char_whitelist=0123456789')
watermeter_last_value_file = os.getenv('WATERMETER_LAST_VALUE_FILE', '/run/shm/watermeter_last_value.txt')

def check_tesseract_exists():
    if not os.path.isfile(tesseract_path):
        print(f"Error: The tesseract binary at {tesseract_path} does not exist.")

# Call the function
check_tesseract_exists()

def load_sensor_data():
    try:
        with open(watermeter_last_value_file, 'r') as f:
            sensor_data = int(f.read())
    except FileNotFoundError:
        print(f"Info: The last value file {watermeter_last_value_file} is not found. Defaulting sensor_data to 0.")
        sensor_data = 0

    return sensor_data

def take_picture():
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
    metadata = camera.capture_file(picamera_image_path)
    camera.close()
    #led.off()
    return True

def read_image():
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

def main():
    sensor_data = load_sensor_data()
    take_picture()
    read_image()

app = Flask(__name__)

@app.route('/')
def root():
    sensor_data = load_sensor_data()
    return f"Sensor data: {sensor_data}"

@app.route('/preview')
def preview():
    take_picture()
    try:
        return render_template_string("""
            <img src="{{ url_for('last_image') }}" alt="Last image">
            <form action="{{ url_for('take_new_picture') }}" method="post">
                <button type="submit">Take New Picture</button>
            </form>
        """)
    except FileNotFoundError:
        return "No image found", 404

@app.route('/take_new_picture', methods=['POST'])
def take_new_picture():
    take_picture()
    return redirect(url_for('preview'))

@app.route('/last_image')
def last_image():
    try:
        return send_file(picamera_image_path, mimetype='image/jpeg')
    except FileNotFoundError:
        return "No image found", 404

if __name__ == '__main__':
    main()
    app.run(host='0.0.0.0', port=5000)