# Use Python 3

from os import walk
import cv2
import time
import sys
import random

import sys
import tkinter
from PIL import Image, ImageTk

def exit():
    system.exit()

global imagesprite
global image
global pilImage

# Time to show each image in seconds
IMTIME = 1

root = tkinter.Tk()
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.overrideredirect(1)
root.geometry("%dx%d+0+0" % (w, h))
root.focus_set()
root.bind("<Escape>", lambda e: (e.widget.withdraw(), e.widget.quit()))
canvas = tkinter.Canvas(root,width=w,height=h)
canvas.pack()
canvas.configure(background='black')

def simg(name):
    global pilImage
    global image
    global imagesprite
    global canvas
    pilImage = Image.open(name)
    imgWidth, imgHeight = pilImage.size
    if imgWidth > w or imgHeight > h:
        ratio = min(w/imgWidth, h/imgHeight)
        imgWidth = int(imgWidth*ratio)
        imgHeight = int(imgHeight*ratio)
    pilImage = pilImage.resize((imgWidth,imgHeight), Image.ANTIALIAS)
    image = ImageTk.PhotoImage(pilImage)
    imagesprite = canvas.create_image(w/2,h/2,image=image)

ord = []

def img():
    global ord
    if len(ord) < 1:
        tmp = []
        for f in flist:
            tmp.append(f)
        while len(tmp) > 0:
            ord.append(tmp.pop(random.randint(0, len(tmp)-1)))
    simg(ord.pop())
    root.after(IMTIME*1000, img)

root.after(0, img)
root.mainloop()
