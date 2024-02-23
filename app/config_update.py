from app import load_config
import yaml
import json
from flask import request

config = load_config()

def update_config():
    try:
        print(request.form)
        for key in request.form:
            if key.startswith('picamera_image_brightness'):
                picamera_image_brightness = request.form['picamera_image_brightness']
                config['picamera_image_brightness'] = picamera_image_brightness
            if key.startswith('picamera_image_contrast'):
                picamera_image_contrast = request.form['picamera_image_contrast']
                config['picamera_image_contrast'] = picamera_image_contrast
            if key.startswith('picamera_led_brightness'):
                picamera_led_brightness = request.form['picamera_led_brightness']
                config['picamera_led_brightness'] = picamera_led_brightness
            if key.startswith('picamera_image_focus_position'):
                picamera_image_focus_position = request.form['picamera_image_focus_position']
                config['picamera_image_focus_position'] = picamera_image_focus_position
            if key.startswith('picamera_image_rotate'):
                picamera_image_rotate = request.form['picamera_image_rotate']
                config['picamera_image_rotate'] = picamera_image_rotate
            if key.startswith('picamera_image_sharpness'):
                picamera_image_sharpness = request.form['picamera_image_sharpness']
                config['picamera_image_sharpness'] = picamera_image_sharpness
            if key.startswith('picamera_image_denoise_mode'):
                picamera_image_denoise_mode = request.form['picamera_image_denoise_mode']
                config['picamera_image_denoise_mode'] = picamera_image_denoise_mode
            if key.startswith('picamera_photo_height'):
                picamera_photo_height = request.form['picamera_photo_height']
                config['picamera_photo_height'] = picamera_photo_height
            if key.startswith('picamera_photo_width'):
                picamera_photo_width = request.form['picamera_photo_width']
                config['picamera_photo_width'] = picamera_photo_width
            if key.startswith('picamera_buffer_count'):
                picamera_buffer_count = request.form['picamera_buffer_count']
                config['picamera_buffer_count'] = picamera_buffer_count
            if key.startswith('picamera_image_binary_mode'):
                picamera_image_binary_mode = request.form['picamera_image_binary_mode']
                config['picamera_image_binary_mode'] = picamera_image_binary_mode
            if key.startswith('watermeter_job_schedule'):
                watermeter_job_schedule = request.form['watermeter_job_schedule']
                config['watermeter_job_schedule'] = watermeter_job_schedule
            if key.startswith('tesseract_oem'):
                tesseract_oem = request.form['tesseract_oem']
                config['tesseract_oem'] = tesseract_oem
            if key.startswith('tesseract_psm'):
                tesseract_psm = request.form['tesseract_psm']
                config['tesseract_psm'] = tesseract_psm
            if key.startswith('tesseract_validation_counter'):
                tesseract_validation_counter = request.form['tesseract_validation_counter']
                tesseract_validation_counter = int(tesseract_validation_counter)
                config['tesseract_validation_counter'] = tesseract_validation_counter
            if key.startswith('picamera_image_focus_manual_enabled'):
                picamera_image_focus_manual_enabled = request.form['picamera_image_focus_manual_enabled']
                if picamera_image_focus_manual_enabled == 'True':
                    config['picamera_image_focus_manual_enabled'] = True
                if picamera_image_focus_manual_enabled == 'False':
                    config['picamera_image_focus_manual_enabled'] = False
            if key.startswith('picamera_led_enabled'):
                picamera_led_enabled = request.form['picamera_led_enabled']
                if picamera_led_enabled == 'True':
                    config['picamera_led_enabled'] = True
                if picamera_led_enabled == 'False':
                    config['picamera_led_enabled'] = False

        # Write the updated configuration to the YAML file
        with open('config/config.yaml', 'w') as file:
            yaml.dump(config, file, default_flow_style=None)
        return True
    except ValueError:
        return "Invalid input: could not convert data to an integer", 400

def update_roi_editor_config():
    try:
        # Iterate over the form data
        prerois = []
        pregaugerois = []
        postrois = []
        postgaugerois = []
        roi_json = request.form
        print(request.form)
        for key, value in roi_json.items():
            if key.startswith('preroi'):
                rois = json.loads(value)
                # Create a list of lists, where each inner list contains the values of a dictionary
                prerois = [[int(roi['x']), int(roi['y']), int(roi['w']), int(roi['h'])] for roi in rois]
                print(prerois)
                # Print the list of lists as YAML
                config['prerois'] = prerois

        for key, value in roi_json.items():
            if key.startswith('pregaugeroi'):
                rois = json.loads(value)
                # Create a list of lists, where each inner list contains the values of a dictionary
                pregaugerois = [[int(roi['x']), int(roi['y']), int(roi['w']), int(roi['h'])] for roi in rois]
                print(pregaugerois)
                # Print the list of lists as YAML
                config['pregaugerois'] = pregaugerois

        for key, value in roi_json.items():
            if key.startswith('postroi'):
                rois = json.loads(value)
                # Create a list of lists, where each inner list contains the values of a dictionary
                postrois = [[int(roi['x']), int(roi['y']), int(roi['w']), int(roi['h'])] for roi in rois]
                print(postrois)
                # Print the list of lists as YAML
                config['postrois'] = postrois

        for key, value in roi_json.items():
            if key.startswith('postgaugeroi'):
                rois = json.loads(value)
                # Create a list of lists, where each inner list contains the values of a dictionary
                postgaugerois = [[int(roi['x']), int(roi['y']), int(roi['w']), int(roi['h'])] for roi in rois]
                print(postgaugerois)
                # Print the list of lists as YAML
                config['postgaugerois'] = postgaugerois

        # Write the updated configuration to the YAML file
        with open('config/config.yaml', 'w') as file:
            yaml.dump(config, file, default_flow_style=None)
        return True
    except ValueError:
        return "Invalid input: could not convert data to an integer", 400

