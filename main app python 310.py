# Author: Kubera Murthi
#Description: Aerothrust pendulum Serial Data Transmitter and plotter
#Date: 22-12-18
#Reference: Adithya Selvaprithviraj
#Python Versio 3.10

import math
import serial
from time import sleep
import time
import numpy as np
from collections import deque
from tkinter import *
import tkinter as tk
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
from tkinter import messagebox

#Transmitter parameters
startflag=1
channels={"A":"00","B":"01","C":"10","D":"11"}
data4word="0b1000000000"
global varl
varl=0
prev=0
prev1=0
rrate=15
theta=0
thetadot=0

# Plotter Parameters
data1 = [0]
data2 = [0]
plotdata=0
c1ylim=600
c2ylim=600
xybufflen=500
LARGE_FONT= ("Verdana", 16)

#XY Graph (Theta vs Theta dot)

app = QtWidgets.QApplication([])
p = pg.plot()
p.setWindowTitle('live plot from serial')
curve = p.plot()


#data decoding
def switch_data(option,data):     
    def theta_l():
        global varl
        varl = data&31        
    def theta_h():
        global varh
        global theta
        global varl
        varh = data&31
        temp = (varh*32)+varl
        theta = temp
        if theta>180:
            theta = theta-360
        #print(theta)
    def thetadot_l():
        global varl
        varl = data&31        
    def thetadot_h():
        global varh
        global varl
        global thetadot
        varh = data&31
        temp= (varh*32)+varl
        thetadot = (temp*3)-1200
        #print(thetadot)
    def default() :
        print ("0")
    dictionary = {
        0: theta_l,
        1: theta_h,
        2: thetadot_l,
        3: thetadot_h,
        4: default,
        5: default,
        6: default,
        7: default}
    dictionary[option]()

#clear graph
def clearscr():
    setconfig()
    
    global p
    global curve
    global app
    p.clear()    
    for i in range(len(data1)):
        data1[i]=0
        data2[i]=0
    app.closeAllWindows()
    p = pg.plot()
    curve = p.plot()    
    setconfig()
    pollSerial()
    
#plot update
def update(d1,d2):
    global curve
    if len(data1)<xybufflen:
        data1.append(float(d1))
        data2.append(float(d2))
    else:
        data1.pop(0)
        data2.pop(0)
        data1.append(float(d1))
        data2.append(float(d2))
    curve.setData(data1,data2)        
    app.processEvents()
    
#Serial Data Reciever function (USB data from MCU)
try:
 def pollSerial():    
    global prev
    global rrate
    global theta
    global thetadot   
    if plotdata==1:
        tym = time.clock()-prev
        prev = time.clock()
        count =0            
        while ser1.inWaiting :
            count+=1
            if count >rrate: 
                break
            prev1 = time.clock()
            a=ser1.read()            
            b= int(a.encode('hex'),16)            
            choice=int(b/32)
            switch_data(choice,b)           
            update(theta,thetadot)
            tym1 = time.clock()-prev1
            rrate = int(tym/tym1)            
    root.after(20,pollSerial)
except Exception as e:
            print(e)
    
#Stop all operations and quit
def pyquit():       
        sleep(1)
        root.destroy()        
        app.closeAllWindows()
        ser1.close()
        quit()
#Start or stop plotting
def ploten():        
        global plotdata
        if startflag==1:
            setconfig() 
        if plotdata ==1:
            but1.configure(bg ="#128C03",fg ="#F7FCF6" )
            plotdata=0
            but1["text"] = "Start plot"            
        else:            
            but1.configure(bg ="#C50D04",fg ="#F7FCF6" )
            but1["text"] = "Stop plot"
            sleep(1)
            plotdata =1
            pollSerial()
            #clearscr() 
#Initialization & Configuration f plotter
def setconfig():        
        global c1ylim
        global c2ylim
        global xybufflen
        global startflag
        global ser1
        xybufflen=int(bufflen.get())        
        c1ylim=int(xlimit.get())
        c2ylim=int(ylimit.get())       
        p.setXRange(-c1ylim,c1ylim,padding=0)
        p.setYRange(-c2ylim,c2ylim,padding=0)
        if startflag==1:
            ser1=serial.Serial(port.get(),115200)
            startflag=0
#Transmitter Dec button operated            
def Dec():
    global data4word
    if data4word[9]=="1":
        btn2.configure(bg ="#128C03",fg ="#F7FCF6" )
        data4word=data4word[:9]+"0"+data4word[10:]
        btn2["text"] = "DEC"
        sendData("D",int(data4word,2))
    else:
        btn2.configure(bg ="#C50D04",fg ="#F7FCF6" )
        data4word=data4word[:9]+"1"+data4word[10:]
        btn2["text"] = "Stop"
        sendData("D",int(data4word,2))

#Transmitter Inc button operated
def Inc():
    global data4word
    if data4word[10]=="1":
        btn3.configure(bg ="#128C03",fg ="#F7FCF6" )
        data4word=data4word[:10]+"0"+data4word[11:]
        btn3["text"] = "INC"        
        sendData("D",int(data4word,2))
    else:
        btn3.configure(bg ="#C50D04",fg ="#F7FCF6" )
        data4word=data4word[:10]+"1"+data4word[11:]
        btn3["text"] = "Stop"
        sendData("D",int(data4word,2))

#Motor On/Off button operated
def BLDC_Ctrl():
    global data4word
    if data4word[11]=="1":
        btn1.configure(bg ="#128C03",fg ="#F7FCF6" )
        data4word=data4word[:11]+"0"
        btn1["text"] = "ON"
        sendData("D",int(data4word,2))
    else:
        answer = messagebox.askquestion("Turn On Motor", "Do you want to Turn ON motor?", icon='warning')
        if answer == "yes" :
            btn1.configure(bg ="#C50D04",fg ="#F7FCF6" )
            data4word=data4word[:11]+"1"
            btn1["text"] = "OFF"
            sendData("D",int(data4word,2))

#Sending Data
def sendData (channel,data1):
    global startflag    
    cword=channels[channel]
    
    bdata=format(data1,"#012b")
   
    word1= cword+"0"+bdata[7:]
    word2= cword+"1"+bdata[2:7]
    
    word1=int(word1,2)
    word2=int(word2,2)    
    
    fcommand= bytearray([word1,word2])

    if startflag==1:
        setconfig()       
        
    ser1.write(fcommand)
    sleep(0.1)

#Initial configuration of Transmitter GUI    
def packData():
    global set_theta    
    d1 = float(Kp1.get())
    d2 = float(Kd1.get())
    d3 = float(Ki1.get())
    d4 = float(set_theta1.get())
    if d4>360 :
        messagebox.showerror('window Title','Enter value between 0 to 360')
    elif d4<0 :
        messagebox.showerror('window Title','Enter value between 0 to 360')
    else :       
        Kp = int(d1*100)
        Kd = int(d2*100)
        Ki = int(d3*100)
        set_theta = int(d4)    
        sendData ("A",Kp)
        sendData ("B",Kd)
        sendData ("C",Ki)
        sendData ("D",set_theta)
        sleep(0.01)
#GUI Object (root) creation
root = tk.Tk()
root.configure(bg="#C2F2F7")
root.geometry("260x300")
root.title('Aerothrust Transmitter & Plotter')

#Transmitter GUI Components
LabelPort = Label(root, text = "Port",bg="#C2F2F7").grid(row=0)
LabelKp = Label(root, text = "Kp",bg="#C2F2F7").grid(row=1)
LabelKd = Label(root, text = "Kd",bg="#C2F2F7").grid(row=2)
LabelKi = Label(root, text = "Ki",bg="#C2F2F7").grid(row=3)
Label_Set_Theta = Label(root, text = "Set Theta",bg="#C2F2F7").grid(row=4)

port = Entry(root)
Kp1 = Entry(root)
Kd1 = Entry(root)
Ki1 = Entry(root)
set_theta1 = Entry(root)

port.insert(0,'COM5')
Kp1.insert(0,'0.91')
Kd1.insert(0,'0.98')
Ki1.insert(0,'0.1')
set_theta1.insert(0,'0')

port.grid(row=0, column=1)
Kp1.grid(row=1, column=1)
Kd1.grid(row=2, column=1)
Ki1.grid(row=3, column=1)
set_theta1.grid(row=4, column=1)

button = Button(root, text = "Send", command=packData,fg="#C2F2F7",bg="#444DF9",bd="3")
btn1 = Button(root, text = "ON", width=4, command=BLDC_Ctrl,bg ="#128C03",fg ="#F7FCF6",bd="3")
btn2 = Button(root, text = "DEC", width=4, command=Dec,bg ="#128C03",fg ="#F7FCF6",bd="3")
btn3 = Button(root, text = "INC", width=4, command=Inc,bg ="#128C03",fg ="#F7FCF6",bd="3")

button.grid(row=9, column=1, sticky = E)
btn1.grid(row=9, column=1, sticky = S)
btn2.grid(row=9, column=1, sticky = W)
btn3.grid(row=9, column=0, sticky = E)

#Plotter GUI Components
LabBuflen = Label(root, text = "Buffer length",bg="#C2F2F7").grid(row=6)
LabXlim = Label(root, text = "X limit",bg="#C2F2F7").grid(row=7)
LabYlim = Label(root, text = "Y limit",bg="#C2F2F7").grid(row=8)

bufflen = Entry(root)
xlimit = Entry(root)
ylimit = Entry(root)

bufflen.insert(0,'1000')
xlimit.insert(0,'400')
ylimit.insert(0,'400')

bufflen.grid(row=6, column=1)
xlimit.grid(row=7, column=1)
ylimit.grid(row=8, column=1)

but = Button(root, text = "Set", width=4, command=setconfig,fg="#C2F2F7",bg="#444DF9",bd="3")
but1 = Button(root, text = "Start plot", width=6, command=ploten,bg ="#128C03",fg ="#F7FCF6",bd="3")
but2 = Button(root, text = "Quit", width=3, command=pyquit,bg ="#C50D04",fg ="#F7FCF6",bd="3")
but3 = Button(root, text = "Clear", width=3, command=clearscr,bg ="#C50D04",fg ="#F7FCF6",bd="3")

labplt = Label(root, text = "Plotter Control",bg="#C2F2F7",fg="#C2F2F7").grid(row=10,column=1)
but.grid(row=11, column=0, sticky = E)
but1.grid(row=11, column=1, sticky = S)
but2.grid(row=11, column=1, sticky = E)
but3.grid(row=11, column=1, sticky = W)

if __name__ == "__main__":
    while True:
        try:
            root.mainloop()
            import sys
            if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
                QtWidgets.QApplication.instance().exec_()
                break
        except Exception as e:
            print(e)
