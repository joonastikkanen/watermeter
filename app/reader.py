import cv2
import pytesseract
from app import load_config
import numpy as np
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from camera import take_picture

config = load_config()
gauge_rois = config['gauge_rois'] = [tuple(roi) for roi in config['gauge_rois']]
picamera_image_path = config['picamera_image_path']
rois = config['rois'] = [tuple(roi) for roi in config['rois']]
tesseract_path = config['tesseract_path']
tesseract_config = config['tesseract_config']
watermeter_last_value_file = config['watermeter_last_value_file']
watermeter_preview_image_path = config['watermeter_preview_image_path']

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
        read_digits()
        read_gauges()
        # Convert the digits string to an integer
        if digits.isdigit():
            value = int(digits)
        else:
           value = "Error: Digits contains non-integer values."
        return digits
    # Wire sensor data to file
    with open(watermeter_last_value_file, 'w') as f:
    	f.write(digits)

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
