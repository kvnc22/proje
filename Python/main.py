from enum import auto
from lib2to3.pygram import Symbols
from re import MULTILINE
from tkinter import CENTER
from turtle import width, window_height, window_width
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.graphics.texture import Texture
from kivy.lang import Builder
Builder.load_file('main.kv')
from kivy.core.window import Window
from pyzbar import pyzbar
import webbrowser
import cv2
import numpy as np
from pyfirmata import Arduino, util, SERVO
from time import sleep
board = Arduino('COM5')
pin = 10
board.digital[pin].mode = SERVO 
barcode1 = "8690767716300"
barcode2 = "8690504135913"
barcode3 = "8690504116486"

outputtext=''
weblink=''
leb=Label(text=outputtext,size_hint_y='2',height='48dp',font_size='45dp')
found = set()       
togglflag=True
Window.fullscreen = 'auto'

def rotateServo1(pin):
    board.digital[pin].write('30')
    sleep(0.015)

def rotateServo2(pin):
    board.digital[pin].write('90')
    sleep(0.015)

def rotateServo3(pin):
    board.digital[pin].write('150')
    sleep(0.015)

class MainScreen(BoxLayout):
   
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.orientation='vertical' 
        
        self.cam=cv2.VideoCapture(0)    
        self.cam.set(3,1280)        
        self.cam.set(4,720)
        self.img=Image()        #
        

        self.togbut=ToggleButton(text='Durdur',group='camstart',state='down',size_hint_y=None,width='12dp',height='64dp',on_press=self.change_state)
        self.add_widget(self.img)
        self.add_widget(self.togbut)
        Clock.schedule_interval(self.update,1.0/30)     
        
                
    # update frame of OpenCV camera
    def update(self,dt):
        if togglflag:
            ret, frame = self.cam.read()    
            
            if ret:
                buf1=cv2.flip(frame,0)       
                buf=buf1.tostring()
                image_texture=Texture.create(size=(frame.shape[1],frame.shape[0]),colorfmt='bgr')
                image_texture.blit_buffer(buf,colorfmt='bgr',bufferfmt='ubyte')
                self.img.texture=image_texture  
                
                barcodes = pyzbar.decode(frame,symbols=[pyzbar.ZBarSymbol.QRCODE])    
                for barcode in barcodes:
                    (x, y, w, h) = barcode.rect
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    barcodeData = barcode.data.decode("utf-8")
                    barcodeType = barcode.type
                    text = "{} ({})".format(barcodeData, barcodeType)
                    cv2.putText(frame, text, (x, y - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    outputtext=text
                    leb.text=outputtext         
                    board.digital[2].write(1)
                    sleep(0.04)
                    board.digital[2].write(0)
                    print(barcodeData)
                    self.change_screen()
                    if barcodeData == barcode1:
                        rotateServo1(pin)
                    elif barcodeData == barcode2:
                        rotateServo2(pin)
                    elif barcodeData == barcode3:
                        rotateServo3(pin)
                    break

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    cv2.destroyAllWindows()
                    exit(0)
        
    # change state of toggle button
    def change_state(self,*args):
        global togglflag
        if togglflag:
            self.togbut.text='Başlat'
            togglflag=False
        else:
            self.togbut.text='Durdur'
            togglflag=True
            
            
    def stop_stream(self,*args):
        self.cam.release()  
        
    def change_screen(self,*args):
        main_app.sm.current='second'    

class SecondScreen(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.orientation='vertical'
        self.lab1=Label(text='Barkod: ',size_hint_y='2',height='48dp',font_size='45dp')
        self.but1=Button(text='Geri Dön',
                         on_press=self.change_screen2,
                         size_hint_y=None,
                         height='48dp')
        self.add_widget(self.lab1)
        self.add_widget(leb)
        self.add_widget(self.but1)
        
    def change_screen2(self,*args):
        main_app.sm.current='main'
        
class FirstScreen(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.orientation='vertical'
        '''
        self.lab1=Label(text='ID Giriniz:',
                        y=100
                        )
        self.name=TextInput(hint_text='ID Giriniz.',
                            size_hint=(.2, .05),
                            multiline = False,
                            pos=[.5,.5],
                            pos_hint={'x': .5, 'y': .5}
                            
                            )
        self.but1=Button(text='Kaydet',
                         on_press=self.change_screen3,
                            size_hint_y=None,
                         height='48dp')
        
        self.add_widget(self.lab1)
        self.add_widget(self.name)
        self.add_widget(self.but1)
        '''
    def change_screen3(self,*args):
        main_app.sm.current='main'
class TestApp(App):
    def build(self):
        self.sm=ScreenManager()     
        self.firstsc=FirstScreen()
        scrn=Screen(name='first')
        scrn.add_widget(self.firstsc)
        self.sm.add_widget(scrn)

        self.mainsc=MainScreen()
        scrn=Screen(name='main')
        scrn.add_widget(self.mainsc)
        self.sm.add_widget(scrn)
        
        self.secondsc=SecondScreen()
        scrn=Screen(name='second')
        scrn.add_widget(self.secondsc)
        self.sm.add_widget(scrn)
        

        return self.sm



if __name__ == '__main__':
    main_app=TestApp()
    main_app.run()
    cv2.destroyAllWindows()        
