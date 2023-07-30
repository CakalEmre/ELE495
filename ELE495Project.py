import cv2
import numpy as np
import sys 
import time
import nanocamera as nano
from jetbot.robot import Robot
import serial
import requests

#"apiKey": '24f5e3a8-de99-430c-b69d-8695bebf6401',
def send_message_detector(message_value,description_value):
    requests.post('https://api.mynotifier.app', {
    "apiKey": '24f5e3a8-de99-430c-b69d-8695bebf6400',
    "message": message_value,
    "description": description_value,
    "type": "warning", # info, error, warning or success
})

def metal_detector(data):
    if data == '1':
        send_message_detector("Çöp Türü","Metal")
    elif data == '2':
        send_message_detector("Çöp Türü","Plastik veya Cam")   
    return int(data)

def compare_frames(frame1,frame2,th=5): #Deneme
    difference = cv2.absdiff(frame1,frame2)
    average_diff = np.mean(difference)
    if average_diff < th:
        temp = 1
    else: 
        temp = 0
    return temp

dispW=640
dispH=480
video_capture = nano.Camera (flip=0 ,width = 640, height = 480, fps=60)
robot = Robot()
frame = video_capture.read()


low_red = np.array([0, 100, 105])
high_red = np.array([179, 255, 255])
low_green = np.array([40, 75, 80])
high_green = np.array([100, 255, 125])
low_black = np.array([0, 0, 50])
high_black = np.array([179, 255, 65])
low_orange = np.array([0, 120, 120])
high_orange = np.array([20, 255, 255])

mb =90
mc = 170

timer = 0 #Deneme
collision_counter = 0 #Deneme
time_th = 3 #Deneme

hız = 0
sol = 0.0
sag = 0.0
hız = 0.165
sol = 0.27
sag = 0.26

cup_found = 0
start = 0
count_to_start = 0
metal = 0
window_title = "Bitirme Projesi"
open_claws = 0
time_count = 0
port_arduino = serial.Serial('/dev/ttyUSB0',9600)
time.sleep(2)
frame = video_capture.read()
port_arduino.write(b'3')
cup_counter = 0
color = 0 #1 yesil 2 kırmızı
start_time = time.time()#Deneme
crash = 0 #Deneme
#window_handle = cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE)

while True:
    if cup_counter == 3:
        robot.stop()
        start = 0
    error_x = 0
    green_mask = []
    red_mask = []
    black_mask = []
    black_contours = []
    red_contours = []
    green_contours = []
    x = 0
    y = 0
    w = 0
    h = 0
    count_to_start = count_to_start + 1
    if start:
        if compare_frames(frame,frame2) == 1:
            #print(collision_counter)
            collision_counter += 1
            if collision_counter >= 100:
                robot.set_motors(-1*sol,-1*sag)
                for l in range(1000000):
                    if l == 999999:
                        frame = video_capture.read()
                robot.stop()
                robot.right(hız)
                for l in range(1000000):
                    if l == 999999:
                        frame = video_capture.read()
                robot.stop()
                collision_counter = 0
        else:
            collision_counter = 0

        frame = video_capture.read()
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        if cup_found == 0: #Bardağı bul
            
            black_mask = cv2.inRange(hsv_frame, low_black, high_black)
            black_contours, _ = cv2.findContours(black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)		
            black_contours = sorted(black_contours, key=lambda x:cv2.contourArea(x), reverse=True)
          
            if open_claws == 1:
                color = 0
                robot.set_motors(sol,sag)
                for l in range(1300000):
                    if l == 1299999:
                        frame = video_capture.read()
                robot.stop()
                port_arduino.write(b'2')
                for l in range(6000000):
                    if l == 5999999:
                        frame = video_capture.read()
                port_arduino.write(b'1')
                while True:
                    if port_arduino.in_waiting > 0:
                        data_arduino = port_arduino.readline().decode('utf-8').rstrip()
                        if data_arduino != '0':
                            metal = metal_detector(data_arduino)
                            break
                robot.set_motors(-1*sol+0.02,-1*sag+0.02)
                for l in range(2000000):
                    if l == 1999999:
                        frame = video_capture.read()
                robot.stop()
                open_claws = 0
                timer = 0
                cup_found = 1  
            else:
                if len(black_contours) > 0:
                    for cnt in black_contours:
                        area=cv2.contourArea(cnt)
                        (x, y, w, h) = cv2.boundingRect(cnt)
                        if (y > 120) and (x > 120) and (x < 520):
                            if area >= 90: 
                                cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),3)
                                obj_x=x+w/2
                                obj_y=y-h/2
                                error_x=obj_x-dispW/2
                                if error_x > mb:
                                    robot.right(hız)
                                    break
                                elif error_x < -1*mb:
                                    robot.left(hız) 
                                    break
                                elif error_x < mb and error_x > -1*mb :
                                    robot.set_motors(sol,sag)
                                    if (w/h) > 1.0:
                                        open_claws = 1
                                    break
                            else:
                                if color == 1: #Bu kısım kalıcak
                                    robot.right(hız)
                                elif color == 2:
                                    robot.left(hız) 
                                else:
                                    robot.left(hız)
                        else:
                            if color == 1: #Bu kısım kalıcak
                                robot.right(hız)
                            elif color == 2:
                                robot.left(hız) 
                            else:
                                robot.left(hız)
                else:
                    if color == 1: #Bu kısım kalıcak
                        robot.right(hız)
                    elif color == 2:
                        robot.left(hız) 
                    else:
                        robot.left(hız)

        elif cup_found == 1: # Bardağı gerekli yere götür
            if metal == 1: # Bardağı kırmızıya götür
                color = 2
                red_mask = cv2.inRange(hsv_frame, low_red, high_red)
                red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)		
                red_contours = sorted(red_contours, key=lambda x:cv2.contourArea(x), reverse=True)

                for cnt in red_contours:
                    area=cv2.contourArea(cnt)
                    (x, y, w, h) = cv2.boundingRect(cnt)
                    
                    if area >= 1500: 
                        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),3)
                        obj_x=x+w/2
                        obj_y=y-h/2
                        error_x=obj_x-dispW/2
                        if error_x > mc:
                            robot.right(hız)#deneme
                            break
                        elif error_x < -1*mc:
                            robot.left(hız)#deneme
                            break 
                        elif error_x < mc and error_x > -1*mc and (w/h) < 0.8 :
                            robot.set_motors(sol,sag)#deneme
                            break
                        elif w>250:
                            robot.stop()
                            port_arduino.write(b'3')
                            cup_counter += 1
                            for l in range(6000000):
                                if l == 5999999:
                                    frame = video_capture.read()
                            robot.set_motors(-1*sol,-1*sag)
                            for l in range(3000000):
                                if l == 2999999:
                                    frame = video_capture.read()
                            robot.stop()
                            robot.left(hız)
                            for l in range(4000000):
                                if l == 3999999:
                                    frame = video_capture.read()
                            robot.stop()
                            robot.set_motors(sol,sag)
                            for l in range(2500000):
                                if l == 2499999:
                                    frame = video_capture.read()
                            robot.stop()
                            for l in range(10):
                                frame = video_capture.read()
                            cup_found = 0
                            metal = 0
                            open_claws = 0
                            break
                    else: #kırmızı bulamadıysa dönsün
                        robot.right(hız)
                        #break

            elif metal == 2: # Bardağı yeşile götür 
                color = 1
                green_mask = cv2.inRange(hsv_frame, low_green, high_green)
                green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)		
                green_contours = sorted(green_contours, key=lambda x:cv2.contourArea(x), reverse=True)
                for cnt in green_contours:
                    area=cv2.contourArea(cnt)
                    (x, y, w, h) = cv2.boundingRect(cnt) 
                    
                    if area >= 1500: 
                        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),3)
                        obj_x=x+w/2
                        obj_y=y-h/2
                        error_x=obj_x-dispW/2
                        if error_x > mc:
                            robot.right(hız)#deneme
                            break
                        elif error_x < -1*mc:
                            robot.left(hız)#deneme
                            break
                        elif error_x < mc and error_x > -1*mc and (w/h) < 0.8 : 
                            robot.set_motors(sol,sag)
                            break
                        elif w>250:
                            robot.stop()
                            port_arduino.write(b'3')
                            cup_counter += 1
                            for l in range(6000000):
                                if l == 5999999:
                                    frame = video_capture.read()
                            robot.set_motors(-1*sol,-1*sag)
                            for l in range(3000000):
                                if l == 2999999:
                                    frame = video_capture.read()
                            robot.stop()
                            robot.right(hız)
                            for l in range(4000000):
                                if l == 3999999:
                                    frame = video_capture.read()
                            robot.stop()
                            robot.set_motors(sol,sag)
                            for l in range(2500000):
                                if l == 2499999:
                                    frame = video_capture.read()
                            robot.stop()
                            for l in range(10):
                                frame = video_capture.read()
                            cup_found=0
                            metal = 0
                            open_claws = 0
                            break
                    else: 
                        robot.left(hız)
                        #break
    area = 0               
    #cv2.imshow(window_title, frame)
    if count_to_start == 15:
        start = 1
    del(w)
    del(h)
    del(x)
    del(y)
    del(black_contours)
    del(green_contours)
    del(red_contours)
    del(black_mask)
    del(red_mask)
    del(green_mask)
    frame2 = video_capture.read()

    #keyCode = cv2.waitKey(10) & 0xFF
    # Stop the program on the ESC key or 'q'
    #if keyCode == 27 or keyCode == ord('q'):
     #   break