from flask import send_file, redirect, url_for, render_template
from app import app, load_config
from app.reader import load_sensor_data, read_image, draw_rois_and_gauges
from app.camera import take_picture, get_picamera_image_timestamp
from app.config_update import update_config

config = load_config()
# Convert the lists to tuples
picamera_image_path = config['picamera_image_path']
picamera_led_enabled = config['picamera_led_enabled']
picamera_led_brightness = config['picamera_led_brightness']
picamera_image_brightness = config['picamera_image_brightness']
picamera_image_contrast = config['picamera_image_contrast']
picamera_image_rotate = config['picamera_image_rotate']
prerois = config['prerois'] = [tuple(roi) for roi in config['prerois']]
pregaugerois = config['pregaugerois'] = [tuple(roi) for roi in config['pregaugerois']]
postrois = config['postrois'] = [tuple(roi) for roi in config['postrois']]
postgaugerois = config['postgaugerois'] = [tuple(roi) for roi in config['postgaugerois']]
watermeter_preview_image_path = config['watermeter_preview_image_path']
watermeter_job_schedule = config['watermeter_job_schedule']

# ROUTES
@app.route('/')
def home():
    try:
        sensor_data = load_sensor_data()
        return sensor_data
    except FileNotFoundError:
        return "Failed to load sensor data", 404


@app.route('/take_new_picture', methods=['POST'])
def take_new_picture_route():
    try:
        config = load_config()
        picamera_led_enabled = config['picamera_led_enabled']
        picamera_led_brightness = config['picamera_led_brightness']
        picamera_image_rotate = config['picamera_image_rotate']
        take_picture(picamera_led_enabled, picamera_led_brightness, picamera_image_rotate)
    except FileNotFoundError:
        return "Failed to take new picture", 404

@app.route('/preview/picamera_image')
def picamera_image():
    try:
        return send_file(picamera_image_path, mimetype='image/jpeg')
    except FileNotFoundError:
        return "No image found", 404


@app.route('/read_image', methods=['POST'])
def read_image_route():
    try:
        read_image(picamera_image_brightness, picamera_image_contrast)
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
        draw_rois_and_gauges(picamera_image_path, prerois, pregaugerois, postrois, postgaugerois, watermeter_preview_image_path,  )
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
        picamera_led_brightness = config['picamera_led_brightness']
        picamera_image_brightness = config['picamera_image_brightness']
        picamera_image_contrast = config['picamera_image_contrast']
        picamera_image_rotate = config['picamera_image_rotate']
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
                               watermeter_job_schedule=watermeter_job_schedule
                               )
    except FileNotFoundError:
        return "Failed to render preview page", 404

@app.route('/update_config', methods=['POST'])
def update_config_route():
    try:
        update_config()
        take_new_picture_route()
        read_image_route()
        draw_rois_route()
        return redirect(url_for('preview'))
    except FileNotFoundError:
        return "Failed to update config", 404
