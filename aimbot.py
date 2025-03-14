import numpy as np
import pyautogui
import win32api, win32con, win32gui
import cv2
import math
import time
import keyboard
import random


gun_reload_time = 8
gun_ammo_capacity = 5

last_shot = time.time()

CONFIG_FILE = './yolo/yolov3_testing.cfg'
WEIGHT_FILE = './yolo/yolov3_training_v2.weights'

net = cv2.dnn.readNetFromDarknet(CONFIG_FILE, WEIGHT_FILE)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
#net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
#net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

ln = net.getLayerNames()
ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# Get rect of Window
print("Please have WTLO open before the timer ends")
print("3")
time.sleep(1)
print("2")
time.sleep(1)
print("1")
time.sleep(0.9)
WTLO = win32gui.GetForegroundWindow()
print(WTLO)

delta_uses = 0

rect = win32gui.GetWindowRect(WTLO)

region = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]

size_scale = 2

shots = 1
while keyboard.is_pressed('q') == False:
    current_time = time.time()
    delta_time = current_time - last_shot
    if delta_time > 35:
        if delta_uses%2:
            pyautogui.keyDown('a')
            time.sleep(random.uniform(0.1,0.4))
            pyautogui.keyUp('a')
        else:
            pyautogui.keyDown('d')
            time.sleep(random.uniform(0.1,0.4))
            pyautogui.keyUp('d')
        delta_uses += 1
            
        
    if pyautogui.locateOnScreen("./escape.jpg"):
        pyautogui.press('esc')

    # Get image of screen
    frame = np.array(pyautogui.screenshot(region=region))
    frame_height, frame_width = frame.shape[:2]

    # Detection
    blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layerOutputs = net.forward(ln)

    boxes = []
    confidences = []

    for output in layerOutputs:
        for detection in output:
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]
            if confidence > 0.5 and classID == 0:
                box = detection[:4] * np.array([frame_width, frame_height, frame_width, frame_height])
                (centerX, centerY, width, height) = box.astype("int")
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                box = [x, y, int(width), int(height)]
                boxes.append(box)
                confidences.append(float(confidence))

    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.7, 0.6)

    # Calculate distance for picking the closest enemy from crosshair
    if len(indices) > 0:
        last_shot = time.time()
        print(f"Detected:{len(indices)} -" + str(time.time()))
        min = 99999
        min_at = 0
        for i in indices.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)

            dist = math.sqrt(math.pow(frame_width/2 - (x+w/2), 2) + math.pow(frame_height/2 - (y+h/2), 2))
            if dist < min:
                min = dist
                min_at = i
        # Distance of the closest from crosshair
        x = int(boxes[min_at][0] + boxes[min_at][2]/2 - frame_width/2)
        y = int(boxes[min_at][1] + boxes[min_at][3]/2 - frame_height/2) - boxes[min_at][3] * 0.3 # For head shot do 0.5
        print("x co ord is " + str(x))
        print(y)
        print("---")
        print(boxes[min_at])
        # Move mouse and shoot
        scale = 0.3
        x = int(x * scale)
        y = int(y * scale)
        
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)
        time.sleep(0.25)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
        time.sleep(0.11)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)
        time.sleep(0.25)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.21)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
        time.sleep(0.2)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)

        pyautogui.keyDown('w')
        time.sleep(random.uniform(0.05,0.2))
        pyautogui.keyUp('w')


        if shots%(gun_ammo_capacity-1) == 0:
            time.sleep(0.5)
            pyautogui.press('r')
            time.sleep(gun_reload_time-3)
            pyautogui.press('h')
            time.sleep(0.5)
            pyautogui.press('h')
        shots = shots + 1

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (frame.shape[1] // size_scale, frame.shape[0] // size_scale))
    cv2.imshow("frame", frame)
    cv2.waitKey(1)
    #input("")
    
