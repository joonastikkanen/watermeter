from time import sleep
from picamera2 import Picamera2, Preview
from flask import redirect, url_for, app, send_file

def take_picture():
    picamera_config = app.config['picamera_config']
    picamera_image_path = app.config['picamera_image_path']
    camera = Picamera2()
    preview_config = camera.create_preview_configuration(main=picamera_config)
    camera.configure(preview_config)
    # Turn on LED
    #led.on()
    # Turn on Camera and allow to adjust to brightness
    camera.start_preview(Preview.NULL)
    camera.start()
    sleep(1)
    # Take an image. I put in in /run/shm to not wear the SD card
    camera.capture_file(picamera_image_path)
    camera.close()
    #led.off()
    return True

@app.route('/take_new_picture', methods=['POST'])
def take_new_picture():
    take_picture()
    return redirect(url_for('preview'))

@app.route('/last_image')
def last_image():
    picamera_image_path = app.config['picamera_image_path']
    try:
        return send_file(picamera_image_path, mimetype='image/jpeg')
    except FileNotFoundError:
        return "No image found", 404