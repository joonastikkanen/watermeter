import cv2
import pytesseract
from app import app
from camera import take_picture

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
