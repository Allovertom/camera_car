from picamera import PiCamera
from time import sleep
from PIL import Image
import numpy as np
import os

def Take_pics():
    camera = PiCamera()
    camera.rotation = 180
    camera.resolution = (64,64)
    camera.start_preview()
    for i in range(5):
        sleep(2)
        camera.capture('/home/pi/画像/image%s.jpg' % i)
    camera.stop_preview()

def Preprocess():
    image_P = Image.open('/home/pi/画像/image1.jpg').convert('L')
    image_P = image_P.resize((8,8), Image.ANTIALIAS)
    print(image_P.format, image_P.size, image_P.mode,image_P.getextrema())
    image_P.save('/home/pi/画像/image_L.jpg')
    
Preprocess()
