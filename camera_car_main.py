# -*- coding: utf-8 -*-
from picamera import PiCamera
import RPi.GPIO as GPIO
from time import sleep
from time import sleep
from PIL import Image
import numpy as np
import os
import glob
from sklearn import svm, metrics
from sklearn.model_selection import train_test_split
import pickle
import shutil
import random

PickleName = "model_20191102_9.pickle"
honban = 0


# MCP3208からSPI通信で12ビットのデジタル値を取得。0から7の8チャンネル使用可
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
    if adcnum > 7 or adcnum < 0:
        return -1
    GPIO.output(cspin, GPIO.HIGH)
    GPIO.output(clockpin, GPIO.LOW)
    GPIO.output(cspin, GPIO.LOW)

    commandout = adcnum
    commandout |= 0x18  # スタートビット＋シングルエンドビット
    commandout <<= 3    # LSBから8ビット目を送信するようにする
    for i in range(5):
        # LSBから数えて8ビット目から4ビット目までを送信
        if commandout & 0x80:
            GPIO.output(mosipin, GPIO.HIGH)
        else:
            GPIO.output(mosipin, GPIO.LOW)
        commandout <<= 1
        GPIO.output(clockpin, GPIO.HIGH)
        GPIO.output(clockpin, GPIO.LOW)
    adcout = 0
    # 13ビット読む（ヌルビット＋12ビットデータ）
    for i in range(13):
        GPIO.output(clockpin, GPIO.HIGH)
        GPIO.output(clockpin, GPIO.LOW)
        adcout <<= 1
        if i>0 and GPIO.input(misopin)==GPIO.HIGH:
            adcout |= 0x1
    GPIO.output(cspin, GPIO.HIGH)
    return adcout
    
def Preprocess(i,honban):
    size = [28,28]
    array = np.empty([size[0]*size[1],0],int)
    print(array.shape)
    FullPath = glob.glob('/home/pi/ドキュメント/camera_car/Predict/*.jpg')
    print(FullPath)
    #前処理
    img = Image.open(FullPath[0]).convert('L')
    img = img.resize(size, Image.ANTIALIAS)
    print(img.format, img.size, img.mode,img.getextrema())
    #一次元化
    img_arr = np.asarray(img)
    print("OD"+str(img_arr.ravel().shape))
    if honban:
        os.remove(FullPath[0])#本番用
    else:
        shutil.move(FullPath[0],'/home/pi/ドキュメント/camera_car/Predict/done/%s.jpg' % i)
    return img_arr.ravel(), img

GPIO.setmode(GPIO.BCM)
# ピンの名前を変数として定義
#SPICLK = 11
#SPIMOSI = 10
#SPIMISO = 9
#SPICS = 8
# SPI通信用の入出力を定義
#GPIO.setup(SPICLK, GPIO.OUT)
#GPIO.setup(SPIMOSI, GPIO.OUT)
#GPIO.setup(SPIMISO, GPIO.IN)
#GPIO.setup(SPICS, GPIO.OUT)

with open(PickleName, mode='rb') as fp:
    clf = pickle.load(fp)

camera = PiCamera()
#camera.rotation = 180
camera.resolution = (64,64)

GPIO.setup(25, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)

p0 = GPIO.PWM(25, 50)#RH
p1 = GPIO.PWM(24, 50)#RH
p2 = GPIO.PWM(23, 50)#LH
p3 = GPIO.PWM(22, 50)#LH

p0.start(0)
p1.start(0)
p2.start(0)
p3.start(0)
print("start moving...")
sleep(10)
#adc_pin0 = 0
i = 0
duty = 70
#まずは前進
p0.ChangeDutyCycle(20)
p1.ChangeDutyCycle(0)
p2.ChangeDutyCycle(20)
p3.ChangeDutyCycle(0)
#sleep(3)
try:
    while True:
#        inputVal0 = readadc(adc_pin0, SPICLK, SPIMOSI, SPIMISO, SPICS)

        #写真取って指定フォルダに保存
        i += 1
        camera.capture('/home/pi/ドキュメント/camera_car/Predict/%s.jpg' % i)
        #指定フォルダの写真を前処理
        X_pred, img = Preprocess(i,honban)
        #推定
        pred = clf.predict(X_pred)
        #デューティー比変更
        if pred[0] == 0:#前進
            print("Forward")
            p0.ChangeDutyCycle(duty)
            p1.ChangeDutyCycle(0)
            p2.ChangeDutyCycle(duty)
            p3.ChangeDutyCycle(0)
            sleep(0.8)
        elif pred[0] == 1:#左折
            print("Left")
            p0.ChangeDutyCycle(duty-20)
            p1.ChangeDutyCycle(0)
            p2.ChangeDutyCycle(0)
            p3.ChangeDutyCycle(20)
            sleep(0.3)
        elif pred[0] == 2:#右折
            print("Right")
            p0.ChangeDutyCycle(0)
            p1.ChangeDutyCycle(20)
            p2.ChangeDutyCycle(duty-20)
            p3.ChangeDutyCycle(0)
            sleep(0.3)
        elif pred[0]  == 3:#後退
            p0.ChangeDutyCycle(0)
            p1.ChangeDutyCycle(duty-10)
            p2.ChangeDutyCycle(0)
            p3.ChangeDutyCycle(duty-40)
            print("Backing...")
            sleep(1)
            print("finish backing")
        #前処理後写真を保存
        if honban:
            pass
        else:
            rand = random.randint(0,100000)
            img.save('/home/pi/ドキュメント/camera_car/Train/'
                     +str(i)+'_'+str(int(pred[0]))+
                     '_'+str(rand)+'.jpg')

except KeyboardInterrupt:
    pass

p0.stop()
p1.stop()
GPIO.cleanup()

