#!/usr/bin/python3
# coding=utf8
import sys

sys.path.append('/home/pi/TurboPi/')
import cv2
import numpy as np
import time
import signal
import HiwonderSDK.mecanum as mecanum

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

print('''
**********************************************************
********************功能:小车前进例程 Function: Move Forward************************
**********************************************************
----------------------------------------------------------
Official website: https://www.hiwonder.com
Online mall: https://hiwonder.tmall.com
----------------------------------------------------------
Tips:
 * 按下Ctrl+C可关闭此次程序运行，若失败请多次尝试！ Press Ctrl+C to exit the program, please try few more times if fail to exit!
----------------------------------------------------------
''')

chassis = mecanum.MecanumChassis()
cap = cv2.VideoCapture(0)  # Open the default camera (index 0)

start = True


# 关闭前处理 Processing before exit
def Stop(signum, frame):
    global start

    start = False
    print('closing...')
    chassis.set_velocity(0, 90, 0)  # 关闭所有电机 Turn off all motors
    cap.release()  # Release the camera
    cv2.destroyAllWindows()  # Close OpenCV windows


signal.signal(signal.SIGINT, Stop)

if __name__ == '__main__':
    while start:
        ret, frame = cap.read()  # Read a frame from the camera
        if not ret:
            print("Error: Failed to capture frame")
            break

        cv2.imshow('Camera Feed', frame)  # Display the camera feed

        # Convert BGR image to HSV for color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define the lower and upper bounds of the green color in HSV
        lower_green = np.array([40, 40, 40])
        upper_green = np.array([80, 255, 255])

        # Create a mask for the green color
        mask = cv2.inRange(hsv, lower_green, upper_green)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) > 0:
            # Green color detected, move the car forward
            chassis.set_velocity(50, 90, 0)  # 控制机器人移动函数,线速度50(0~100)，方向角90(0~360)，偏航角速度0(-2~2)
        else:
            # No green color detected, stop the car
            chassis.set_velocity(0, 0, 0)

        key = cv2.waitKey(1)
        if key == 27:  # Press ESC to exit
            break

    chassis.set_velocity(0, 0, 0)  # 关闭所有电机 Turn off all motors
    print('Closed')
