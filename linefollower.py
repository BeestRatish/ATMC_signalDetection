#!/usr/bin/python3
# coding=utf8
import sys

sys.path.append('/home/pi/TurboPi/')
import cv2
import time
import math
import signal
import Camera
import threading
import numpy as np
import yaml_handle
import HiwonderSDK.Board as Board
import HiwonderSDK.mecanum as mecanum
import HiwonderSDK.FourInfrared as infrared

# 红绿灯行驶 Traffic light Recognition

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

car = mecanum.MecanumChassis()
line = infrared.FourInfrared()

servo1 = 1500
servo2 = 1500
car_stop = False
color_list = []
size = (640, 480)
__isRunning = False
detect_color = 'None'
target_color = ('red', 'green')

lab_data = None
servo_data = None


def load_config():
    global lab_data, servo_data

    lab_data = yaml_handle.get_yaml_data(yaml_handle.lab_file_path)
    servo_data = yaml_handle.get_yaml_data(yaml_handle.servo_file_path)


# 初始位置 Initial Position
def initMove():
    car.set_velocity(0, 90, 0)
    Board.setPWMServoPulse(1, servo1, 1000)
    Board.setPWMServoPulse(2, servo2, 1000)


# 设置蜂鸣器 Set Buzzer
def setBuzzer(timer):
    Board.setBuzzer(0)
    Board.setBuzzer(1)
    time.sleep(timer)
    Board.setBuzzer(0)


range_rgb = {
    'red': (0, 0, 255),
    'blue': (255, 0, 0),
    'green': (0, 255, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
}

draw_color = range_rgb["black"]


# 变量重置 Reset Variables
def reset():
    global car_stop
    global color_list
    global detect_color
    global start_pick_up
    global servo1, servo2

    car_stop = False
    color_list = []
    detect_color = 'None'
    servo1 = servo_data['servo1']
    servo2 = servo_data['servo2']


# app初始化调用 APP Initialization
def init():
    print("LineFollower Init")
    load_config()
    reset()
    initMove()


# app开始玩法调用 App starts calling game program
def start():
    global __isRunning
    reset()
    __isRunning = True
    car.set_velocity(35, 90, 0)
    print("LineFollower Start")


# app停止玩法调用 App stops calling game program
def stop():
    global car_stop
    global __isRunning
    car_stop = True
    __isRunning = False
    set_rgb('None')
    print("LineFollower Stop")


# app退出玩法调用  Exit the game
def exit():
    global car_stop
    global __isRunning
    car_stop = True
    __isRunning = False
    set_rgb('None')
    print("LineFollower Exit")


def setTargetColor(color):
    global target_color

    target_color = color
    return (True, ())


# 设置扩展板的RGB灯颜色使其跟要追踪的颜色一致 The color of RGB light on expansion board is set to consistent with the tracked color
def set_rgb(color):
    if color == "red":
        Board.RGB.setPixelColor(0, Board.PixelColor(255, 0, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(255, 0, 0))
        Board.RGB.show()
    elif color == "green":
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 255, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 255, 0))
        Board.RGB.show()
    elif color == "blue":
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 255))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 255))
        Board.RGB.show()
    else:
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
        Board.RGB.show()


# 找出面积最大的轮廓  Find the maximum contour
# 参数为要比较的轮廓的列表 Parameters are the list of contours to be compared
def getAreaMaxContour(contours):
    contour_area_temp = 0
    contour_area_max = 0
    area_max_contour = None

    for c in contours:  # 历遍所有轮廓 Loop over the contours
        contour_area_temp = math.fabs(cv2.contourArea(c))  # 计算轮廓面积 Calculate the contour area
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp > 300:  # 只有在面积大于300时，最大面积的轮廓才是有效的，以过滤干扰 Only when the area is greater than 300, the maximum contour takes effect to filter the interference
                area_max_contour = c

    return area_max_contour, contour_area_max  # 返回最大的轮廓 Return the maximum contour


def move():
    global car_stop
    global __isRunning
    global detect_color

    while True:
        if __isRunning:
            if detect_color != 'red':
                set_rgb(detect_color)  # Set RGB color based on detected color
                sensor_data = line.readData()  # Read sensor data

                # Check sensor data to determine robot movement
                if sensor_data[1] and sensor_data[2]:
                    car.set_velocity(35, 90, 0)  # Move forward
                    car_stop = True
                elif sensor_data[1]:
                    car.set_velocity(35, 90, 0.03)  # Turn slightly right
                    car_stop = True
                elif sensor_data[2]:
                    car.set_velocity(35, 90, -0.03)  # Turn slightly left
                    car_stop = True
                else:
                    if car_stop:
                        car.set_velocity(0, 90, 0)  # Stop moving
                        car_stop = False
                    time.sleep(0.01)

                # If both sensors detect the line or the robot is picked up, stop moving
                if sensor_data[1] and sensor_data[2]:
                    if car_stop:
                        car.set_velocity(0, 90, 0)
                        car_stop = False
                    time.sleep(0.01)

            else:  # Red color detected
                if car_stop:
                    setBuzzer(0.1)  # Sound the buzzer for 0.1 seconds
                    set_rgb(detect_color)  # Set RGB color to red
                    car.set_velocity(0, 90, 0)  # Stop moving
                    car_stop = False
                time.sleep(0.01)

        else:
            if car_stop:
                car.set_velocity(0, 90, 0)  # Stop moving
                car_stop = False
            time.sleep(0.01)


# 运行子线程 Run child thread
th = threading.Thread(target=move)
th.setDaemon(True)
th.start()


# 机器人图像处理 Image processing
def run(img):
    global __isRunning
    global detect_color, draw_color, color_list

    if not __isRunning:  # 检测是否开启玩法，没有开启则返回原图像 Detect whether the game is started, if not, the orginal image will be returned
        return img

    img_copy = img.copy()
    img_h, img_w = img.shape[:2]

    frame_resize = cv2.resize(img_copy, size, interpolation=cv2.INTER_NEAREST)
    frame_gb = cv2.GaussianBlur(frame_resize, (3, 3), 3)
    frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # 将图像转换到LAB空间 Convert image into LAB space

    max_area = 0
    color_area_max = None
    areaMaxContour_max = 0
    for i in target_color:
        if i in lab_data:
            frame_mask = cv2.inRange(frame_lab,
                                     (lab_data[i]['min'][0],
                                      lab_data[i]['min'][1],
                                      lab_data[i]['min'][2]),
                                     (lab_data[i]['max'][0],
                                      lab_data[i]['max'][1],
                                      lab_data[i]['max'][
                                          2]))  # 对原图像和掩模进行位运算 Bitwise operation of the original image and mask
            opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))  # 开运算 Opening
            closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))  # 闭运算 Closing
            contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # 找出轮廓 Find contour
            areaMaxContour, area_max = getAreaMaxContour(contours)  # 找出最大轮廓 Find the maximum contour
            if areaMaxContour is not None:
                if area_max > max_area:  # 找最大面积 Find the maximum area
                    max_area = area_max
                    color_area_max = i
                    areaMaxContour_max = areaMaxContour
    if max_area > 2500:  # 有找到最大面积 The maximum area is found
        rect = cv2.minAreaRect(areaMaxContour_max)
        box = np.int0(cv2.boxPoints(rect))
        cv2.drawContours(img, [box], -1, range_rgb[color_area_max], 2)

        if color_area_max == 'red':  # 红色最大 Red occupies the maxmium area
            color = 1
        elif color_area_max == 'green':  # 绿色最大 Green occupies the maxmium area
            color = 2
        else:
            color = 0
        color_list.append(color)

        if len(color_list) == 3:  # 多次判断  Multiple judgements
            color = np.mean(np.array(color_list))  # 取平均值 Take average
            color_list = []
            start_pick_up = True
            if color == 1:
                detect_color = 'red'
                draw_color = range_rgb["red"]
            elif color == 2:
                detect_color = 'green'
                draw_color = range_rgb["green"]
            else:
                detect_color = 'None'
                draw_color = range_rgb["black"]
    else:
        detect_color = 'None'
        draw_color = range_rgb["black"]

    cv2.putText(img, "Color: " + detect_color, (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, draw_color,
                2)  # 把检测到的颜色打印在画面上

    return img


# 关闭前处理 Processing before exit
def manualcar_stop(signum, frame):
    global __isRunning

    print('关闭中...')
    __isRunning = False
    car.set_velocity(0, 90, 0)  # 关闭所有电机 Turn off all motors


if __name__ == '__main__':
    init()
    start()
    camera = Camera.Camera()
    camera.camera_open(correction=True)  # 开启畸变矫正,默认不开启 Enable distortion correction which is not enabled by default
    signal.signal(signal.SIGINT, manualcar_stop)
    while __isRunning:
        img = camera.frame
        if img is not None:
            frame = img.copy()
            Frame = run(frame)
            frame_resize = cv2.resize(Frame, (320, 240))
            cv2.imshow('frame', frame_resize)
            key = cv2.waitKey(1)
            if key == 27:
                break
        else:
            time.sleep(0.01)
    camera.camera_close()
    cv2.destroyAllWindows()

