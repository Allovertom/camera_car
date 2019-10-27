from picamera import PiCamera
from time import sleep
from PIL import Image
import numpy as np
import os
import glob
from sklearn import svm, metrics


def main():
    arr = Preprocess()
    #print(arr, len(arr))
#    clf = svm.SVC()
#    clf.fit(data_train, label_train)
#    pre = clf.predict(data_test)
#    
#    ac_score = metrics.accuracy_score(label_test, pre)
#    print(ac_score)


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
    size = [28,28]
    files = glob.glob('/home/pi/ドキュメント/camera_car/Train/*.jpg')
    array = np.empty([size[0]*size[1],0],int)
    print(array.shape)
    print(files)
    for i, file in enumerate(files):
        img = Image.open(file).convert('L')
        img = img.resize(size, Image.ANTIALIAS)
        print(img.format, img.size, img.mode,img.getextrema())
        img.save('/home/pi/ドキュメント/camera_car/Prep/'+str(i)+'_out.jpg')
        img_arr = np.asarray(img)
        print("OD"+str(img_arr.ravel().shape))
        array = np.append(array,img_arr.ravel())
        print(array.shape)
    return array

if __name__ == '__main__':
    main()


