#!/usr/bin/python3
from time import sleep
from picamera2 import Picamera2, Preview
from libcamera import controls

camera = Picamera2()
preview_config = camera.create_preview_configuration(main={"size": (1920, 1080)})
camera.configure(preview_config)
camera.start_preview(Preview.QTGL)
camera.start()
#camera.set_controls({"AfMode": controls.AfModeEnum.Continuous})
sleep(300)
camera.close()
