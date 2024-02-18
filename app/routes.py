from flask import send_file, redirect, url_for, render_template, request, Flask, jsonify
from app import app, load_config
from app.reader import load_sensor_data, read_image, draw_rois_and_gauges
from app.config_update import update_config, update_roi_editor_config
import json
import os
import psutil
import cv2
import blinkt
import time
import numpy as np
import cv2
from PIL import Image
from picamera2 import Picamera2
from picamera2.controls import Controls
from libcamera import controls
import libcamera
from time import sleep
from app import load_config

config = load_config()
# Convert the lists to tuples
picamera_image_path = config['picamera_image_path']
picamera_led_enabled = config['picamera_led_enabled']
picamera_led_brightness = config['picamera_led_brightness']
picamera_image_brightness = config['picamera_image_brightness']
picamera_image_contrast = config['picamera_image_contrast']
picamera_image_sharpness = config['picamera_image_sharpness']
picamera_image_denoise_mode = config['picamera_image_denoise_mode']
picamera_image_rotate = config['picamera_image_rotate']
picamera_photo_height = config['picamera_photo_height']
picamera_photo_width = config['picamera_photo_width']
picamera_debug = config['picamera_debug']
prerois = config['prerois'] = [tuple(roi) for roi in config['prerois']]
pregaugerois = config['pregaugerois'] = [tuple(roi) for roi in config['pregaugerois']]
postrois = config['postrois'] = [tuple(roi) for roi in config['postrois']]
postgaugerois = config['postgaugerois'] = [tuple(roi) for roi in config['postgaugerois']]
watermeter_preview_image_path = config['watermeter_preview_image_path']
watermeter_job_schedule = config['watermeter_job_schedule']

# Picamera debugging
if picamera_debug:
    Picamera2.set_logging(Picamera2.DEBUG)
camera = Picamera2()

# ROUTES
@app.route('/')
def home():
    try:
        sensor_data = load_sensor_data()
        return sensor_data
    except FileNotFoundError:
        return "Failed to load sensor data", 404


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
          camera.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": picamera_image_focus_position})
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
        if picamera_image_binary_mode == "off":
          binary = rotated_image
        elif picamera_image_binary_mode == "adaptive":
          rotated_image = cv2.medianBlur(rotated_image,5)
          binary = cv2.adaptiveThreshold(rotated_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        elif picamera_image_binary_mode == "otsu":
          rotated_image = cv2.GaussianBlur(rotated_image,(5,5),0)
          _, binary = cv2.threshold(rotated_image, 100, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
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
        #camera.stop()
        #camera.close()
        return True

def get_picamera_image_timestamp(picamera_image_path):
    if not os.path.isfile(picamera_image_path):
        picamera_image_time = "No picture yet taken"
    else:
        picamera_image_timestamp = os.path.getctime(picamera_image_path)
        picamera_image_time = time.ctime(picamera_image_timestamp)
    return picamera_image_time


@app.route('/take_new_picture', methods=['POST'])
def take_new_picture_route():
    try:
        config = load_config()
        picamera_led_enabled = config['picamera_led_enabled']
        picamera_led_brightness = config['picamera_led_brightness']
        picamera_image_rotate = config['picamera_image_rotate']
        picamera_image_brightness = config['picamera_image_brightness']
        picamera_image_contrast = config['picamera_image_contrast']
        picamera_image_focus_position = config['picamera_image_focus_position']
        picamera_image_focus_manual_enabled = config['picamera_image_focus_manual_enabled']
        picamera_image_sharpness = config['picamera_image_sharpness']
        picamera_image_denoise_mode = config['picamera_image_denoise_mode']
        picamera_buffer_count = config['picamera_buffer_count']
        picamera_photo_width = config['picamera_photo_width']
        picamera_photo_height = config['picamera_photo_height']
        picamera_image_binary_mode = config['picamera_image_binary_mode']
        take_picture(picamera_led_enabled, 
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
                     )
    except FileNotFoundError:
        return "Failed to take new picture", 404

@app.route('/preview/picamera_image')
def picamera_image():
    try:
        return send_file(picamera_image_path, mimetype='image/jpeg')
    except FileNotFoundError:
        return "No image found", 404


@app.route('/preview/roi_editor')
def roi_editor_route():
    try:
        roi_id = None
        roi_name = None
        roi_rgb_colors = None
        preroi_rgb_colors = None
        pregaugeroi_rgb_colors = None
        postroi_rgb_colors = None
        postgaugeroi_rgb_colors = None
        roi_colors_codes = {
          "preroi_rgb_colors": "255, 0, 0",
          "pregaugeroi_rgb_colors": "255, 140, 0",
          "postroi_rgb_colors": "0, 0, 255",
          "postgaugeroi_rgb_colors": "0, 140, 255",
        }
        print(request.args)
        for key, value in request.args.items():
            # Check if the key starts with 'roi_id'
            if key.startswith('roi_id'):
                roi_id = value
            # Check if the key starts with 'roi_name'
            if key.startswith('roi_name'):
                roi_name = value
            # Check if the key starts with 'roi_rgb_colors'
            if key.startswith('roi_rgb_colors'):
              roi_rgb_colors = value
              if roi_rgb_colors in roi_colors_codes:
                roi_rgb_color_code = roi_colors_codes[roi_rgb_colors]
        print(roi_rgb_color_code)

        return render_template('roi_editor.html',
                       roi_id=roi_id,
                       roi_name=roi_name,
                       picamera_photo_height=picamera_photo_height,
                       picamera_photo_width=picamera_photo_width,
                       roi_rgb_colors=roi_rgb_color_code
                       )
    except FileNotFoundError:
        return "No image found", 404


@app.route('/preview/submit_rois', methods=['POST'])
def submit_rois_route():
    update_roi_editor_config()
    read_image_route()
    draw_rois_route()
    return redirect(url_for('preview'))

@app.route('/read_image', methods=['POST'])
def read_image_route_post():
    try:
        read_image_route()
        return redirect(url_for('preview'))
    except FileNotFoundError:
        return "Failed to read data from image", 404

def read_image_route():
    try:
        read_image()
    except FileNotFoundError:
        return "Failed to read data from image", 404

@app.route('/draw_rois', methods=['POST'])
def draw_rois_route():
    try:
        # Load the configuration
        config = load_config()
        prerois = config.get('prerois')
        pregaugerois = config.get('pregaugerois')
        postrois = config.get('postrois')
        postgaugerois = config.get('postgaugerois')
        watermeter_preview_image_path = config['watermeter_preview_image_path']

        draw_rois_and_gauges(picamera_image_path, prerois, pregaugerois, postrois, postgaugerois, watermeter_preview_image_path)
    except FileNotFoundError:
        return "Failed to draw ROI areas to image", 404

@app.route('/preview/image')
def preview_image():
    try:
        return send_file(watermeter_preview_image_path, mimetype='image/jpeg')
    except FileNotFoundError:
        return "No image found", 404

@app.route('/preview')
def preview():
    try:
        # Load the configuration
        config = load_config()
        # Get the ROIs
        prerois = config.get('prerois')
        pregaugerois = config.get('pregaugerois')
        postrois = config.get('postrois')
        postgaugerois = config.get('postgaugerois')
        watermeter_job_schedule = config['watermeter_job_schedule']
        picamera_led_enabled = config['picamera_led_enabled']
        picamera_led_brightness = config['picamera_led_brightness']
        picamera_image_brightness = config['picamera_image_brightness']
        picamera_image_contrast = config['picamera_image_contrast']
        picamera_image_rotate = config['picamera_image_rotate']
        picamera_image_sharpness = config['picamera_image_sharpness']
        picamera_image_denoise_mode = config['picamera_image_denoise_mode']
        picamera_image_focus_position = config['picamera_image_focus_position']
        picamera_image_focus_manual_enabled = config['picamera_image_focus_manual_enabled']
        picamera_photo_height = config['picamera_photo_height']
        picamera_photo_width = config['picamera_photo_width']
        picamera_buffer_count = config['picamera_buffer_count']
        picamera_image_binary_mode = config['picamera_image_binary_mode']
        tesseract_oem = config['tesseract_oem']
        tesseract_psm = config['tesseract_psm']
        sensor_data = load_sensor_data()
        print(sensor_data)
        capture_timestamp = get_picamera_image_timestamp(picamera_image_path)
        # Render the template
        return render_template('preview.html',
                               sensor_data=sensor_data,
                               prerois=prerois,
                               pregaugerois=pregaugerois,
                               postrois=postrois,
                               postgaugerois=postgaugerois,
                               capture_timestamp=capture_timestamp,
                               picamera_led_enabled=picamera_led_enabled,
                               picamera_led_brightness=picamera_led_brightness,
                               picamera_image_brightness=picamera_image_brightness,
                               picamera_image_contrast=picamera_image_contrast,
                               picamera_image_rotate=picamera_image_rotate,
                               picamera_image_focus_position=picamera_image_focus_position,
                               picamera_image_focus_manual_enabled=picamera_image_focus_manual_enabled,
                               watermeter_job_schedule=watermeter_job_schedule,
                               picamera_image_sharpness=picamera_image_sharpness,
                               picamera_image_denoise_mode=picamera_image_denoise_mode,
                               picamera_buffer_count=picamera_buffer_count,
                               picamera_image_binary_mode=picamera_image_binary_mode,
                               picamera_photo_height=picamera_photo_height,
                               picamera_photo_width=picamera_photo_width,
                               tesseract_oem=tesseract_oem,
                               tesseract_psm=tesseract_psm
                               )
    except FileNotFoundError:
        return "Failed to render preview page", 404

# Global variable to track if a request is being processed
is_request_being_processed = False

@app.route('/update_config', methods=['POST'])
def update_config_route():
    try:
        global is_request_being_processed
        # If a request is being processed, return an error
        if is_request_being_processed:
            return jsonify({'error': 'A request is already being processed'}), 429
        # Otherwise, set the global variable to True and process the request
        is_request_being_processed = True
        update_config()
        take_new_picture_route()
        read_image_route()
        draw_rois_route()
        # After processing the request, set the global variable back to False
        is_request_being_processed = False

        return redirect(url_for('preview'))
    except FileNotFoundError:
        return "Failed to update config", 404
