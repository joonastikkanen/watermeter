from app import load_config
import yaml
import json
from flask import request, jsonify

config = load_config()

def update_config():
    try:
        # Iterate over the form data
        prerois = []
        pregaugerois = []
        postrois = []
        postgaugerois = []
        print(request.form)
        for key in request.form:
            # Check if the key starts with 'preroi'
            if key.startswith('preroi'):
                # Split the key into parts
                parts = key.split('_')

                # Check if the key has the correct format
                if len(parts) == 3:
                    # Get the ROI number and coordinate
                    preroi_number = int(parts[1])
                    coordinate = parts[2]
                    # Ensure the ROIs list has enough elements
                    while len(prerois) < preroi_number:
                        prerois.append([])

                    # Get the value from the form data and convert it to an integer
                    value = int(request.form[key])
                    # Validate the value
                    if not (0 <= value <= 2000):
                        return "Invalid input: ROI values must be between 0 and 2000", 400

                    # Add the value to the correct ROI
                    prerois[preroi_number - 1].append(value)

            # Check if the key starts with 'gaugeroi'
            if key.startswith('pregaugeroi'):
                # Split the key into parts
                parts = key.split('_')

                # Check if the key has the correct format
                if len(parts) == 3:
                    # Get the ROI number and coordinate
                    pregauge_roi_number = int(parts[1])
                    coordinate = parts[2]

                    # Ensure the ROIs list has enough elements
                    while len(pregaugerois) < pregauge_roi_number:
                        pregaugerois.append([])

                    # Get the value from the form data and convert it to an integer
                    value = int(request.form[key])

                    # Validate the value
                    if not (0 <= value <= 2000):
                        return "Invalid input: ROI values must be between 0 and 2000", 400

                    # Add the value to the correct ROI
                    pregaugerois[pregauge_roi_number - 1].append(value)

        for key in request.form:
            # Check if the key starts with 'postroi'
            if key.startswith('postroi'):
                # Split the key into parts
                parts = key.split('_')

                # Check if the key has the correct format
                if len(parts) == 3:
                    # Get the ROI number and coordinate
                    postroi_number = int(parts[1])
                    coordinate = parts[2]
                    # Ensure the ROIs list has enough elements
                    while len(postrois) < postroi_number:
                        postrois.append([])

                    # Get the value from the form data and convert it to an integer
                    value = int(request.form[key])
                    # Validate the value
                    if not (0 <= value <= 2000):
                        return "Invalid input: ROI values must be between 0 and 2000", 400

                    # Add the value to the correct ROI
                    postrois[postroi_number - 1].append(value)

            # Check if the key starts with 'postgaugeroi'
            if key.startswith('postgaugeroi'):
                # Split the key into parts
                parts = key.split('_')

                # Check if the key has the correct format
                if len(parts) == 3:
                    # Get the ROI number and coordinate
                    postgauge_roi_number = int(parts[1])
                    coordinate = parts[2]

                    # Ensure the ROIs list has enough elements
                    while len(postgaugerois) < postgauge_roi_number:
                        postgaugerois.append([])

                    # Get the value from the form data and convert it to an integer
                    value = int(request.form[key])

                    # Validate the value
                    if not (0 <= value <= 2000):
                        return "Invalid input: ROI values must be between 0 and 2000", 400

                    # Add the value to the correct ROI
                    postgaugerois[postgauge_roi_number - 1].append(value)

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
            if key.startswith('picamera_led_enabled'):
                if request.form['picamera_led_enabled']:
                    config['picamera_led_enabled'] = bool(True)
                else:
                    config['picamera_led_enabled'] = bool(False)

        # Convert the lists to tuples
        prerois = [list(roi) for roi in prerois]
        pregaugerois = [list(roi) for roi in pregaugerois]
        postrois = [list(roi) for roi in postrois]
        postgaugerois = [list(roi) for roi in postgaugerois]
        config['prerois'] = prerois
        config['pregaugerois'] = pregaugerois
        config['postrois'] = postrois
        config['postgaugerois'] = postgaugerois

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
                config['pregaugeroi'] = pregaugerois

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

