# -*- coding: utf-8 -*-
from picamera import PiCamera
import RPi.GPIO as GPIO
from time import sleep
from PIL import Image
import numpy as np
import os
import glob
import pickle
import shutil
import random

def Preprocess(i,SaveP):
    size = [28,28]
    array = np.empty([size[0]*size[1],0],int)
    print(array.shape)
    FullPath = glob.glob('/home/pi/ドキュメント/camera_car/Predict/*.jpg')
    print(FullPath)
    #Preprocessing
    img = Image.open(FullPath[0]).convert('L')
    img = img.resize(size, Image.ANTIALIAS)
    print(img.format, img.size, img.mode,img.getextrema())
    #Make one dimention array
    img_arr = np.asarray(img)
    print("OneDimention"+str(img_arr.ravel().shape))
    if SaveP:
        os.remove(FullPath[0])
    else:#saving pics for re-training the model.才が羽州のために写真保存
        shutil.move(FullPath[0],'/home/pi/ドキュメント/camera_car/Predict/done/%s.jpg' % i)
    return img_arr.ravel(), img


PickleName = "model_20191102_9.pickle"#indicate trained model(pickle)
SavePics = 0
with open(PickleName, mode='rb') as fp:
    clf = pickle.load(fp)

camera = PiCamera()
#camera.rotation = 180#if camera is upside down カメラが上下反対の場合
camera.resolution = (64,64)

GPIO.setmode(GPIO.BCM)
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
i = 0
duty = 70


#At first go forward
p0.ChangeDutyCycle(20)
p1.ChangeDutyCycle(0)
p2.ChangeDutyCycle(20)
p3.ChangeDutyCycle(0)
try:
    while True:
        #Take a pic and save to indicated folder.写真取って指定フォルダに保存
        i += 1
        camera.capture('/home/pi/ドキュメント/camera_car/Predict/%s.jpg' % i)
        #preprocessing at indicated folder.指定フォルダの写真を前処理
        X_pred, img = Preprocess(i, SavePics)
        #predict 推定
        pred = clf.predict(X_pred)
        #change duty ratio.デューティー比変更
        if pred[0] == 0:#前進
            print("Forward")
            p0.ChangeDutyCycle(duty)
            p1.ChangeDutyCycle(0)
            p2.ChangeDutyCycle(duty)
            p3.ChangeDutyCycle(0)
            sleep(0.8)
        elif pred[0] == 1:#left 左折
            print("Left")
            p0.ChangeDutyCycle(duty-20)
            p1.ChangeDutyCycle(0)
            p2.ChangeDutyCycle(0)
            p3.ChangeDutyCycle(20)
            sleep(0.3)
        elif pred[0] == 2:#right 右折
            print("Right")
            p0.ChangeDutyCycle(0)
            p1.ChangeDutyCycle(20)
            p2.ChangeDutyCycle(duty-20)
            p3.ChangeDutyCycle(0)
            sleep(0.3)
        elif pred[0]  == 3:#backword 後退
            p0.ChangeDutyCycle(0)
            p1.ChangeDutyCycle(duty-10)
            p2.ChangeDutyCycle(0)
            p3.ChangeDutyCycle(duty-40)
            print("Backing...")
            sleep(1)
            print("finish backing")
        #save preprocessed pic前処理後写真を保存
        if SavePics:
            pass
        else:#collect preprocessed pics with pred number.再学習用写真（推定値付き）保存
            rand = random.randint(0,100000)
            img.save('/home/pi/ドキュメント/camera_car/Train/'
                     +str(i)+'_'+str(int(pred[0]))+
                     '_'+str(rand)+'.jpg')

except KeyboardInterrupt:
    pass

p0.stop()
p1.stop()
GPIO.cleanup()

