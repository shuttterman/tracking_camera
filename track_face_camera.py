import numpy as np
import cv2
import RPi.GPIO as GPIO
import time
import pigpio

def setangle(hor=90, ver=90) : # 카메라 각도설정
    global pi
    pi.set_servo_pulsewidth(horizental,600+10*hor)
    pi.set_servo_pulsewidth(horizental,600+10*ver)

def get_distance() : #초음파로 거리 구하는 함수
    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)

    while GPIO.input(echo) == 0 :
        pulse_start = time.time()
    while GPIO.input(echo) == 1 :
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 34300/2
    distance = round(distance, 2)
    print(f"I found you, you're {distance}cm away from me")
    return distance

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

pi = pigpio.pi() # 지터링을 없애기 위해 쓰는 프로그램 인터페이스

horizental = 18
vertical = 12
trig = 23
echo = 24

GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)

GPIO.output(trig, False)

faceCascade = cv2.CascadeClassifier('./haarcascades/haarcascades/haarcascade_frontalface_default.xml') #cascade분류기 활용
cap = cv2.VideoCapture(0) # cv2 활용
cap.set(3,640) # set Width
cap.set(4,480) # set Height

ver = False
hor = False

rotation_speed = 1 #회전 속도 조절

horizental_angle = 90 #initial 각도
vertical_angle = 90
setangle(horizental_angle, vertical_angle)

while True:
    ret, img = cap.read()
    img = cv2.flip(img, -1) 
    img = cv2.flip(img, 1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(20, 20)
    )
    for (x,y,w,h) in faces: #찾은 얼굴에 box 그리기
        horizental_mid = (x*2+w)/2
        vertical_mid = (y*2+h)/2
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        if 256<=horizental_mid<=384 : #horizental angle 조절
            hor = True
            pass
        else :
            if horizental_mid>384 :
                horizental_angle = (horizental_angle + rotation_speed)%180
            else :
                horizental_angle = (horizental_angle - rotation_speed)%180
            pi.set_servo_pulsewidth(horizental,600+10*horizental_angle)

        if 160<=vertical_mid<=320 : #vertical angle 조절
            ver = True
            pass
        else :
            if vertical_mid>320 :
                vertical_angle = (vertical_angle + rotation_speed)%180
            else :
                vertical_angle = (vertical_angle - rotation_speed)%180
            pi.set_servo_pulsewidth(vertical,600+10*vertical_angle)
        if ver and hor : #vertical, horizental angle이 안정적인 위치에 오면 거리 구하기
            distance = get_distance()
            cv2.putText(img, f'{distance}cm', (x+w,y+h), cv2.FONT_HERSHEY_SIMPLEX, 1.5,(255, 0, 0), 2, cv2.LINE_AA)
            hor = False
            ver = False

    cv2.imshow('video',img) #화면 출력
    k = cv2.waitKey(30) & 0xff
    if k == 27: #esc누르면 종료
        break

#자원 정리
setangle()
GPIO.cleanup()
cap.release()
cv2.destroyAllWindows()
