import yaml
from time import sleep
from picamera2 import Picamera2
from flask import Flask, send_file, redirect, url_for, request, render_template
import cv2
import pytesseract
import numpy as np
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
import blinkt

# LOAD CONFIG FILE
def load_config():
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    return config

config = load_config()
# Convert the lists to tuples
gauge_rois = config['gauge_rois'] = [tuple(roi) for roi in config['gauge_rois']]
picamera_image_path = config['picamera_image_path']
picamera_config = config['picamera_config']
rois = config['rois'] = [tuple(roi) for roi in config['rois']]
tesseract_path = config['tesseract_path']
tesseract_config = config['tesseract_config']
watermeter_last_value_file = config['watermeter_last_value_file']
watermeter_preview_image_path = config['watermeter_preview_image_path']

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
    # Turn on LED
    led_on()
    # Turn on Camera and allow to adjust to brightness
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
    try:
        sensor_data = load_sensor_data()
        return sensor_data
    except FileNotFoundError:
        return "Failed to load sensor data", 404


@app.route('/take_new_picture', methods=['POST'])
def take_new_picture_route():
    try:
        take_picture()
        return redirect(url_for('preview'))
    except FileNotFoundError:
        return "Failed to read data from image", 404

@app.route('/read_image', methods=['POST'])
def read_image_route():
    try:
        read_image()
        return redirect(url_for('preview'))
    except FileNotFoundError:
        return "Failed to read data from image", 404

@app.route('/draw_rois', methods=['POST'])
def draw_rois_route():
    try:
        # Load the configuration
        config = load_config()
        draw_rois()
        return redirect(url_for('preview'))
    except FileNotFoundError:
        return "Failed to draw ROI areas to image", 404

@app.route('/preview/image')
def preview_image():
    try:
        return send_file(watermeter_preview_image_path, mimetype='image/jpeg')
    except FileNotFoundError:
        return "No image found", 404

@app.route('/preview')
def preview():
    try:
        # Load the configuration
        config = load_config()
        # Get the ROIs
        rois = config.get('rois')
        gauge_rois = config.get('gauge_rois')
        print(rois)
        print(gauge_rois)
        sensor_data = load_sensor_data()

        # Render the template
        return render_template('preview.html', sensor_data=sensor_data, rois=rois, gauge_rois=gauge_rois)
    except FileNotFoundError:
        return "Failed to render preview page", 404
    
@app.route('/update_config', methods=['POST'])
def update_config():
    try:
        rois = []
        gauge_rois = []
        print(rois)
        print(gauge_rois)
        if request.method == 'POST':
            # Iterate over the form data
            for key in request.form:
                # Check if the key starts with 'roi'
                if key.startswith('roi'):
                    # Split the key into parts
                    parts = key.split('_')

                    # Check if the key has the correct format
                    if len(parts) == 3:
                        # Get the ROI number and coordinate
                        roi_number = int(parts[1])
                        coordinate = parts[2]

                        # Ensure the ROIs list has enough elements
                        while len(rois) < roi_number:
                            rois.append([])

                        # Get the value from the form data and convert it to an integer
                        value = int(request.form[key])

                        # Validate the value
                        if not (0 <= value <= 2000):
                            return "Invalid input: ROI values must be between 0 and 2000", 400

                        # Add the value to the correct ROI
                        rois[roi_number - 1].append(value)

                # Check if the key starts with 'gaugeroi'
                if key.startswith('gaugeroi'):
                    # Split the key into parts
                    parts = key.split('_')

                    # Check if the key has the correct format
                    if len(parts) == 3:
                        # Get the ROI number and coordinate
                        gauge_roi_number = int(parts[1])
                        coordinate = parts[2]

                        # Ensure the ROIs list has enough elements
                        while len(gauge_rois) < gauge_roi_number:
                            gauge_rois.append([])

                        # Get the value from the form data and convert it to an integer
                        value = int(request.form[key])

                        # Validate the value
                        if not (0 <= value <= 2000):
                            return "Invalid input: ROI values must be between 0 and 2000", 400

                        # Add the value to the correct ROI
                        gauge_rois[gauge_roi_number - 1].append(value)

            # Convert the lists to tuples
            rois = [tuple(roi) for roi in rois]
            gauge_rois = [tuple(roi) for roi in gauge_rois]
            print(rois)
            print(gauge_rois)
            config = load_config()
            config['rois'] = rois
            config['gauge_rois'] = gauge_rois
            # Update more values here
            print(rois)
            print(gauge_rois)
            # Write the updated configuration to the YAML file
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file)
            return redirect(url_for('preview'))
    except ValueError:
        return "Invalid input: could not convert data to an integer", 400

        

    
