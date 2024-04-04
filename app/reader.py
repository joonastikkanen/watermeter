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
from PIL import Image
from decimal import Decimal, getcontext
import boto3
import base64
import os
import time
import datetime
import math

config = load_config()
picamera_image_path = config['picamera_image_path']
prerois = config['prerois'] = [tuple(roi) for roi in config['prerois']]
pregaugerois = config['pregaugerois'] = [tuple(roi) for roi in config['pregaugerois']]
postrois = config['postrois'] = [tuple(roi) for roi in config['postrois']]
postgaugerois = config['postgaugerois'] = [tuple(roi) for roi in config['postgaugerois']]
watermeter_last_value_file = config['watermeter_last_value_file']
watermeter_preview_image_path = config['watermeter_preview_image_path']
watermeter_init_value = config['watermeter_init_value']
aws_use_rekognition_api = config['aws_use_rekognition_api']
aws_profile = config["aws_profile"]
aws_region = config["aws_region"]
session = boto3.Session(profile_name=aws_profile, region_name=aws_region)

# READ IMAGE
def read_image():
    """
    Reads an image, processes it, and returns the total digits read from the image.

    Returns:
        str: The total digits read from the image.
    """
    # Load the image
    image = cv2.imread(picamera_image_path)

    def read_digits_using_aws(prerois, postrois, picamera_image_path, session):
        getcontext().prec = 25
        regions_of_interest = []
        rois = prerois + postrois
        with Image.open(picamera_image_path) as img:
            # Get the width and height
            image_width, image_height = img.size
        for roi in rois:
            # x, y, w, h
            topleft_col, topleft_row, width, height = roi
            width_pos = Decimal(width) / Decimal(image_width)
            height_pos = Decimal(height) / Decimal(image_height)
            left_pos = Decimal(topleft_col) / Decimal(image_width)
            top_pos = Decimal(topleft_row) / Decimal(image_height)
            region = {
                "BoundingBox": {
                    "Width": float(width_pos),
                    "Height": float(height_pos),
                    "Left": float(left_pos),
                    "Top": float(top_pos),
                }
            }
            regions_of_interest.append(region)
        print("Regions of interest: " + str(regions_of_interest))
        client = session.client("rekognition")

        # Open the image file in binary mode, encode it to base64
        with open(picamera_image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

        response = client.detect_text(
            Image={
                "Bytes": base64.b64decode(encoded_image),
            },
            Filters={"RegionsOfInterest": regions_of_interest},
        )

        text_detections = response["TextDetections"]
        # Filter out the detections that are not digits and confidence is more than 90
        digit_detections = [
            d["DetectedText"]
            for d in text_detections
            if d["DetectedText"].isdigit() and d["Type"] == "WORD" and d["Confidence"] > 0
        ]
 
        print(digit_detections)

        digits = ""
        preroisdigits = ""
        postroisdigits = ""

        for digit in digit_detections:
            digits += str(digit)
            print(digits)

        preroisdigits = digits[:len(postrois)]
        print("preroisdigits: ", preroisdigits)
        postroisdigits = digits[len(prerois):]
        print("postroisdigits: ", postroisdigits)

        return preroisdigits, postroisdigits

    def preprocess_for_model(roi, roi_resize_h, roi_resize_w):
        # Resize the image to the size expected by your model
        roi = cv2.resize(roi, (roi_resize_h,roi_resize_w))

        # Convert the image to the RGB color space
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

        # Convert the image to a numpy array
        roi = image_utils.img_to_array(roi, dtype="float32")

        # Expand the dimensions of the image
        roi = np.expand_dims(roi, axis=0)

        # Preprocess the image for your model
        roi = preprocess_input(roi)

        return roi

    def read_digits(rois, image):
        last_value = None;
        #global last_value  # Use the global last value
        digits = ''  # Initialize digits as an empty string
        # Load your trained TensorFlow model
        interpreter = tf.lite.Interpreter(model_path='app/neuralnets/dig1410s3.tflite')
        interpreter.allocate_tensors()

        # Get input and output tensors.
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        # Process each ROI
        for x, y, w, h in rois:
            last_digit = None;
            # Crop the image
            roi = image[y:y+h, x:x+w]
            # Save the image for future neural networks
            date = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
            #save_roi = cv2.imwrite('/home/joonas/rois/digit-' + date + '.jpg', roi)
            roi = preprocess_for_model(roi, roi_resize_h=20, roi_resize_w=32)
            # Use your TensorFlow model to predict the digit
            K.clear_session()
            # Print the text
            # Set the value of the input tensor
            interpreter.set_tensor(input_details[0]['index'], roi)

            # Run the computation
            interpreter.invoke()

            # Get the output tensor
            digit = interpreter.get_tensor(output_details[0]['index'])

            # Check if the digit is 10
            if last_digit is not None and digit == 10:
                # If the digit is 10
                print("digit read as 10, the last_value will be set as digit")
                digit = last_value

            # Update the last value
            last_digit = digit

            # Add the predicted digit to the string of digits
            digits += str(np.argmax(digit))

            print(digits)
        # Convert the string of digits to an integer
        value = int(digits)

        # Check if the value has changed drastically
        if last_value is not None and abs(int(value) - last_value) > 10:
            # If the value has changed drastically, return the last value
            return last_value

        # Update the last value
        last_value = int(value)

        # Return the value
        return digits

    def read_gauges(gaugerois, image):
        total_gauges = ''
        # Load your trained TensorFlow model
        model = tf.keras.models.load_model('app/neuralnets/CNN_Analog-Readout_Version-6.0.1.h5')
        # Process each ROI
        for x, y, w, h in gaugerois:
            # Crop the image
            roi = image[y:y+h, x:x+w]
            roi = preprocess_for_model(roi, roi_resize_h=32, roi_resize_w=32)
            # Use your TensorFlow model to predict the digit
            gauge = model.predict(roi)
            out_sin = gauge[0][0]
            out_cos = gauge[0][1]
            K.clear_session()
            result_gauge = np.arctan2(out_sin, out_cos)/(2*math.pi) % 1
            result_gauge = result_gauge * 10
            total_gauges += str(result_gauge).split('.', 1)[0]
            # Print the text
            print(total_gauges)
        return total_gauges

    def read_rois(prerois, pregaugerois, postrois, postgaugerois, image):
        aws_use_rekognition_api = config['aws_use_rekognition_api']
        # Read the digits from the image
        if aws_use_rekognition_api:
            preroisdigits, postroisdigits = read_digits_using_aws(prerois, postrois, watermeter_preview_image_path, session)

        else:
            preroisdigits = str(read_digits(prerois, image))
            postroisdigits = str(read_digits(postrois, image))

        pregaugeroisdigits = str(read_gauges(pregaugerois, image))
        pre_digits = preroisdigits + pregaugeroisdigits
        print(f"pre_digits: ", pre_digits)

        postgaugeroisdigits = str(read_gauges(postgaugerois, image))
        post_digits = postroisdigits + postgaugeroisdigits
        print(f"postroi_digits: ", post_digits)

        total_digits = pre_digits + "." + post_digits
        print(f"total_digits: ", total_digits)

        # Return the value
        return total_digits

    total_digits = read_rois(prerois, pregaugerois, postrois, postgaugerois, image)
    # Wire sensor data to file
    with open(watermeter_last_value_file, 'w') as f:
        f.write(total_digits)

# Draw the ROIs on the image
def draw_rois_and_gauges(image_path, prerois, pregaugerois, postrois, postgaugerois, output_path):
    """
    Draw regions of interest (ROIs) and gauges on an image.

    Args:
        image_path (str): The path to the input image.
        prerois (list): A list of tuples representing the pre-ROIs. Each tuple contains the (x, y, width, height) coordinates of a ROI.
        pregaugerois (list): A list of tuples representing the pre-gauge ROIs. Each tuple contains the (x, y, width, height) coordinates of a gauge ROI.
        postrois (list): A list of tuples representing the post-ROIs. Each tuple contains the (x, y, width, height) coordinates of a ROI.
        postgaugerois (list): A list of tuples representing the post-gauge ROIs. Each tuple contains the (x, y, width, height) coordinates of a gauge ROI.
        output_path (str): The path to save the output image.

    Returns:
        bool: True if the image was successfully saved, False otherwise.
    """
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

    for x, y, w, h in pregaugerois:
        text = "pregaugerois"
        d = 2
        d_eclipse = 1
        cv2.rectangle(image,(x-d,y-d),(x+w+2*d,y+h+2*d),(0,255,0),d)
        xct = int(x+w/2)+1
        yct = int(y+h/2)+1
        cv2.line(image,(x,yct),(x+w+5,yct),(0,140,255),2)
        cv2.line(image,(xct,y),(xct,y+h),(0,140,255),2)
        cv2.ellipse(image, (xct, yct), (int(w/2)+2*d_eclipse, int(h/2)+2*d_eclipse), 0, 0, 360, (0,140,255), d_eclipse)
        cv2.putText(image, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 140, 255), 2)

    for x, y, w, h in postgaugerois:
        text = "postgaugerois"
        d = 2
        d_eclipse = 1
        cv2.rectangle(image,(x-d,y-d),(x+w+2*d,y+h+2*d),(255,140,0),d)
        xct = int(x+w/2)+1
        yct = int(y+h/2)+1
        cv2.line(image,(x,yct),(x+w+5,yct),(255,140,0),2)
        cv2.line(image,(xct,y),(xct,y+h),(255,140,0),2)
        cv2.ellipse(image, (xct, yct), (int(w/2)+2*d_eclipse, int(h/2)+2*d_eclipse), 0, 0, 360, (255,140,0), d_eclipse)
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
    """
    Get the timestamp of a PiCamera image.

    Args:
        picamera_image_path (str): The path to the PiCamera image file.

    Returns:
        str: The timestamp of the PiCamera image in a human-readable format.

    """
    if not os.path.isfile(picamera_image_path):
        picamera_image_time = "No picture yet taken"
    else:
        picamera_image_timestamp = os.path.getctime(picamera_image_path)
        picamera_image_time = time.ctime(picamera_image_timestamp)
    return picamera_image_time
