import os
import cv2
import blinkt
import time
import numpy as np
import cv2
import io
from PIL import Image
from libcamera import controls
from picamera2 import Picamera2
from time import sleep
from app import load_config

config = load_config()
picamera_image_path = config['picamera_image_path']
picamera_photo_height = config['picamera_photo_height']
picamera_photo_width = config['picamera_photo_width']
picamera_led_enabled = config['picamera_led_enabled']
picamera_led_brightness = config['picamera_led_brightness']
picamera_image_rotate = config['picamera_image_rotate']
picamera_image_focus_position = config['picamera_image_focus_position']
picamera_image_focus_manual_enabled = config['picamera_image_focus_manual_enabled']
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
def take_picture(picamera_led_enabled, picamera_led_brightness, picamera_image_rotate, picamera_image_brightness, picamera_image_contrast, picamera_image_focus_position, picamera_image_focus_manual_enabled):
    camera = Picamera2()
    picamera_led_enabled = bool(picamera_led_enabled)
    picamera_led_brightness = float(picamera_led_brightness)
    picamera_image_rotate = int(picamera_image_rotate)
    picamera_image_brightness = float(picamera_image_brightness)
    picamera_image_contrast = float(picamera_image_contrast)
    picamera_image_focus_position = float(picamera_image_focus_position)
    picamera_image_focus_manual_enabled = bool(picamera_image_focus_manual_enabled)
    if picamera_led_enabled:
      # Turn on LED
      led_on(picamera_led_brightness)
    config = camera.create_preview_configuration({"format": "YUV420", "size": (picamera_photo_width, picamera_photo_height)}, main)
    camera.configure(config)
    # Set resolution and turn on Camera
    #camera.still_configuration.size = (picamera_photo_width, picamera_photo_height)
    # Set the brightness and contrast
    #camera.brightness = picamera_image_brightness
    #camera.contrast = picamera_image_contrast
    camera.start()
    if picamera_image_focus_manual_enabled:
      camera.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": picamera_image_focus_position})
    if not picamera_image_focus_manual_enabled:
      success = camera.autofocus_cycle()
      job = camera.autofocus_cycle(wait=False)
      success = camera.wait(job)
    sleep(1)

    stream = io.BytesIO()
    camera.capture_file(stream, format='jpeg')
    # Open the image and rotate it
    img = Image.open(stream)
    rotated_img = img.rotate(picamera_image_rotate) 

    # Convert the PIL Image to a NumPy array
    image = np.array(rotated_img)

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Save the image
    cv2.imwrite(picamera_image_path, gray_image)
    # Close the camera
    camera.stop()
    camera.close()

    return True

def get_picamera_image_timestamp(picamera_image_path):
    if not os.path.isfile(picamera_image_path):
        picamera_image_time = "No picture yet taken"
    else:
        picamera_image_timestamp = os.path.getctime(picamera_image_path)
        picamera_image_time = time.ctime(picamera_image_timestamp)
    return picamera_image_time
