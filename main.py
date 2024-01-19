import os
from time import sleep
from picamera2 import Picamera2, Preview
from flask import Flask, render_template_string, send_file, redirect, url_for
import cv2
import pytesseract
import numpy as np
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
import blinkt

# GLOBAL VARIABLES
picamera_image_path = os.getenv('PICAMERA_IMAGE_PATH', '/run/shm/watermeter_last.jpg')
picamera_config = os.getenv('PICAMERA_CONFIG', '{"size": (1000, 1000)}')
tesseract_path = os.getenv('TESSERACT_PATH', '/usr/bin/tesseract')
tesseract_config = os.getenv('TESSERACT_CONFIG', '--psm 6 -c tessedit_char_whitelist=0123456789')
watermeter_last_value_file = os.getenv('WATERMETER_LAST_VALUE_FILE', '/run/shm/watermeter_last_value.txt')
watermeter_preview_image_path = os.getenv('WATERMETER_PREVIEW_IMAGE_PATH', '/run/shm/watermeter_preview.jpg')
draw_rois = True
# Define the ROIs
rois = [
    (439, 388, 71, 102),
    (520, 388, 71, 102),
    (604, 381, 71, 102),
    (679, 374, 71, 102),
    (760, 374, 71, 102),
    (844, 371, 71, 102),
    (928, 368, 71, 102),
    (1015, 408, 71, 102),
    # Add more ROIs as needed
]
gauge_rois = [
    (967, 602, 265, 291),
    # Add more ROIs as needed
]
# CONFIGURATION
class Config(object):
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
    camera = Picamera2()
    #preview_config = camera.create_preview_configuration(main=picamera_config)
    #camera.configure(preview_config)
    # Turn on LED
    led_on()
    # Turn on Camera and allow to adjust to brightness
    #camera.start_preview(Preview.NULL)
    camera.start()
    sleep(1)
    # Take an image. I put in in /run/shm to not wear the SD card
    camera.capture_file(picamera_image_path)
    camera.close()
    led_off()
    return True

# READ IMAGE
def read_image():
    # Initialize an empty string to hold the digits
    digits = ''
    # Set the path to the tesseract executable
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    # Load the image from file
    image = cv2.imread(picamera_image_path)

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def read_digits():

        # Crop the image
        # Process each ROI
        for x, y, w, h in rois:
            # Crop the image
            roi = gray_image[y:y+h, x:x+w]

            # Use Tesseract to do OCR on the ROI
            digits += pytesseract.image_to_string(roi, config=tesseract_config)

            # Print the text
            print(digits)

        return(digits)

    def read_gauges():
        # Process each ROI
        for x, y, w, h in gauge_rois:
            # Crop the image to the ROI
            gauge_roi = gray_image[y:y+h, x:x+w]

            # Use edge detection and Hough line transformation to find the pointer
            edges = cv2.Canny(gauge_roi, 50, 150, apertureSize=3)
            lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

            # Find the line with the maximum y value, which should be the pointer
            max_y = -np.inf
            pointer_angle = 0
            if lines is not None:
                for rho, theta in lines[0]:
                    a = np.cos(theta)
                    b = np.sin(theta)
                    x0 = a * rho
                    y0 = b * rho
                    x1 = int(x0 + 1000 * (-b))
                    y1 = int(y0 + 1000 * (a))

                    if y1 > max_y:
                        max_y = y1
                        pointer_angle = np.arctan2(y2 - y1, x2 - x1)

            # Calculate the value indicated by the pointer
            value_range = 10  # The range of values on the gauge
            angle_range = np.pi  # The range of angles on the gauge (180 degrees)
            value = (pointer_angle / angle_range) * value_range
            digits += str(value)
        # Convert the digits string to an integer
        value = int(digits)
        return digits
    # Wire sensor data to file
    with open(watermeter_last_value_file, 'w') as f:
    	f.write(int(digits))
  
# Draw the ROIs on the image
def draw_rois():
    # Load the image
    with Image(filename=picamera_image_path) as img:
        # Create a Drawing object and set its properties
        with Drawing() as draw:
            draw.stroke_color = Color('red')
            draw.stroke_width = 2
            draw.fill_color = Color('transparent')

            # Draw each ROI
            for x, y, w, h in rois:
                draw.rectangle(left=x, top=y, width=w, height=h)

            for x, y, w, h in gauge_rois:
                draw.rectangle(left=x, top=y, width=w, height=h)

            # Overlay the ROIs onto the image
            draw(img)

        # Save the image
        img.save(filename=watermeter_preview_image_path)
    return True


# LOAD SENSOR DATA
def load_sensor_data():
    try:

        with open(watermeter_last_value_file, 'r') as f:
            sensor_data = str(f.read())
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

@app.route('/read_image')
def read_image():
    read_image = read_image()
    return read_image

@app.route('/take_new_picture', methods=['POST'])
def take_new_picture():
    take_picture()
    draw_rois()
    return redirect(url_for('preview'))

@app.route('/last_image')
def last_image():
    try:
        return send_file(watermeter_preview_image_path, mimetype='image/jpeg')
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
