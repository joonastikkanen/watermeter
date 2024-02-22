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
