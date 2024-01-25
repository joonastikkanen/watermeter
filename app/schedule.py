import schedule
import time
from app import load_config
from app.camera import take_picture
from app.reader import read_image

def run_schedule():
    config = load_config()
    picamera_led_enabled = config['picamera_led_enabled']
    picamera_led_brightness = config['picamera_led_brightness']
    picamera_image_brightness = config['picamera_image_brightness']
    picamera_image_contrast = config['picamera_image_contrast']
    picamera_image_rotate = config['picamera_image_rotate']
    take_picture(picamera_led_enabled, picamera_led_brightness, picamera_image_rotate)
    read_image(picamera_image_brightness, picamera_image_contrast)