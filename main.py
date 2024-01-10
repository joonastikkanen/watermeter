#!/usr/bin/python3
from time import sleep
from picamera2 import Picamera2, Preview
from libcamera import controls
import cv2
import pytesseract

camera = Picamera2()
preview_config = camera.create_preview_configuration(main={"size": (1920, 1080)})
camera.configure(preview_config)
camera.start_preview(Preview.QTGL)
camera.start()
#camera.set_controls({"AfMode": controls.AfModeEnum.Continuous})
sleep(300)
camera.close()

# Set the path to the tesseract executable
# On Windows, this is typically 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# Load the image from file
image = cv2.imread('image.png')

# Convert the image to grayscale
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Use Tesseract to do OCR on the image
text = pytesseract.image_to_string(gray_image, config='--psm 6 -c tessedit_char_whitelist=0123456789')

# Print the text
print(text)