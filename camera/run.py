#!/usr/bin/python3
#from gpiozero import LED
from time import sleep
from picamera2 import Picamera2, Preview
#led = LED(17) # LED is connected to GPIO 17 (3,3 V on a Zero)

camera = Picamera2()
preview_config = camera.create_preview_configuration(main={"size": (1920, 1080)})
camera.configure(preview_config)
# Turn on LED
#led.on()
# Turn on Camera and allow to adjust to brightness
camera.start_preview(Preview.NULL)
camera.start()
sleep(1)
# Take an image. I put in in /run/shm to not wear the SD card
metadata = camera.capture_file("/run/shm/watermeter_last.jpg")
print(metadata)
camera.close()
#led.off()
