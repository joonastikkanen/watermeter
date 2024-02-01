from flask import Flask
from flask_apscheduler import APScheduler
import yaml

# LOAD CONFIG FILE
def load_config():
    with open('config/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    return config

config = load_config()
# Convert the lists to tuples
picamera_image_path = config['picamera_image_path']
picamera_photo_height = config['picamera_photo_height']
picamera_photo_width = config['picamera_photo_width']
picamera_image_rotate = config['picamera_image_rotate']
picamera_led_enabled = config['picamera_led_enabled']
picamera_led_brightness = config['picamera_led_brightness']
picamera_image_brightness = config['picamera_image_brightness']
picamera_image_contrast = config['picamera_image_contrast']
picamera_image_focus_position = config['picamera_image_focus_position']
picamera_image_focus_manual_enabled = config['picamera_image_focus_manual_enabled']
prerois = config['prerois'] = [tuple(roi) for roi in config['prerois']]
pregaugerois = config['pregaugerois'] = [tuple(roi) for roi in config['pregaugerois']]
postrois = config['postrois'] = [tuple(roi) for roi in config['postrois']]
postgaugerois = config['postgaugerois'] = [tuple(roi) for roi in config['postgaugerois']]
tesseract_path = config['tesseract_path']
tesseract_config = config['tesseract_config']
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

from app.camera import take_picture
from app.reader import read_image

def run_schedule():
    take_picture(picamera_led_enabled, picamera_led_brightness, picamera_image_rotate, picamera_image_brightness, picamera_image_contrast, picamera_image_focus_position, picamera_image_focus_manual_enabled)
    read_image()


scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

watermeter_job_schedule = int(watermeter_job_schedule)

# Schedule the job to run every day at 10:30am
scheduler.add_job(id='run_schedule', func=run_schedule, trigger='interval', minutes=watermeter_job_schedule)

from app import routes
