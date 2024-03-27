#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/TurboPi/')
import cv2
import time
import signal
import threading
import numpy as np
import yaml_handle
import HiwonderSDK.Board as Board
import HiwonderSDK.mecanum as mecanum
import HiwonderSDK.FourInfrared as infrared
import HiwonderSDK.Sonar as Sonar
import pandas as pd

# Initialize hardware components
car = mecanum.MecanumChassis()
sonar = Sonar.Sonar()
Board.RGB.setup(Board.RGB.RGB_BOARD)  # Setup RGB LED

# Load Haar cascade classifiers
stop_cascade = cv2.CascadeClassifier('stop_sign.xml')  # Path to stop sign cascade XML
light_cascade = cv2.CascadeClassifier('traffic_light.xml')  # Path to traffic light cascade XML


# Handle program exit
def stop_program(signum, frame):
    print("Closing...")
    car.set_velocity(0, 90, 0)  # Stop the car
    Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))  # Turn off RGB LED
    exit(0)


signal.signal(signal.SIGINT, stop_program)


# Function to detect stop signs and traffic lights in the frame
def detect_objects(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect stop signs
    stops = stop_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    for (x, y, w, h) in stops:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        print("Stop sign detected!")

    # Detect traffic lights
    lights = light_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(20, 20))
    for (x, y, w, h) in lights:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        print("Traffic light detected!")

    return frame


# Main program loop
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)  # Open the default camera (index 0)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame")
            break

        # Detect objects in the frame
        detected_frame = detect_objects(frame)

        cv2.imshow('Object Detection', detected_frame)
        if cv2.waitKey(1) == 27:  # Press ESC to exit
            break

    cap.release()
    cv2.destroyAllWindows()
