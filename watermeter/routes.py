from flask import Blueprint, render_template_string, redirect, url_for, send_file
from app import app
from camera import take_picture
from reader import read_image, load_sensor_data

bp = Blueprint('routes', __name__)

@bp.route('/')
def home():
    sensor_data = load_sensor_data()
    return sensor_data

@bp.route('/take_new_picture', methods=['POST'])
def take_new_picture():
    take_picture()
    return redirect(url_for('preview'))

@bp.route('/last_image')
def last_image():
    picamera_image_path = app.config['picamera_image_path']
    try:
        return send_file(picamera_image_path, mimetype='image/jpeg')
    except FileNotFoundError:
        return "No image found", 404

@bp.route('/preview')
def preview():
    take_picture()
    read_image()
    try:
        return render_template_string("""
            <img src="{{ url_for('last_image') }}" alt="Last image">
            <form action="{{ url_for('take_new_picture') }}" method="post">
                <button type="submit">Take New Picture</button><br>
                Sensor data: {{ url_for('root') }}
            </form>
        """)
    except FileNotFoundError:
        return "No image found", 404
