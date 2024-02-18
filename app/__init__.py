from flask import Flask
from time import sleep
import yaml

# LOAD CONFIG FILE
def load_config():
    with open('config/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    return config

config = load_config()
# Convert the lists to tuples
picamera_debug = config['picamera_debug']
picamera_image_path = config['picamera_image_path']
picamera_photo_height = config['picamera_photo_height']
picamera_photo_width = config['picamera_photo_width']
picamera_image_rotate = config['picamera_image_rotate']
picamera_led_enabled = config['picamera_led_enabled']
picamera_led_brightness = config['picamera_led_brightness']
picamera_image_brightness = config['picamera_image_brightness']
picamera_image_contrast = config['picamera_image_contrast']
picamera_image_sharpness = config['picamera_image_sharpness']
picamera_image_denoise_mode = config['picamera_image_denoise_mode']
picamera_image_focus_position = config['picamera_image_focus_position']
picamera_image_focus_manual_enabled = config['picamera_image_focus_manual_enabled']
picamera_buffer_count = config['picamera_buffer_count']
picamera_image_binary_mode = config['picamera_image_binary_mode']
prerois = config['prerois'] = [tuple(roi) for roi in config['prerois']]
pregaugerois = config['pregaugerois'] = [tuple(roi) for roi in config['pregaugerois']]
postrois = config['postrois'] = [tuple(roi) for roi in config['postrois']]
postgaugerois = config['postgaugerois'] = [tuple(roi) for roi in config['postgaugerois']]
tesseract_path = config['tesseract_path']
tesseract_oem = config['tesseract_oem']
tesseract_psm = config['tesseract_psm']
watermeter_last_value_file = config['watermeter_last_value_file']
watermeter_preview_image_path = config['watermeter_preview_image_path']
watermeter_init_value = config['watermeter_init_value']
watermeter_job_schedule = config['watermeter_job_schedule']

# CONFIGURATION
class Config(object):
    DEBUG = False
    SCHEDULER_API_ENABLED = True

# APP
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    return app

app = create_app()

from app import routes
