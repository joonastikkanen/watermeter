from time import sleep
from picamera2 import Picamera2, Preview
from flask import app
import os

def take_picture():
    picamera_config = app.config['picamera_config']
    picamera_image_path = app.config['picamera_image_path']
    camera = Picamera2()
    preview_config = camera.create_preview_configuration(main=picamera_config)
    camera.configure(preview_config)
    # Turn on LED
    #led.on()
    # Turn on Camera and allow to adjust to brightness
    camera.start_preview(Preview.NULL)
    camera.start()
    sleep(1)
    # Take an image. I put in in /run/shm to not wear the SD card
    metadata = camera.capture_file(picamera_image_path)
    camera.close()
    #led.off()
    return True