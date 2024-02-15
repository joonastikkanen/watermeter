import os
import psutil
import cv2
import blinkt
import time
import numpy as np
import cv2
import io
from PIL import Image
import libcamera
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
picamera_buffer_count = config['picamera_buffer_count']
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
def take_picture(picamera_led_enabled, 
                 picamera_led_brightness, 
                 picamera_image_rotate,
                 picamera_image_brightness,
                 picamera_image_contrast,
                 picamera_image_sharpness,
                 picamera_image_denoise_mode,
                 picamera_image_focus_position,
                 picamera_image_focus_manual_enabled,
                 picamera_buffer_count,
                 picamera_photo_width,
                 picamera_photo_height,
                 picamera_image_binary_mode
                 ):
    from picamera2 import Picamera2
    from picamera2.controls import Controls
    # Picamera debugging
    if picamera_debug:
      Picamera2.set_logging(Picamera2.DEBUG)
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
        picamera_photo_width = int(picamera_photo_width)
        picamera_photo_height = int(picamera_photo_height)
        picamera_buffer_count = int(picamera_buffer_count)
        if picamera_led_enabled:
          # Turn on LED
          led_on(picamera_led_brightness)
        # Set resolution
        camera.start()
        config = camera.create_still_configuration(main={"size": (picamera_photo_width, picamera_photo_height)}, buffer_count=picamera_buffer_count)
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
        ctrls = Controls(camera)
        camera.set_controls(ctrls)
        if picamera_image_focus_manual_enabled:
          camera.set_controls({"AfMode": Controls.AfModeEnum.Manual, "LensPosition": picamera_image_focus_position})
        if not picamera_image_focus_manual_enabled:
          success = camera.autofocus_cycle()
          job = camera.autofocus_cycle(wait=False)
          success = camera.wait(job)
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
        if picamera_image_binary_mode == "simple":
          rotated_image = cv2.medianBlur(rotated_image,5)
          binary = cv2.threshold(rotated_image, 100, 255, cv2.THRESH_BINARY)
        elif picamera_image_binary_mode == "adaptive":
          rotated_image = cv2.medianBlur(rotated_image,5)
          binary = cv2.adaptiveThreshold(rotated_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        elif picamera_image_binary_mode == "otsu":
          rotated_image = cv2.GaussianBlur(rotated_image,(5,5),0)
          binary = cv2.threshold(rotated_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # Save the image
        cv2.imwrite(picamera_image_path, binary)
        # Get the process ID of the current process
        pid = os.getpid()
        # Create a Process object
        process = psutil.Process(pid)
        # Get the memory info
        memory_info = process.memory_info()
        # Print the memory usage
        print(f"Memory usage: {memory_info.rss / 1024 / 1024} MB")
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
