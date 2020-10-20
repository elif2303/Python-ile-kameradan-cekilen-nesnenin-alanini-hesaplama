from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
from matplotlib import pyplot as plt
from PIL import Image
from PyQt5 import QtCore, QtGui,QtWidgets
from PyQt5.QtCore import QCoreApplication
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys 


class Window(QMainWindow): 
    def __init__(self): 
        super().__init__() 

        # setting title 
        self.setWindowTitle("Python ") 

        # setting geometry 
        self.setGeometry(100, 100, 600, 400) 

        # calling method 
        self.UiComponents() 

        # showing all the widgets 
        self.show() 

    # method for widgets 
    def UiComponents(self): 

        # creating a push button 
        button = QPushButton("CLICK", self) 

        # setting geometry of button 
        button.setGeometry(200, 150, 100, 30) 
        
        self.textbox = QLineEdit(self)
        self.textbox.move(20, 20)
        self.textbox.resize(280,40)

        # adding action to a button 
        button.clicked.connect(self.hesap) 
    
    # action method 
        
    def hesap(self):


        def midpoint(ptA, ptB):
                return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

            
        kamera=cv2.VideoCapture(0) # 0 numaralı kayıtlı kamerayı alma
        
        while(True):
            ret,goruntu=kamera.read() # kamera okumayı başlatma

            """
            # Değişkenlerin yapılandırıldığı ve çözümlendiği kısım
            ap = argparse.ArgumentParser()
            ap.add_argument("-i", "--image", required=True,
                help="path to the input image")
            
            ap.add_argument("-w", "--width", type=float, required=True,
                help="width of the left-most object in the image (in inches)")
            
            args = vars(ap.parse_args())
            """

            # Görüntü yüklenir, gri tona dönüştürülür ve bulanıklaştırılır.
            
            gray = cv2.cvtColor(goruntu, cv2.COLOR_RGB2GRAY)
            gray = cv2.GaussianBlur(gray, (7, 7), 0)

            # Kenar tespiti, genişletme ve daraltma işlemleri uygulanır
            # Nesne kenarları arasındaki boşluklar kapatılır
            edged = cv2.Canny(gray, 50, 100)
            edged = cv2.dilate(edged, None, iterations=1)
            edged = cv2.erode(edged, None, iterations=1)

            # Kenar haritasında kontürler bulunur.
            cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)

            # Kontürler soldan sağa doğru sıralanır.
            # "Metrik başına piksel" kalibrasyon değişkeni
            (cnts, _) = contours.sort_contours(cnts)
            pixelsPerMetric = None

            for c in cnts:
                # Kontur yeterince büyük değilse görmezden gel
                if cv2.contourArea(c) < 100:
                    continue

                # Kontürün döndürülmüş sınırlayıcı kutusunu hesaplanır
                orig = goruntu.copy()
                box = cv2.minAreaRect(c)
                box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
                box = np.array(box, dtype="int")
                

                # Kontürdeki noktalar görünecek şekilde sıralanır
                # sol üst, sağ üst, sağ alt ve sol altta
                # Sınırların ana hatları çizilir
                box = perspective.order_points(box)
                cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

                # Orjinal noktaların üzerinde döngü yapılır ve onlar çizilir
                for (x, y) in box:
                    cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)
                
                # sıralı sınırlayıcı kutuyu açın, ardından orta noktayı hesaplar
                # sol üst ve sağ üst koordinatlar arasında, ardından
                # sol alt ve sağ alt koordinatlar arasındaki orta nokta
                (tl, tr, br, bl) = box
                (tltrX, tltrY) = midpoint(tl, tr)
                (blbrX, blbrY) = midpoint(bl, br)

                # sol üst ve sağ üst noktalar arasındaki orta noktayı hesaplar,
                # ardından sağ üst ve sağ alt arasındaki orta nokta
                (tlblX, tlblY) = midpoint(tl, bl)
                (trbrX, trbrY) = midpoint(tr, br)

                # görüntünün orta noktaları çizilir
                cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)	
                cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
                cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
                cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)

                # orta noktalar arasında çizgiler çizilir
                cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
                    (255, 0, 255), 2)
                cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
                    (255, 0, 255), 2)

                # orta noktalar arasındaki Öklid mesafesi hesaplanır
                dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
                dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))
                print("dA", dA)
                print("dB", dB)
                
                # metrik başına piksel başlatılmadıysa,
                # bunu piksellerin sağlanan metriğe oranı olarak hesaplanır
                # (bu durumda, inç)
                if pixelsPerMetric is None:
                    pixelsPerMetric = 0.0050858

                # nesnenin boyutu hesaplanır
                dimA = dA * pixelsPerMetric * 2.54
                dimB = dB * pixelsPerMetric * 2.54

                # görüntüdeki nesne boyutları çizilir
                cv2.putText(orig, "{:.1f}cm".format(dimB),
                    (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
                    0.65, (255, 255, 255), 2)
                cv2.putText(orig, "{:.1f}cm".format(dimA),
                    (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
                    0.65, (255, 255, 255), 2)

                cv2.imshow("Image", orig)
                #  çıktı görüntüsü gösterilir 
                """
                plt.imshow(orig)
                plt.show()
                """
                cv2.waitKey(0)

                kamera.release() # kamerayı serbest bırak.

            area_cm=round(dimA*dimB,1)
            print("Alan: ", area_cm , "cm^2")

            """
            sad1 = np.size(orig, axis = 0)                          #(0,1,2)   axis=0=24        derinlik 
            sad2 = np.size(orig, axis = 1)                          #(0,1,2)   axis=1=256       satır 
            sad3 = np.size(orig, axis = 2)                          #(0,1,2)   axis=2=256       sütun


            print(sad1,sad2,sad3)
            """
            print(orig.size)
            print(orig.shape)
        
        

# create pyqt5 app 
App = QApplication(sys.argv) 

# create the instance of our Window 
window = Window() 

# start the app 
sys.exit(App.exec()) 



        
