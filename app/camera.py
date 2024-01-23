import os
import blinkt
from picamera2 import Picamera2
from time import sleep, time
from datetime import datetime
from app import load_config

config = load_config()
picamera_image_path = config['picamera_image_path']
picamera_photo_height = config['picamera_photo_height']
picamera_photo_width = config['picamera_photo_width']
watermeter_preview_image_path = config['watermeter_preview_image_path']

# LED ON
def led_on():
    blinkt.set_clear_on_exit(False)
    blinkt.set_all(255, 255, 255, 1.0)
    blinkt.show()

# LED OFF
def led_off():
    blinkt.clear()
    blinkt.show()

# TAKE PICTURE
def take_picture():
    camera = Picamera2()
    # Turn on LED
    led_on()
    # Set resolution and turn on Camera
    camera.still_configuration.size = (picamera_photo_width, picamera_photo_height)
    camera.still_configuration.enable_raw()
    camera.still_configuration.raw.size = camera.sensor_resolution
    camera.start()
    sleep(1)
    # Take an image. I put in in /run/shm to not wear the SD card
    camera.switch_mode_and_capture_file("still", picamera_image_path)
    camera.close()
    led_off()
    return True

def get_picamera_image_timestamp(picamera_image_path):
    picamera_image_timestamp = os.path.getctime(picamera_image_path)
    picamera_image_time = time.ctime(picamera_image_timestamp)
    return picamera_image_time