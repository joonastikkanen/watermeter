import cv2
import pytesseract
from app import load_config
import numpy as np
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from app.camera import take_picture
import os

config = load_config()
picamera_image_path = config['picamera_image_path']
prerois = config['prerois'] = [tuple(roi) for roi in config['prerois']]
pregauge_rois = config['pregauge_rois'] = [tuple(roi) for roi in config['pregauge_rois']]
postrois = config['postrois'] = [tuple(roi) for roi in config['postrois']]
postgauge_rois = config['postgauge_rois'] = [tuple(roi) for roi in config['postgauge_rois']]
tesseract_path = config['tesseract_path']
tesseract_config = config['tesseract_config']
watermeter_last_value_file = config['watermeter_last_value_file']
watermeter_preview_image_path = config['watermeter_preview_image_path']
watermeter_init_value = config['watermeter_init_value']
# READ IMAGE
def read_image():
    # Initialize an empty string to hold the digits
    predigits = ''
    postdigits = ''
    # Set the path to the tesseract executable
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    # Load the image from file
    image = cv2.imread(picamera_image_path)

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def read_predigits():

        # Crop the image
        # Process each ROI
        for x, y, w, h in prerois:
            # Crop the image
            preroi = gray_image[y:y+h, x:x+w]

            # Use Tesseract to do OCR on the ROI
            predigits += pytesseract.image_to_string(preroi, config=tesseract_config)

            # Print the text
            print(predigits)

        return(predigits)

    def read_pregauges():
        # Process each ROI
        for x, y, w, h in pregauge_rois:
            # Crop the image to the ROI
            pregauge_roi = gray_image[y:y+h, x:x+w]

            # Use edge detection and Hough line transformation to find the pointer
            edges = cv2.Canny(pregauge_roi, 50, 150, apertureSize=3)
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
            predigits += str(value)
        return(predigits)

    def read_postdigits():

        # Crop the image
        # Process each ROI
        for x, y, w, h in postrois:
            # Crop the image
            postroi = gray_image[y:y+h, x:x+w]

            # Use Tesseract to do OCR on the ROI
            postdigits += pytesseract.image_to_string(postroi, config=tesseract_config)

            # Print the text
            print(postdigits)

        return(postdigits)

    def read_postgauges():
        # Process each ROI
        for x, y, w, h in postgauge_rois:
            # Crop the image to the ROI
            postgauge_roi = gray_image[y:y+h, x:x+w]

            # Use edge detection and Hough line transformation to find the pointer
            edges = cv2.Canny(postgauge_roi, 50, 150, apertureSize=3)
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
            postdigits += str(value)
        return(postdigits)
    
    read_predigits()
    read_pregauges()
    read_postdigits()
    read_postgauges()
    
    digits = predigits + '.' + postdigits
    
    # Convert the digits string to an integer
    if digits.isdigit():
        value = int(digits)
    else:
        value = "Error: Digits contains non-integer values."

    # Wire sensor data to file
    with open(watermeter_last_value_file, 'w') as f:
        f.write(value)
     
    # Return the value
    return value

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
            for x, y, w, h in prerois:
                draw.rectangle(left=x, top=y, width=w, height=h)

            for x, y, w, h in pregauge_rois:
                draw.rectangle(left=x, top=y, width=w, height=h)

            for x, y, w, h in postrois:
                draw.rectangle(left=x, top=y, width=w, height=h)

            for x, y, w, h in postgauge_rois:
                draw.rectangle(left=x, top=y, width=w, height=h)

            # Overlay the ROIs onto the image
            draw(img)

        # Save the image
        img.save(filename=watermeter_preview_image_path)
    return True

# LOAD SENSOR DATA
def load_sensor_data():
    if not os.path.isfile(watermeter_last_value_file):
        with open(watermeter_last_value_file, 'w') as f:
            f.write(str(watermeter_init_value))
    else:              
        with open(watermeter_last_value_file, 'r') as f:
            sensor_data = str(f.read())
    return sensor_data
