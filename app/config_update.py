from app import load_config
import yaml
import json
from flask import request

config = load_config()

def update_config():
    """
    Update the configuration settings based on the values received from the request form.

    Returns:
        bool or tuple: True if the configuration was successfully updated, or a tuple containing
                      an error message and status code if there was an invalid input.
    """
    try:
        print(request.form)
        for key, value in request.form.items():
            if key.startswith('picamera_'):
                config[key] = value
            if key.startswith('watermeter_job_schedule'):
                config[key] = value
            if key.startswith('picamera_image_focus_manual_enabled'):
                config[key] = value == 'True'
            if key.startswith('picamera_led_enabled'):
                config[key] = value == 'True'
            if key.startswith('aws_'):
                config[key] = value
        # Write the updated configuration to the YAML file
        with open('config/config.yaml', 'w') as file:
            yaml.dump(config, file, default_flow_style=None)
        return True
    except ValueError:
        return "Invalid input: could not convert data to an integer", 400

def update_roi_editor_config():
    """
    Update the ROI editor configuration based on the form data.

    This function iterates over the form data and updates the configuration file with the ROI values.
    The form data should contain keys starting with 'preroi', 'pregaugeroi', 'postroi', or 'postgaugeroi',
    followed by a JSON string representing the ROI coordinates.

    Returns:
        - True if the configuration was successfully updated.
        - An error message and status code (400) if the input data is invalid.
    """
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

