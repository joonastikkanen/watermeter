import schedule
import time
from app import load_config
from app.camera import take_picture
from app.reader import read_image

config = load_config()
# Convert the lists to tuples
watermeter_job_schedule = config['watermeter_job_schedule']
picamera_led_enabled = config['picamera_led_enabled']
picamera_led_brightness = config['picamera_led_brightness']
picamera_image_brightness = config['picamera_image_brightness']
picamera_image_contrast = config['picamera_image_contrast']

def job():
    take_picture(picamera_led_enabled, picamera_led_brightness)
    read_image(picamera_image_brightness, picamera_image_contrast)

# Schedule the job every 5 minutes
schedule.every(watermeter_job_schedule).minutes.do(job)

while True:
    # Run pending jobs
    schedule.run_pending()
    # Sleep for a while before checking for pending jobs again
    time.sleep(1)