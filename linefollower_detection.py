#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/TurboPi/')
import time
import signal
import HiwonderSDK.mecanum as mecanum
import cv2
import numpy as np

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

print('''
**********************************************************
********************功能:小车前进例程 Function: Move Forward************************
**********************************************************
----------------------------------------------------------
Official website:https://www.hiwonder.com
Online mall:https://hiwonder.tmall.com
----------------------------------------------------------
Tips:
 * 按下Ctrl+C可关闭此次程序运行，若失败请多次尝试！ Press Ctrl+C to exit the program, please try few more times if fail to exit!
----------------------------------------------------------
''')

chassis = mecanum.MecanumChassis()
start = True

# Function to detect green color in an image
def detect_green(frame):
    # Convert the frame from BGR to HSV color space
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define the lower and upper bounds for green color in HSV
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])

    # Create a mask to isolate green color
    mask = cv2.inRange(hsv_frame, lower_green, upper_green)

    # Apply morphological operations to remove noise
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Check if any contour (green area) is detected
    if len(contours) > 0:
        return True
    else:
        return False

# Signal handler to stop the program
def Stop(signum, frame):
    global start
    start = False
    print('Closing...')
    chassis.set_velocity(0, 0, 0)  # Turn off all motors

# Set up signal handling
signal.signal(signal.SIGINT, Stop)

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)  # Open the default camera (usually camera index 0)

    while start:
        ret, frame = cap.read()  # Read a frame from the camera

        if not ret:
            print('Error capturing frame')
            break

        # Check if green color is detected in the frame
        if detect_green(frame):
            chassis.set_velocity(50, 90, 0)  # Move forward if green color is detected
        else:
            chassis.set_velocity(0, 0, 0)  # Stop if green color is not detected

        time.sleep(0.1)  # Wait for a short duration between frame processing

    chassis.set_velocity(0, 0, 0)  # Turn off all motors
    print('Closed')
    cap.release()  # Release the camera
    cv2.destroyAllWindows()  # Close OpenCV windows
