from flask import Flask
from time import sleep
from flask_apscheduler import APScheduler
from app.routes import load_sensor_data, read_image, take_new_picture_route
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

# ROUTES
@app.route('/')
def home():
    try:
        sensor_data = load_sensor_data()
        return sensor_data
    except FileNotFoundError:
        return "Failed to load sensor data", 404

def run_schedule():
    take_new_picture_route()
    read_image()

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

watermeter_job_schedule = int(watermeter_job_schedule)

# Schedule the job to run every day at 10:30am
scheduler.add_job(id='run_schedule', func=run_schedule, trigger='interval', minutes=watermeter_job_schedule)

from app import routes
