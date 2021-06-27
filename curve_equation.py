import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import xlrd
import array
import math
from scipy import stats
from scipy.optimize import curve_fit
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import tkinter.messagebox
from tkinter import *

def func(x,a,b,c):
    return a*np.exp(-b*x)+c

def poly_fit(xdata,ydata):    
    popt,pcov = curve_fit(func,xdata,ydata)
    y_predict = func(xdata, *popt)
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.plot(xdata, ydata, '.',label='Original')
    plt.plot(xdata, y_predict, '-',label='Fitted')
    #print(popt[0])
    a = str(round(popt[0],2))
    b = str(round(popt[1],3))
    c = str(round(popt[2],2))
    #eqn = 'y = '+a+r'$e^$'+b+'t'+c
    eqn = 'y = '+a+' exp('+b+' t) + '+c
    plt.text(0.9, 0.2,eqn,horizontalalignment='right',verticalalignment='center',transform = ax.transAxes)
    #plt.text(0.9, 0.1,eqn1,horizontalalignment='right',verticalalignment='center',transform = ax.transAxes)
    plt.legend() 
    plt.show()
    
def linear_regresion(xdata,ydata):
    sinQ = np.sin(xdata*math.pi/180)
    xdata = 1.6314*sinQ
    #xdata = 1.7342*sinQ
    slope, intercept, r_value, p_value, std_err = stats.linregress(xdata,ydata)
    slope = round(slope,3)
    intercept = round(intercept,3)    
    X_Running = np.linspace(min(xdata), max(xdata), sheet.nrows/2)
    Y_estimated = (slope*X_Running)+ intercept
    m = str(slope)
    c = str(intercept)
    eqn = r'$y = $'+m+r'$\ \varkappa + $'+c
    eqn1 = r'$R^2 = $'+str(round((r_value*r_value),3))
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.plot(xdata, ydata, '.',label='Original')
    plt.plot(X_Running, Y_estimated, '-',label='Fitted')
    plt.text(0.9, 0.2,eqn,horizontalalignment='right',verticalalignment='center',transform = ax.transAxes)
    plt.text(0.9, 0.1,eqn1,horizontalalignment='right',verticalalignment='center',transform = ax.transAxes)
    plt.legend() 
    plt.show()
    
        
def getExcel():
    global xdata,ydata,sheet
    book = xlrd.open_workbook(filedialog.askopenfilename())
    sheet = book.sheet_by_name('Sheet1')    
    sheet.cell_value(0, 0)    
    xdata = np.array([], dtype = np.float32)
    ydata = np.array([], dtype = np.float32)
    tempx = np.array([], dtype = np.float32)
    tempy = np.array([], dtype = np.float32)
    i=0
    if (var.get()=="Damping coefficient"):        
        while (i<sheet.nrows):
            if (i%2)>0:
                tempx = np.append(tempx, sheet.cell_value(i, 0)) 
            else:
                if (sheet.cell_value(i, 0)>180):
                    tempy = np.append(tempy, (sheet.cell_value(i, 0)-360))
                else:
                    tempy = np.append(tempy, sheet.cell_value(i, 0))           
            i+=1    
        prev=0
        curr=0
        #print(tempy.size)
        for j in range(tempy.size):
            if (j>=1):
                curr = tempy[j]-tempy[j-1]
        
            if((curr<0)and(prev>=0)):
                if (tempy[j-1]>0):
                    ydata = np.append(ydata,tempy[j-1])
                    xdata = np.append(xdata,tempx[j-1])
                    #print(tempy[j-1])
                
            prev = curr
        #print(ydata)
        poly_fit(xdata,ydata)
    else:
        while (i<sheet.nrows):
            if (i%2)>0:
                xdata = np.append(xdata, sheet.cell_value(i, 0)) 
            else:
                ydata = np.append(ydata, sheet.cell_value(i, 0))
            i+=1            
        linear_regresion(xdata,ydata)

        
root =tk.Tk()
root.title('Thrust Vs Voltage Relationship')
canvas1 = tk.Canvas(root, width = 300, height = 300, bg = 'lightsteelblue')
canvas1.pack()
browseButton_Excel = tk.Button(text='Import Excel File', command=getExcel, bg='green', fg='white', font=('helvetica', 12, 'bold'))
canvas1.create_window(150, 150, window=browseButton_Excel)
var = tk.StringVar()
var.set("Thrust Vs DC")
check_button = tk.OptionMenu(root,var,"Thrust Vs DC","Damping coefficient")
canvas1.create_window(150, 250, window=check_button)
root.mainloop()
