import os
import cv2
import blinkt
import time
import libcamera
from PIL import Image
from picamera2 import Picamera2
from time import sleep
from datetime import datetime
from app import load_config

config = load_config()
picamera_image_path = config['picamera_image_path']
picamera_photo_height = config['picamera_photo_height']
picamera_photo_width = config['picamera_photo_width']
picamera_led_enabled = config['picamera_led_enabled']
picamera_led_brightness = config['picamera_led_brightness']
picamera_image_rotate = config['picamera_image_rotate']
watermeter_preview_image_path = config['watermeter_preview_image_path']

# LED ON
def led_on(picamera_led_brightness):
    blinkt.set_clear_on_exit(False)
    blinkt.set_all(255, 255, 255, picamera_led_brightness)
    blinkt.show()

# LED OFF
def led_off():
    blinkt.clear()
    blinkt.show()

# TAKE PICTURE
def take_picture(picamera_led_enabled, picamera_led_brightness, picamera_image_rotate, picamera_image_brightness, picamera_image_contrast):
    camera = Picamera2()
    picamera_led_enabled = bool(picamera_led_enabled)
    picamera_led_brightness = float(picamera_led_brightness)
    picamera_image_rotate = int(picamera_image_rotate)
    picamera_image_brightness = float(picamera_image_brightness)
    picamera_image_contrast = float(picamera_image_contrast)
    if picamera_led_enabled:
        # Turn on LED
        led_on(picamera_led_brightness)
    # Set resolution and turn on Camera
    camera.still_configuration.size = (picamera_photo_width, picamera_photo_height)
    camera.start()
    sleep(1)
    # Take an image. I put in in /run/shm to not wear the SD card
    camera.switch_mode_and_capture_file("still", picamera_image_path)
    camera.close()
    if picamera_led_enabled:
        # Turn on LED
        led_off()
    # Open an image file
    with Image.open(picamera_image_path) as img:
        # Flip the image vertically
        roteted_img = img.rotate(picamera_image_rotate)
        # Save the flipped image
        roteted_img.save(picamera_image_path)

    # Load the image from file
    image = cv2.imread(picamera_image_path)

    # Adjust brightness and contrast
    image = cv2.convertScaleAbs(image, alpha=picamera_image_contrast, beta=picamera_image_brightness)
    # Save the image
    cv2.imwrite(picamera_image_path, image)
    return True

def get_picamera_image_timestamp(picamera_image_path):
    if not os.path.isfile(picamera_image_path):
        picamera_image_time = "No picture yet taken"
    else:
        picamera_image_timestamp = os.path.getctime(picamera_image_path)
        picamera_image_time = time.ctime(picamera_image_timestamp)
    return picamera_image_time
