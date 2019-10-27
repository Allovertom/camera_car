from picamera import PiCamera
from time import sleep
from PIL import Image
import numpy as np
import os
import glob
from sklearn import svm, metrics
from sklearn.model_selection import train_test_split


def main():
    Path = '/home/pi/ドキュメント/camera_car/Train/'
    Left_L = glob.glob(Path + 'Left/*.jpg')
    Right_L = glob.glob(Path + 'Right/*.jpg')
    Center_L = glob.glob(Path + 'Center/*.jpg')
    X_L = Preprocess(Left_L)
    Y_L = np.ones(int(len(X_L)/784))
    X_R = Preprocess(Right_L)
    Y_R = np.full(int(len(X_R)/784),2)
    X_C = Preprocess(Center_L)
    Y_C = np.zeros(int(len(X_C)/784))
    
    X = np.r_[X_L, X_R, X_C]
    X = X.reshape([784,int(len(X)/784)])
    Y = np.r_[Y_L, Y_R, Y_C]
    print(X.shape)
    print(Y.shape)

    #for gan in [0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000]:
     #   clf = svm.SVC(C=gan)
      #  clf.fit(data_train, label_train)
       # pre = clf.predict(data_test)    
        #ac_score = metrics.accuracy_score(label_test, pre)
        #print(ac_score)


def Take_pics():
    camera = PiCamera()
    camera.rotation = 180
    camera.resolution = (64,64)
    camera.start_preview()
    for i in range(5):
        sleep(2)
        camera.capture('/home/pi/画像/image%s.jpg' % i)
    camera.stop_preview()

def Preprocess(files):
    size = [28,28]
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


