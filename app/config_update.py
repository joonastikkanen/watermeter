from app import load_config
import yaml
import json
from flask import request, jsonify

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
            if key.startswith('picamera_image_rotate'):
                picamera_image_rotate = request.form['picamera_image_rotate']
                config['picamera_image_rotate'] = picamera_image_rotate
            if key.startswith('watermeter_job_schedule'):
                watermeter_job_schedule = request.form['watermeter_job_schedule']
                config['watermeter_job_schedule'] = watermeter_job_schedule
            # Update more values here
            if key.startswith('picamera_led_enabled_true'):
                config['picamera_led_enabled'] = bool(True)
            if key.startswith('picamera_led_enabled_false'):
                config['picamera_led_enabled'] = bool(False)
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

