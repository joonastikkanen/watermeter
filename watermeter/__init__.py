import os
from camera import take_picture
from reader import read_image
from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        picamera_image_path = os.getenv('PICAMERA_IMAGE_PATH', '/run/shm/watermeter_last.jpg'),
        picamera_config = os.getenv('PICAMERA_CONFIG', '{"size": (1920, 1080)}'),
        tesseract_path = os.getenv('TESSERACT_PATH', '/usr/bin/tesseract'),
        tesseract_config = os.getenv('TESSERACT_CONFIG', '--psm 6 -c tessedit_char_whitelist=0123456789'),
        watermeter_last_value_file = os.getenv('WATERMETER_LAST_VALUE_FILE', '/run/shm/watermeter_last_value.txt'),
    )
    def check_tesseract_exists():
        tesseract_path = app.config['tesseract_path']
        if not os.path.isfile(tesseract_path):
            print(f"Error: The tesseract binary at {tesseract_path} does not exist.")

    # Call the function
    check_tesseract_exists()

    def load_sensor_data():
        watermeter_last_value_file = app.config['watermeter_last_value_file']
        try:
            with open(watermeter_last_value_file, 'r') as f:
                sensor_data = int(f.read())
        except FileNotFoundError:
            print(f"Info: The last value file {watermeter_last_value_file} is not found. Running reader function.")
            take_picture()
            read_image()

        return sensor_data
    app = Flask(__name__)
    app.run(host='0.0.0.0', port=5000)

    @app.route('/')
    def root():
        sensor_data = load_sensor_data()
        return sensor_data
