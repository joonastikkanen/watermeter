import cv2
import tensorflow.keras.backend as K
import tensorflow as tf
from tensorflow.keras.preprocessing import image as image_utils
from tensorflow.keras.applications.imagenet_utils import preprocess_input
from app import load_config
import numpy as np
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
import os
import time
import math

config = load_config()
picamera_image_path = config['picamera_image_path']
prerois = config['prerois'] = [tuple(roi) for roi in config['prerois']]
pregaugerois = config['pregaugerois'] = [tuple(roi) for roi in config['pregaugerois']]
postrois = config['postrois'] = [tuple(roi) for roi in config['postrois']]
postgaugerois = config['postgaugerois'] = [tuple(roi) for roi in config['postgaugerois']]
tesseract_path = config['tesseract_path']
tesseract_oem = config['tesseract_oem']
tesseract_psm = config['tesseract_psm']
tesseract_validation_counter = int(config['tesseract_validation_counter'])
watermeter_last_value_file = config['watermeter_last_value_file']
watermeter_preview_image_path = config['watermeter_preview_image_path']
watermeter_init_value = config['watermeter_init_value']

# READ IMAGE
def read_image():
    # Load the image
    image = cv2.imread(picamera_image_path)
    def preprocess_for_model(roi):
        # Resize the image to the size expected by your model
        roi = cv2.resize(roi, (20,32))

        # Convert the image to the RGB color space
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        #roi = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)

        # Convert the image to a numpy array
        roi = image_utils.img_to_array(roi, dtype="float32")

        # Expand the dimensions of the image
        roi = np.expand_dims(roi, axis=0)

        # Preprocess the image for your model
        roi = preprocess_input(roi)

        return roi

    def read_digits(rois, image):
        digits = ''  # Initialize digits as an empty string
        # Load your trained TensorFlow model
        model = tf.keras.models.load_model('app/neuralnets/Train_CNN_Digital-Readout_Version_6.0.0.h5')
        # Process each ROI
        for x, y, w, h in rois:
            # Crop the image
            roi = image[y:y+h, x:x+w]
            roi = preprocess_for_model(roi)
            # Use your TensorFlow model to predict the digit
            digit = model.predict(roi)
            #K.clear_session()
            digit = np.argmax(digit)
            #digit = digit[0]
            digits += str(digit)
            #digits += digit.strip()  # Append the digit to the digits value
            # Print the text
            print(digits)
        return digits

    def read_gauges(gaugerois, image):
        total_gauges = ''
        # Load your trained TensorFlow model
        model = tf.keras.models.load_model('app/neuralnets/CNN_Analog-Readout_Version-6.0.1.h5')
        # Process each ROI
        for x, y, w, h in gaugerois:
            # Crop the image
            roi = image[y:y+h, x:x+w]
            roi = preprocess_for_model(roi)
            # Use your TensorFlow model to predict the digit
            gauge = model.predict(roi)
            out_sin = gauge[0][0]
            out_cos = gauge[0][1]
            #K.clear_session()
            gauge_result =  np.arctan2(out_sin, out_cos)/(2*math.pi) % 1
            gauge_result = gauge_result * 10
            # Print the text
            print(gauge_result)
        return gauge_result
    
    preroisdigits = read_digits(prerois, image)
    pregaugeroisdigits = read_gauges(pregaugerois, image)
    pre_digits = preroisdigits + pregaugeroisdigits
    print(f"pre_digits: ", pre_digits)

    postroisdigits = read_digits(postrois, image)
    postgaugeroisdigits = read_gauges(postgaugerois, image)
    post_digits = postroisdigits + postgaugeroisdigits
    print(f"postroi_digits: ", post_digits)

    total_digits = pre_digits + "." + post_digits
    print(f"total_digits: ", total_digits)

    # Wire sensor data to file
    with open(watermeter_last_value_file, 'w') as f:
        f.write(total_digits)

    # Return the value
    return total_digits

# Draw the ROIs on the image
def draw_rois_and_gauges(image_path, prerois, pregaugerois, postrois, postgaugerois, output_path):
    # Load the image
    image = cv2.imread(image_path)

    # Draw each ROI
    for x, y, w, h in prerois:
        text = "prerois"
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 255), 2)
        # Draw the text on the image
        cv2.putText(image, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # Draw each ROI
    for x, y, w, h in postrois:
        text = "postrois"
        cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
        # Draw the text on the image
        cv2.putText(image, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

    if 'value' in locals():
        print("The value variable is defined.")
        # Draw each gauge
        for x, y, w, h, value in pregaugerois:
            text = "pregaugerois"
            # Calculate the angle and position of the line
            angle = (value / 10) * 180  # Assuming the gauge range is 10
            line_length = h / 2
            line_x = x + w / 2 + line_length * np.cos(angle)
            line_y = y + h / 2 - line_length * np.sin(angle)

            # Draw the line
            cv2.line(image, (x + w // 2, y + h // 2), (int(line_x), int(line_y)), (0, 140, 255), 2)
            # Draw the text on the image
            cv2.putText(image, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 140, 255), 2)

        for x, y, w, h, value in postgaugerois:
            text = "postgaugerois"
            # Calculate the angle and position of the line
            angle = (value / 10) * 180  # Assuming the gauge range is 10
            line_length = h / 2
            line_x = x + w / 2 + line_length * np.cos(angle)
            line_y = y + h / 2 - line_length * np.sin(angle)

            # Draw the line
            cv2.line(image, (x + w // 2, y + h // 2), (int(line_x), int(line_y)), (255, 140, 0), 2)
            # Draw the text on the image
            cv2.putText(image, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 140, 0), 2)
    else:
        print("The value variable is not defined.")
        for x, y, w, h in pregaugerois:
            text = "pregaugerois"
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 140, 255), 2)
            # Draw the text on the image
            cv2.putText(image, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 140, 255), 2)

        for x, y, w, h in postgaugerois:
            text = "postgaugerois"
            cv2.rectangle(image, (x, y), (x+w, y+h), (255, 140, 0), 2)
            # Draw the text on the image
            cv2.putText(image, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 140, 0), 2)

    # Save the image
    cv2.imwrite(output_path, image)
    return True

# LOAD SENSOR DATA
def load_sensor_data():
    if not os.path.isfile(watermeter_last_value_file):
        with open(watermeter_last_value_file, 'w') as f:
            f.write(str(watermeter_init_value))
    else:
        with open(watermeter_last_value_file, 'r') as f:
            sensor_data = f.read()
    return sensor_data

def get_picamera_image_timestamp(picamera_image_path):
    if not os.path.isfile(picamera_image_path):
        picamera_image_time = "No picture yet taken"
    else:
        picamera_image_timestamp = os.path.getctime(picamera_image_path)
        picamera_image_time = time.ctime(picamera_image_timestamp)
    return picamera_image_time
