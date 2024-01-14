import os

class Config(object):
    PICAMERA_IMAGE_PATH = os.getenv('PICAMERA_IMAGE_PATH', '/run/shm/watermeter_last.jpg'),
    PICAMERA_CONFIG = os.getenv('PICAMERA_CONFIG', '{"size": (1920, 1080)}'),
    TESSERACT_PATH = os.getenv('TESSERACT_PATH', '/usr/bin/tesseract'),
    TESSERACT_CONFIG = os.getenv('TESSERACT_CONFIG', '--psm 6 -c tessedit_char_whitelist=0123456789'),
    WATERMETER_LAST_VALUE_FILE = os.getenv('WATERMETER_LAST_VALUE_FILE', '/run/shm/watermeter_last_value.txt'),
    DEBUG = False