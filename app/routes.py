from flask import send_file, redirect, url_for, render_template, request, jsonify
from flask_apscheduler import APScheduler
import subprocess
from app import app, load_config
from app.reader import load_sensor_data, read_image, draw_rois_and_gauges, get_picamera_image_timestamp
from app.config_update import update_config, update_roi_editor_config

config = load_config()
# Convert the lists to tuples
picamera_image_path = config['picamera_image_path']
picamera_photo_height = config['picamera_photo_height']
picamera_photo_width = config['picamera_photo_width']
prerois = config['prerois'] = [tuple(roi) for roi in config['prerois']]
pregaugerois = config['pregaugerois'] = [tuple(roi) for roi in config['pregaugerois']]
postrois = config['postrois'] = [tuple(roi) for roi in config['postrois']]
postgaugerois = config['postgaugerois'] = [tuple(roi) for roi in config['postgaugerois']]
watermeter_preview_image_path = config['watermeter_preview_image_path']
watermeter_job_schedule = config['watermeter_job_schedule']

@app.route('/')
def home():
    """
    This function handles the home route of the application.
    
    It loads the sensor data and returns it as a response.
    If the sensor data file is not found, it returns a 404 error.
    """
    try:
        sensor_data = load_sensor_data()
        return sensor_data
    except FileNotFoundError:
        return "Failed to load sensor data", 404

@app.route('/take_new_picture', methods=['POST'])
def take_new_picture_route():
    """
    Endpoint for taking a new picture.

    This route runs a Python script called 'camera.py' to capture a new picture.
    It uses the subprocess module to execute the script as a separate process.

    Returns:
        - True if the picture was taken successfully.
        - Error message with status code 404 if the 'camera.py' script is not found.
    """
    try:
        # Define the command to run the Python script
        command = ["python3.11", "./app/camera.py"]
        # Run the command
        subprocess.run(command, check=True)
        return True
    except FileNotFoundError:
        return "Failed to take new picture", 404

@app.route('/preview/picamera_image/watermeter_last.jpg')
def picamera_image():
    """
    Endpoint for retrieving the last captured image from the PiCamera.

    Returns:
        If the image is found, the image file is returned.
        If the image is not found, a 404 error message is returned.
    """
    try:
        return send_file(picamera_image_path)
    except FileNotFoundError:
        return "No image found", 404


@app.route('/preview/roi_editor')
def roi_editor_route():
    """
    Route handler for '/preview/roi_editor' endpoint.
    This function loads the configuration, retrieves the necessary parameters from the request arguments,
    and renders the 'roi_editor.html' template with the retrieved parameters.

    Returns:
        The rendered 'roi_editor.html' template with the retrieved parameters.
        If the configuration file is not found, returns a 404 error message.
    """
    try:
        config = load_config()
        picamera_photo_height = config['picamera_photo_height']
        picamera_photo_width = config['picamera_photo_width']
        roi_id = None
        roi_name = None
        roi_rgb_colors = None
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
    """
    Route handler for submitting ROIs (Regions of Interest) in the preview page.

    This function updates the ROI editor configuration, reads the image, draws the ROIs, and redirects to the preview page.

    Returns:
        A redirect response to the preview page.
    """
    update_roi_editor_config()
    read_image_route()
    draw_rois_route()
    return redirect(url_for('preview'))

@app.route('/read_image', methods=['POST'])
def read_image_route_post():
    """
    Route handler for the '/read_image' endpoint with POST method.
    
    This function calls the 'read_image_route' function and redirects the user to the 'preview' endpoint.
    If the image file is not found, it returns a 404 error message.
    """
    try:
        read_image_route()
        return redirect(url_for('preview'))
    except FileNotFoundError:
        return "Failed to read data from image", 404

def read_image_route():
    """
    This function reads an image and handles any FileNotFoundError that may occur.

    Returns:
        A tuple containing a string message and an HTTP status code.
    """
    try:
        read_image()
    except FileNotFoundError:
        return "Failed to read data from image", 404

@app.route('/draw_rois', methods=['POST'])
def draw_rois_route():
    """
    Endpoint for drawing ROI areas and gauges on an image.

    This function loads the configuration, retrieves the ROI areas and gauge positions,
    and then calls the 'draw_rois_and_gauges' function to draw the ROIs and gauges on
    the image specified in the configuration.

    Returns:
        If the image file is not found, returns a string "Failed to draw ROI areas to image"
        with a status code of 404.
    """
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

@app.route('/preview/image/watermeter_preview.jpg')
def preview_image():
    """
    Endpoint for retrieving the preview image of the watermeter.

    Returns:
        If the image is found, the image file will be returned.
        If the image is not found, a 404 error message will be returned.
    """
    try:
        return send_file(watermeter_preview_image_path)
    except FileNotFoundError:
        return "No image found", 404

@app.route('/preview')
def preview():
    """
    Renders the preview page with the configured settings and sensor data.

    Returns:
        The rendered preview page with the following variables:
        - sensor_data: The sensor data loaded from the sensor.
        - prerois: The pre-defined regions of interest.
        - pregaugerois: The pre-defined gauge regions of interest.
        - postrois: The post-defined regions of interest.
        - postgaugerois: The post-defined gauge regions of interest.
        - capture_timestamp: The timestamp of the captured image.
        - picamera_led_enabled: The status of the PiCamera LED.
        - picamera_led_brightness: The brightness of the PiCamera LED.
        - picamera_image_brightness: The brightness of the captured image.
        - picamera_image_contrast: The contrast of the captured image.
        - picamera_image_rotate: The rotation angle of the captured image.
        - picamera_image_focus_position: The focus position of the captured image.
        - picamera_image_focus_manual_enabled: The status of manual focus for the captured image.
        - watermeter_job_schedule: The schedule for the watermeter job.
        - picamera_image_sharpness: The sharpness of the captured image.
        - picamera_image_denoise_mode: The denoise mode of the captured image.
        - picamera_buffer_count: The buffer count for the PiCamera.
        - picamera_photo_height: The height of the captured photo.
        - picamera_photo_width: The width of the captured photo.
        - aws_use_rekognition_api: The status of using the AWS Rekognition API.
        - aws_profile: The AWS profile used for the Rekognition API.
        - aws_region: The AWS region used for the Rekognition API.
    """
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
        aws_use_rekognition_api = config['aws_use_rekognition_api']
        aws_profile = config['aws_profile']
        aws_region = config['aws_region']
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
                               picamera_photo_height=picamera_photo_height,
                               picamera_photo_width=picamera_photo_width,
                               aws_use_rekognition_api=aws_use_rekognition_api,
                               aws_profile=aws_profile,
                               aws_region=aws_region
                               )
    except FileNotFoundError:
        return "Failed to render preview page", 404

# Global variable to track if a request is being processed
is_request_being_processed = False

@app.route('/update_config', methods=['POST'])
def update_config_route():
    """
    Update the configuration and process the request.

    This route is triggered when a POST request is made to '/update_config'.
    It first checks if a request is already being processed. If so, it returns an error response.
    Otherwise, it sets the global variable 'is_request_being_processed' to True and proceeds to update the configuration,
    take a new picture, read the image, and draw regions of interest (ROIs).
    After processing the request, it sets 'is_request_being_processed' back to False.

    Returns:
        - If the configuration update is successful, it redirects to the 'preview' route.
        - If the configuration file is not found, it returns a 404 error message.
    """
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

def run_schedule():
    """
    Runs the scheduled tasks for taking a new picture and reading the image.

    This function calls the `take_new_picture_route` function to capture a new image and then
    calls the `read_image` function to process the captured image.

    Returns:
        None
    """
    take_new_picture_route()
    read_image()

scheduler = APScheduler()
scheduler.start()

watermeter_job_schedule = int(watermeter_job_schedule)

# Schedule the job to run every day at 10:30am
scheduler.add_job(id='run_schedule', func=run_schedule, trigger='interval', minutes=watermeter_job_schedule)
