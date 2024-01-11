#!/usr/bin/python3
from time import sleep
from picamera2 import Picamera2, Preview
from libcamera import controls
import cv2
import pytesseract
import requests
import os

picamera_image_path = os.getenv('PICAMERA_IMAGE_PATH', '/run/shm/watermeter_last.jpg')
picamera_config = os.getenv('PICAMERA_CONFIG', '{"size": (1920, 1080)}')
terraseract_path = os.getenv('TESSERACT_PATH', '/usr/bin/tesseract')
terrasact_config = os.getenv('TESSERACT_CONFIG', '--psm 6 -c tessedit_char_whitelist=0123456789')
watermeter_last_value_file = os.getenv('WATERMETER_LAST_VALUE_FILE', '/run/shm/watermeter_last_value.txt')
homeassistant_url = os.getenv('HOME_ASSISTANT_URL', 'http://10.20.30.20:8123')
homeassistant_token = os.getenv('HOME_ASSISTANT_TOKEN')

def main():
    sensor_data = load_sensor_data()
    take_picture()
    read_image()
    send_sensor_data_to_homeassistant(sensor_data)

if __name__ == '__main__':
    while True:
        main()
        sleep(300)  # Sleep for 300 seconds (5 minutes)

def load_sensor_data():
    try:
        with open(watermeter_last_value_file, 'r') as f:
            sensor_data = int(f.read())
    except FileNotFoundError:
        sensor_data = 0

    return sensor_data

def take_picture():
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
    metadata = camera.capture_file(picamera_image_path)
    camera.close()
    #led.off()
    return True

def read_image():
    # Set the path to the tesseract executable
    pytesseract.pytesseract.tesseract_cmd = terraseract_path

    # Load the image from file
    image = cv2.imread(picamera_image_path)

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use Tesseract to do OCR on the image
    sensor_data = pytesseract.image_to_string(gray_image, config=terrasact_config)
    # Wire sensor data to file
    with open('', 'w') as f:
        f.write(str(sensor_data))

    # Print the text
    print(sensor_data)

# Send the data to Home Assistant
def send_sensor_data_to_homeassistant(sensor_data):
    url = "http://{HOME_ASSISTANT_URL}/api/states/sensor.water_meter"
    headers = {
        "Authorization": "Bearer {homeassistant_token}",
        "content-type": "application/json",
    }
    data = {
        "state": sensor_data,
        "attributes": {
            "unit_of_measurement": "liters",
            "friendly_name": "Water Meter",
        }
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print("Data sent to Home Assistant successfully. Sensor data: {sensor_data}")
    else:
        print(f"Failed to send data to Home Assistant. Status code: {response.status_code}")