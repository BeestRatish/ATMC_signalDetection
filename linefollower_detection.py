#!/usr/bin/python3
# coding=utf8

import cv2
import time
import HiwonderSDK.Board as Board
import HiwonderSDK.FourInfrared as infrared
import HiwonderSDK.Sonar as Sonar

# Initialize ultrasonic sensor
sonar = Sonar.Sonar()

# Initialize infrared sensor
line = infrared.FourInfrared()

# Load cascade classifier for stop signs
stop_sign_cascade = cv2.CascadeClassifier("stop_sign.xml")

# Initialize camera
camera = cv2.VideoCapture(0)

# Global variables
car_speed = 50
obstacle_distance_threshold = (5, 10)  # Range of obstacle detection in cm
stop_duration = 3  # Duration to stop in seconds

# Function to control car movement
def move_car(direction):
    if direction == "Stop":
        Board.setMotor(-car_speed, -car_speed, -car_speed, -car_speed)  # Stop the car
        time.sleep(stop_duration)  # Stop for specified duration
        Board.setMotor(car_speed, car_speed, car_speed, car_speed)  # Resume forward motion
    elif direction == "Forward":
        Board.setMotor(car_speed, car_speed, car_speed, car_speed)  # Move the car forward

# Main loop
while True:
    ret, frame = camera.read()  # Read frame from camera
    if not ret:
        print("Error: Unable to capture frame.")
        break

    # Convert frame to grayscale for Haar cascade detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect stop signs
    stop_signs = stop_sign_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    if len(stop_signs) > 0:
        # Stop if a stop sign is detected
        move_car("Stop")
    else:
        # Measure distance using ultrasonic sensor
        distance = sonar.getDistance() / 10.0  # Distance in cm

        if obstacle_distance_threshold[0] <= distance <= obstacle_distance_threshold[1]:
            # Stop if an obstacle is detected within the threshold range
            move_car("Stop")
        else:
            # Move the car forward if no stop sign or obstacle detected
            move_car("Forward")

    # Display the frame with detection results
    cv2.imshow('Frame', frame)

    # Exit loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
camera.release()
cv2.destroyAllWindows()
Board.setMotor(0, 0, 0, 0)  # Stop the car
