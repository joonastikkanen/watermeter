from flask import app
import cv2
import pytesseract

def read_image():
    tesseract_path = app.config['tesseract_path']
    tesseract_config = app.config['tesseract_config']
    picamera_image_path = app.config['picamera_image_path']
    watermeter_last_value_file = app.config['watermeter_last_value_file']
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