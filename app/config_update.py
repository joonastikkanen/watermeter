from app import load_config
import yaml
from flask import request

config = load_config()

def update_config():
    try:
        # Iterate over the form data
        rois = []
        gauge_rois = []
        print(request.form)
        for key in request.form:
            # Check if the key starts with 'roi'
            if key.startswith('roi'):
                # Split the key into parts
                parts = key.split('_')

                # Check if the key has the correct format
                if len(parts) == 3:
                    # Get the ROI number and coordinate
                    roi_number = int(parts[1])
                    coordinate = parts[2]
                    # Ensure the ROIs list has enough elements
                    while len(rois) < roi_number:
                        rois.append([])

                    # Get the value from the form data and convert it to an integer
                    value = int(request.form[key])
                    # Validate the value
                    if not (0 <= value <= 2000):
                        return "Invalid input: ROI values must be between 0 and 2000", 400

                    # Add the value to the correct ROI
                    rois[roi_number - 1].append(value)
            # Check if the key starts with 'gaugeroi'
            if key.startswith('gaugeroi'):
                # Split the key into parts
                parts = key.split('_')

                # Check if the key has the correct format
                if len(parts) == 3:
                    # Get the ROI number and coordinate
                    gauge_roi_number = int(parts[1])
                    coordinate = parts[2]

                    # Ensure the ROIs list has enough elements
                    while len(gauge_rois) < gauge_roi_number:
                        gauge_rois.append([])

                    # Get the value from the form data and convert it to an integer
                    value = int(request.form[key])

                    # Validate the value
                    if not (0 <= value <= 2000):
                        return "Invalid input: ROI values must be between 0 and 2000", 400

                    # Add the value to the correct ROI
                    gauge_rois[gauge_roi_number - 1].append(value)

        # Convert the lists to tuples

        rois = [list(roi) for roi in rois]
        gauge_rois = [list(roi) for roi in gauge_rois]
        config['rois'] = rois
        config['gauge_rois'] = gauge_rois
        # Update more values here
        # Write the updated configuration to the YAML file
        with open('config.yaml', 'w') as file:
            yaml.dump(config, file, default_flow_style=None)
        return True
    except ValueError:
        return "Invalid input: could not convert data to an integer", 400
