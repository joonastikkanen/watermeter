import os
import cv2
import blinkt
import time
import numpy as np
import cv2
import io
from PIL import Image
import libcamera
from picamera2 import Picamera2
from picamera2.controls import Controls
from time import sleep
from app import load_config


config = load_config()
picamera_debug = config['picamera_debug']
picamera_image_path = config['picamera_image_path']
picamera_photo_height = config['picamera_photo_height']
picamera_photo_width = config['picamera_photo_width']
picamera_led_enabled = config['picamera_led_enabled']
picamera_led_brightness = config['picamera_led_brightness']
picamera_image_rotate = config['picamera_image_rotate']
picamera_image_denoise_mode = config['picamera_image_denoise_mode']
picamera_image_brightness = config['picamera_image_brightness']
picamera_image_contrast = config['picamera_image_contrast']
picamera_image_sharpness = config['picamera_image_sharpness']
picamera_image_focus_position = config['picamera_image_focus_position']
picamera_image_focus_manual_enabled = config['picamera_image_focus_manual_enabled']
watermeter_preview_image_path = config['watermeter_preview_image_path']

# Picamera debugging
if picamera_debug:
  Picamera2.set_logging(Picamera2.DEBUG)

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
def take_picture(picamera_led_enabled, picamera_led_brightness, picamera_image_rotate, picamera_image_brightness, picamera_image_contrast, picamera_image_sharpness, picamera_image_denoise_mode, picamera_image_focus_position, picamera_image_focus_manual_enabled):
    camera = Picamera2()
    try:
        picamera_led_enabled = bool(picamera_led_enabled)
        picamera_led_brightness = float(picamera_led_brightness)
        picamera_image_rotate = int(picamera_image_rotate)
        picamera_image_brightness = float(picamera_image_brightness)
        picamera_image_contrast = float(picamera_image_contrast)
        picamera_image_focus_position = float(picamera_image_focus_position)
        picamera_image_focus_manual_enabled = bool(picamera_image_focus_manual_enabled)
        picamera_image_sharpness = float(picamera_image_sharpness)
        picamera_image_denoise_mode = str(picamera_image_denoise_mode)
        if picamera_led_enabled:
          # Turn on LED
          led_on(picamera_led_brightness)
        # Set resolution and turn on Camera
        #camera.still_configuration.size = (picamera_photo_width, picamera_photo_height)
        config = camera.create_still_configuration(main={"size": (picamera_photo_width, picamera_photo_height)})
        #camera.configure(config)
        camera.start()
        with camera.controls as ctrl:
          ctrl.Brightness = picamera_image_brightness
          ctrl.Contrast = picamera_image_contrast
          ctrl.Sharpness = picamera_image_sharpness
          if picamera_image_denoise_mode == "Off":
            ctrl.NoiseReductionMode = libcamera.controls.draft.NoiseReductionModeEnum.Off
          elif picamera_image_denoise_mode == "Fast":
            ctrl.NoiseReductionMode = libcamera.controls.draft.NoiseReductionModeEnum.Fast
          elif picamera_image_denoise_mode == "HighQuality":
            ctrl.NoiseReductionMode = libcamera.controls.draft.NoiseReductionModeEnum.HighQuality
        if picamera_image_focus_manual_enabled:
          camera.set_controls({"AfMode": Controls.AfModeEnum.Manual, "LensPosition": picamera_image_focus_position})
        if not picamera_image_focus_manual_enabled:
          success = camera.autofocus_cycle()
          job = camera.autofocus_cycle(wait=False)
          success = camera.wait(job)
        ctrls = Controls(camera)
        camera.set_controls(ctrls)
        sleep(1)
        image = camera.switch_mode_and_capture_array(config, "main")
        # Convert the image to grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        if picamera_image_rotate == 90:
          rotated_image = cv2.rotate(gray_image, cv2.ROTATE_90_CLOCKWISE)
        elif picamera_image_rotate == 180:
          rotated_image = cv2.rotate(gray_image, cv2.ROTATE_180)
        elif picamera_image_rotate == 270:
          rotated_image = cv2.rotate(gray_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        # Save the image
        cv2.imwrite(picamera_image_path, rotated_image)
        pass
    finally:
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
