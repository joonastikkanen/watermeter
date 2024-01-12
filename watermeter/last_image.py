import os
from flask import send_file, app

@app.route('/last_image')
def last_image():
    picamera_image_path = app.config['picamera_image_path']
    try:
        return send_file(picamera_image_path, mimetype='image/jpeg')
    except FileNotFoundError:
        return "No image found", 404