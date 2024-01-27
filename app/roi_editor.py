import cv2
import numpy as np

config = load_config()
# Convert the lists to tuples
picamera_image_path = config['picamera_image_path']

# Initialize the list of rectangles and boolean indicating
# whether cropping is being performed or not
rectangles = []
current_rectangle = []
cropping = False

def click_and_crop(event, x, y, flags, param, picamera_image_path):
    # grab references to the global variables
    global rectangles, current_rectangle, cropping

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being
    # performed
    if event == cv2.EVENT_LBUTTONDOWN:
        current_rectangle = [(x, y)]
        cropping = True

    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        # record the ending (x, y) coordinates
        current_rectangle.append((x, y))
        cropping = False # cropping is finished

        # draw a rectangle around the region of interest
        cv2.rectangle(image, current_rectangle[0], current_rectangle[1], (0, 255, 0), 2)
        cv2.imshow("image", image)
        rectangles.append(tuple(current_rectangle))

# load the image, clone it, and setup the mouse callback function
image = cv2.imread(picamera_image_path)
clone = image.copy()
cv2.namedWindow("image")
cv2.setMouseCallback("image", click_and_crop)

# keep looping until the 'q' key is pressed
while True:
    # display the image and wait for a keypress
    cv2.imshow("image", image)
    key = cv2.waitKey(1) & 0xFF

    # if the 'r' key is pressed, reset the cropping region
    if key == ord("r"):
        image = clone.copy()

    # if the 'c' key is pressed, break from the loop
    elif key == ord("c"):
        break

# close all open windows
cv2.destroyAllWindows()

# print all rectangles
for rect in rectangles:
    print(rect)
