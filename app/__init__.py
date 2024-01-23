from flask import Flask 
import yaml

# LOAD CONFIG FILE
def load_config():
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    return config

config = load_config()
# Convert the lists to tuples
picamera_image_path = config['picamera_image_path']
picamera_photo_height = config['picamera_photo_height']
picamera_photo_width = config['picamera_photo_width']
prerois = config['prerois'] = [tuple(roi) for roi in config['prerois']]
pregauge_rois = config['pregauge_rois'] = [tuple(roi) for roi in config['pregauge_rois']]
postrois = config['postrois'] = [tuple(roi) for roi in config['postrois']]
postgauge_rois = config['postgauge_rois'] = [tuple(roi) for roi in config['postgauge_rois']]
tesseract_path = config['tesseract_path']
tesseract_config = config['tesseract_config']
watermeter_last_value_file = config['watermeter_last_value_file']
watermeter_preview_image_path = config['watermeter_preview_image_path']
watermeter_init_value = config['watermeter_init_value']

# CONFIGURATION
class Config(object):
    DEBUG = False

# APP
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    return app

app = create_app()

from app import routes
