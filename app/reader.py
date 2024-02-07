import cv2
import pytesseract
from app import load_config
import numpy as np
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from app.camera import take_picture
import os
import pytesseract

config = load_config()
picamera_image_path = config['picamera_image_path']
prerois = config['prerois'] = [tuple(roi) for roi in config['prerois']]
pregaugerois = config['pregaugerois'] = [tuple(roi) for roi in config['pregaugerois']]
postrois = config['postrois'] = [tuple(roi) for roi in config['postrois']]
postgaugerois = config['postgaugerois'] = [tuple(roi) for roi in config['postgaugerois']]
tesseract_path = config['tesseract_path']
tesseract_config = config['tesseract_config']
watermeter_last_value_file = config['watermeter_last_value_file']
watermeter_preview_image_path = config['watermeter_preview_image_path']
watermeter_init_value = config['watermeter_init_value']

# READ IMAGE
def read_image():
    # Set the path to the tesseract executable
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    # Load the image from file
    image = cv2.imread(picamera_image_path, cv2.IMREAD_GRAYSCALE)

    # Apply a binary threshold
    _, binary = cv2.threshold(image, 100, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Save the preprocessed image
    cv2.imwrite(picamera_image_path, binary)
    preprocessed_image = cv2.imread(picamera_image_path)
    def read_digits(rois, preprocessed_image):
        digits = ''  # Initialize digits as an empty string
        # Process each ROI
        for x, y, w, h in rois:
            # Crop the image
            roi = preprocessed_image[y:y+h, x:x+w]
            # Use Tesseract to do OCR on the ROI
            digit = pytesseract.image_to_string(roi, config=tesseract_config)
            digits += digit.strip()  # Append the digit to the digits value
            # Print the text
            print(digits)
        return digits


    def read_gauges(gaugerois, preprocessed_image):
        total_digits = 0  # Initialize total_digits as 0
        # Process each ROI
        for x, y, w, h in gaugerois:
            # Crop the image to the ROI
            gauge_roi = preprocessed_image[y:y+h, x:x+w]

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
            total_digits += int(value)
            print(total_digits)
        return total_digits

    pre_digits = ''
    for preroi_digits in [ prerois, pregaugerois]:
        pre_digit = read_digits(preroi_digits, preprocessed_image).strip()
        pre_digits += pre_digit.strip()
        print(f"preroi_digits: ", pre_digits)

    post_digits = ''
    for postroi_digits in [ postrois, postgaugerois ]:
        post_digit = read_digits(postroi_digits, preprocessed_image).strip()
        post_digits += post_digit.strip()
        print(f"postroi_digits: ", post_digits)

    total_digits = pre_digits + "." + post_digits
    # Wire sensor data to file
    with open(watermeter_last_value_file, 'w') as f:
        f.write(total_digits)

    # Return the value
    return total_digits

# Draw the ROIs on the image
def draw_rois_and_gauges(image_path, prerois, pregaugerois, postrois, postgaugerois, output_path):
    # Load the image
    image = cv2.imread(image_path)

    # Draw each ROI
    for x, y, w, h in prerois:
        text = "prerois"
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 255), 2)
        # Draw the text on the image
        cv2.putText(image, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # Draw each ROI
    for x, y, w, h in postrois:
        text = "postrois"
        cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
        # Draw the text on the image
        cv2.putText(image, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

    if 'value' in locals():
        print("The value variable is defined.")
        # Draw each gauge
        for x, y, w, h, value in pregaugerois:
            text = "pregaugerois"
            # Calculate the angle and position of the line
            angle = (value / 10) * 180  # Assuming the gauge range is 10
            line_length = h / 2
            line_x = x + w / 2 + line_length * np.cos(angle)
            line_y = y + h / 2 - line_length * np.sin(angle)

            # Draw the line
            cv2.line(image, (x + w // 2, y + h // 2), (int(line_x), int(line_y)), (0, 140, 255), 2)
            # Draw the text on the image
            cv2.putText(image, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 140, 255), 2)

        for x, y, w, h, value in postgaugerois:
            text = "postgaugerois"
            # Calculate the angle and position of the line
            angle = (value / 10) * 180  # Assuming the gauge range is 10
            line_length = h / 2
            line_x = x + w / 2 + line_length * np.cos(angle)
            line_y = y + h / 2 - line_length * np.sin(angle)

            # Draw the line
            cv2.line(image, (x + w // 2, y + h // 2), (int(line_x), int(line_y)), (255, 140, 0), 2)
            # Draw the text on the image
            cv2.putText(image, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 140, 0), 2)
    else:
        print("The value variable is not defined.")
        for x, y, w, h in pregaugerois:
            text = "pregaugerois"
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 140, 255), 2)
            # Draw the text on the image
            cv2.putText(image, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 140, 255), 2)

        for x, y, w, h in postgaugerois:
            text = "postgaugerois"
            cv2.rectangle(image, (x, y), (x+w, y+h), (255, 140, 0), 2)
            # Draw the text on the image
            cv2.putText(image, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 140, 0), 2)

    # Save the image
    cv2.imwrite(output_path, image)
    return True

# LOAD SENSOR DATA
def load_sensor_data():
    if not os.path.isfile(watermeter_last_value_file):
        with open(watermeter_last_value_file, 'w') as f:
            f.write(str(watermeter_init_value))
    else:
        with open(watermeter_last_value_file, 'r') as f:
            sensor_data = f.read()
    return sensor_data
