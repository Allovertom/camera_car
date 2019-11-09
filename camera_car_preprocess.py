#from picamera import PiCamera
from time import sleep
from PIL import Image
import numpy as np
import os
import glob
from sklearn import svm, metrics
from sklearn.model_selection import train_test_split
import pickle

ModelName = "model_20191102_9.pickle"

def main():
    Path = '/home/pi/ドキュメント/camera_car/Train/'
    #Path = 'Train/'
    Left_L = glob.glob(Path + '1_Left/*.jpg')
    Right_L = glob.glob(Path + '2_Right/*.jpg')
    Center_L = glob.glob(Path + '0_Center/*.jpg')
    Back_L = glob.glob(Path + '3_Back/*.jpg')
    X_L = Preprocess(Left_L)
    Y_L = np.ones(int(len(X_L)/784))
    X_R = Preprocess(Right_L)
    Y_R = np.full(int(len(X_R)/784),2)
    X_C = Preprocess(Center_L)
    Y_C = np.zeros(int(len(X_C)/784))
    X_B = Preprocess(Back_L)
    Y_B = np.full(int(len(X_B)/784),3)
    
    X = np.r_[X_L, X_R, X_C, X_B]
    X = X.reshape([int(len(X)/784),784])
    y = np.r_[Y_L, Y_R, Y_C, Y_B]
    print(X.shape)
    print(y.shape)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

    clf = svm.SVC(kernel='linear')
    clf.fit(X_train, y_train)
    pre = clf.predict(X_test)    
    ac_score = metrics.accuracy_score(y_test, pre)
    print(ac_score)

    
        
    with open(ModelName, mode='wb') as fp:
        pickle.dump(clf, fp)


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
        #img.save('/home/pi/ドキュメント/camera_car/Prep/'+str(i)+'_out.jpg')
        #img.save('Prep/'+str(i)+'_out.jpg')
        img_arr = np.asarray(img)
        print("OD"+str(img_arr.ravel().shape))
        array = np.append(array,img_arr.ravel())
        print(array.shape)
    return array

if __name__ == '__main__':
    main()


