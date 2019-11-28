'''
#
# Team : Oh! Friends
# Project : Golden Way
# File : show.py
# Author : Eunwoo Jung
# Date : 2019.11.27
# Brief : GUI for monitor
#
'''

import os
import sys
import signal
import tkinter
import tkinter.font
import multiprocessing
import threading
import time

def handler(signum, f):
    PIPE_PATH = "./show_MSG"
    DATA_PATH = "./show_data.txt"
    os.unlink(PIPE_PATH)
    os.unlink(DATA_PATH)
    sys.exit()
    MyAPP.stop()

def fifo_run():
    PIPE_PATH = "./show_MSG"
    DATA_PATH = "./show_data.txt"
    while True:
        try:
            fifo = open(PIPE_PATH, 'r')
        except IOError:
            print('Failed to open FIFO')
            sys.exit()
        else:
            msg = fifo.readline()
            fifo.close()

        try:
            fifo_data = open(DATA_PATH, 'w')
        except IOError:
            print('Failed to open DATA_PATH')
            sys.exit()
        else:
            str_msg = ''.join(msg)
            fifo_data.write(str_msg)
            fifo_data.close()
            time.sleep(1)

class Tglobal(object):
    msg = list('AA0300000055')

class read_data(threading.Thread, Tglobal):
    DATA_PATH = "./show_data.txt"

    def __init(self):
        tkinter.Thread.__init__(self)

    def run(self):
        while True:
            time.sleep(1)
            try:
                fifo_data = open(MyAPP.DATA_PATH, 'r')
            except IOError:
                print('Failed to open DATA_PIPE')
                sys.exit()
            else:
                Tglobal.msg = fifo_data.readline()
                fifo_data.close()

class MyAPP(tkinter.Frame, Tglobal):
    DATA_PATH = "./show_data.txt"
    L_img_x = 100
    L_img_y = 22
    R_img_x = 400
    R_img_y = 22
    destroy_img = 0
    destroy_text = 0

    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent)

        self.bg_img = tkinter.PhotoImage(file = "/home/nvidia/goldenway/image/bg.gif")
        self.welcome_img = tkinter.PhotoImage(file = "/home/nvidia/goldenway/image/welcome.gif")
        self.normal_img = tkinter.PhotoImage(file = "/home/nvidia/goldenway/image/normal.gif")
        self.siren_img = tkinter.PhotoImage(file = "/home/nvidia/goldenway/image/siren.gif")
        self.ambulance_img = tkinter.PhotoImage(file = "/home/nvidia/goldenway/image/ambulance.gif")
        self.firetruck_img = tkinter.PhotoImage(file = "/home/nvidia/goldenway/image/firetruck.gif")
        self.left_img = tkinter.PhotoImage(file = "/home/nvidia/goldenway/image/left.gif")
        self.right_img = tkinter.PhotoImage(file = "/home/nvidia/goldenway/image/right.gif")

        self.rootfont=tkinter.font.Font(family="맑은 고딕", size=40)
        self.rootcfont=tkinter.font.Font(family="맑은 고딕", size=30)

        self.bglabel = tkinter.Label(image = self.bg_img)
        self.bglabel.place(x = 0, y = 0)

        self.tlabel1 = tkinter.Label(text = "Welcome!", font = self.rootfont, bg = "white")
        self.tlabel2 = tkinter.Label(text = "ⓒ 2019. Oh! Friends All Rights Reserved.", font = self.rootcfont, bg = "white")
        self.tlabel1.place(relx = 0.4, rely = 0.1, relwidth = 0.6, relheight = 0.3)
        self.tlabel2.place(relx = 0.4,rely = 0.5, relwidth = 0.6, relheight = 0.3)

        self.ilabel1 = tkinter.Label(image = self.welcome_img)
        self.ilabel1.place(x = MyAPP.L_img_x, y = MyAPP.L_img_y)
        self.ilabel2 = tkinter.Label(image = self.welcome_img)
        self.ilabel2.place(x = MyAPP.R_img_x, y = MyAPP.R_img_y)
        MyAPP.destroy_text = 1
        MyAPP.destroy_img = 0

        thread = read_data()
        thread.start()
        self.after(2000,self.check_Fifo)

    def check_Fifo(self):
        while True:
            msg = Tglobal.msg
            if msg[3] == '3':
                self.tlabel1.destroy()
                self.tlabel2.destroy()
                if MyAPP.destroy_text == 0 :
                    self.tlabel3.destroy()
                self.tlabel1 = tkinter.Label(text = "Golden Way", font = self.rootfont, bg = "white")
                self.tlabel2 = tkinter.Label(text = "안전운전하세요", font = self.rootfont, bg = "white")
                self.tlabel1.place(relx = 0.4, rely = 0.1, relwidth = 0.6, relheight = 0.3)
                self.tlabel2.place(relx = 0.4,rely = 0.5, relwidth = 0.6, relheight = 0.3)
                MyAPP.destroy_text = 1
                self.ilabel1.configure(image = self.normal_img)
                self.ilabel2.destroy()
                MyAPP.destroy_img = 1
                self.update()
            elif msg[3] == '0':
                self.tlabel1.destroy()
                self.tlabel2.destroy()
                if MyAPP.destroy_text == 0 :
                    self.tlabel3.destroy()
                self.tlabel1 = tkinter.Label(text = "긴급차량이 접근하고 있습니다!", font = self.rootfont, bg = "white")
                self.tlabel2 = tkinter.Label(text = "주의해주세요", font = self.rootfont, bg = "white")
                self.tlabel1.place(relx = 0.4, rely = 0.1, relwidth = 0.6, relheight = 0.3)
                self.tlabel2.place(relx = 0.4,rely = 0.5, relwidth = 0.6, relheight = 0.3)
                MyAPP.destroy_text = 1
                self.ilabel1.configure(image = self.siren_img)
                if MyAPP.destroy_img == 0 :
                    self.ilabel2.configure(image = self.siren_img)
                    self.ilabel2.place(x = MyAPP.R_img_x, y = MyAPP.R_img_y)
                else :
                    self.ilabel2 = tkinter.Label(image = self.siren_img)
                    self.ilabel2.place(x = MyAPP.R_img_x, y = MyAPP.R_img_y)
                    MyAPP.destroy_img = 0
                self.update()
            elif msg[3] == '1':
                self.tlabel1.destroy()
                self.tlabel2.destroy()
                if MyAPP.destroy_text == 0 :
                    self.tlabel3.destroy()
                self.tlabel1 = tkinter.Label(text = "구급차가 접근하고 있습니다!", font = self.rootfont, bg = "white")
                self.ilabel1.configure(image = self.ambulance_img)
                if msg[5] == '1':
                    self.tlabel2 = tkinter.Label(text = "현재 차선을 유지하거나", font = self.rootfont, bg = "white")
                    self.tlabel3 = tkinter.Label(text = "왼쪽으로 양보 부탁드립니다.", font = self.rootfont, bg = "white")
                    self.tlabel1.place(relx = 0.4, rely = 0.05, relwidth = 0.6, relheight = 0.3)
                    self.tlabel2.place(relx = 0.4, rely = 0.33, relwidth = 0.6, relheight = 0.3)
                    self.tlabel3.place(relx = 0.4, rely = 0.6, relwidth = 0.6, relheight = 0.3)
                    MyAPP.destroy_text = 0
                    if MyAPP.destroy_img == 0 :
                        self.ilabel2.configure(image = self.left_img)
                        self.ilabel2.place(x = MyAPP.R_img_x, y = MyAPP.R_img_y)
                    else:
                        self.ilabel2 = tkinter.Label(image = self.left_img)
                        self.ilabel2.place(x = MyAPP.R_img_x, y = MyAPP.R_img_y)
                        MyAPP.destroy_img = 0
                    self.update()
                elif msg[5] == '2':
                    self.tlabel2 = tkinter.Label(text = "현재 차선을 유지하거나", font = self.rootfont, bg = "white")
                    self.tlabel3 = tkinter.Label(text = "오른쪽으로 양보 부탁드립니다.", font = self.rootfont, bg = "white")
                    self.tlabel1.place(relx = 0.4, rely = 0.05, relwidth = 0.6, relheight = 0.3)
                    self.tlabel2.place(relx = 0.4, rely = 0.33, relwidth = 0.6, relheight = 0.3)
                    self.tlabel3.place(relx = 0.4, rely = 0.6, relwidth = 0.6, relheight = 0.3)
                    MyAPP.destroy_text = 0
                    if MyAPP.destroy_img == 0 :
                        self.ilabel2.configure(image = self.right_img)
                        self.ilabel2.place(x = MyAPP.R_img_x, y = MyAPP.R_img_y)
                    else:
                        self.ilabel2 = tkinter.Label(image = self.right_img)
                        self.ilabel2.place(x = MyAPP.R_img_x, y = MyAPP.R_img_y)
                        MyAPP.destroy_img = 0
                    self.update()
                else:
                    self.tlabel2 = tkinter.Label(text = "도로 상황에 따라 양보 부탁드립니다!", font = self.rootfont, bg = "white")
                    self.tlabel1.place(relx = 0.4, rely = 0.1, relwidth = 0.6, relheight = 0.3)
                    self.tlabel2.place(relx = 0.4, rely = 0.5, relwidth = 0.6, relheight = 0.3)
                    MyAPP.destroy_text = 1
                    if MyAPP.destroy_img == 0 :
                        self.ilabel2.configure(image = self.siren_img)
                        self.ilabel2.place(x = MyAPP.R_img_x, y = MyAPP.R_img_y)
                    else :
                        self.ilabel2 = tkinter.Label(image = self.siren_img)
                        self.ilabel2.place(x = MyAPP.R_img_x, y = MyAPP.R_img_y)
                        MyAPP.destroy_img = 0
                    self.update()
            elif msg[3] == '2':
                self.tlabel1.destroy()
                self.tlabel2.destroy()
                if MyAPP.destroy_text == 0 :
                    self.tlabel3.destroy()
                self.tlabel1 = tkinter.Label(text = "소방차가 접근하고 있습니다!", font = self.rootfont, bg = "white")
                self.ilabel1.configure(image = self.firetruck_img)
                if msg[5] == '1':
                    self.tlabel2 = tkinter.Label(text = "현재 차선을 유지하거나", font = self.rootfont, bg = "white")
                    self.tlabel3 = tkinter.Label(text = "왼쪽으로 양보 부탁드립니다.", font = self.rootfont, bg = "white")
                    self.tlabel1.place(relx = 0.4, rely = 0.05, relwidth = 0.6, relheight = 0.3)
                    self.tlabel2.place(relx = 0.4, rely = 0.33, relwidth = 0.6, relheight = 0.3)
                    self.tlabel3.place(relx = 0.4, rely = 0.6, relwidth = 0.6, relheight = 0.3)
                    MyAPP.destroy_text = 0
                    if MyAPP.destroy_img == 0 :
                        self.ilabel2.configure(image = self.left_img)
                        self.ilabel2.place(x = MyAPP.R_img_x, y = MyAPP.R_img_y)
                    else:
                        self.ilabel2 = tkinter.Label(image = self.left_img)
                        self.ilabel2.place(x = MyAPP.R_img_x, y = MyAPP.R_img_y)
                        MyAPP.destroy_img = 0
                    self.update()
                elif msg[5] == '2':
                    self.tlabel2 = tkinter.Label(text = "현재 차선을 유지하거나", font = self.rootfont, bg = "white")
                    self.tlabel3 = tkinter.Label(text = "오른쪽으로 양보 부탁드립니다.", font = self.rootfont, bg = "white")
                    self.tlabel1.place(relx = 0.4, rely = 0.05, relwidth = 0.6, relheight = 0.3)
                    self.tlabel2.place(relx = 0.4, rely = 0.33, relwidth = 0.6, relheight = 0.3)
                    self.tlabel3.place(relx = 0.4, rely = 0.6, relwidth = 0.6, relheight = 0.3)
                    MyAPP.destroy_text = 0
                    if MyAPP.destroy_img == 0 :
                        self.ilabel2.configure(image = self.right_img)
                        self.ilabel2.place(x = MyAPP.R_img_x, y = MyAPP.R_img_y)
                    else:
                        self.ilabel2 = tkinter.Label(image = self.right_img)
                        self.ilabel2.place(x = MyAPP.R_img_x, y = MyAPP.R_img_y)
                        MyAPP.destroy_img = 0
                    self.update()
                else:
                    self.tlabel2 = tkinter.Label(text = "도로 상황에 따라 양보 부탁드립니다!", font = self.rootfont, bg = "white")
                    self.tlabel1.place(relx = 0.4, rely = 0.1, relwidth = 0.6, relheight = 0.3)
                    self.tlabel2.place(relx = 0.4,rely = 0.5, relwidth = 0.6, relheight = 0.3)
                    MyAPP.destroy_text = 1
                    if MyAPP.destroy_img == 0 :
                        self.ilabel2.configure(image = self.siren_img)
                        self.ilabel2.place(x = MyAPP.R_img_x, y = MyAPP.R_img_y)
                    else :
                        self.ilabel2 = tkinter.Label(image = self.siren_img)
                        self.ilabel2.place(x = MyAPP.R_img_x, y = MyAPP.R_img_y)
                        MyAPP.destroy_img = 0
                    self.update()
            self.update()
            time.sleep(2)

if __name__ == '__main__':
    PIPE_PATH = "./show_MSG"
    DATA_PATH = "./show_data.txt"
    try:
        os.mkfifo(DATA_PATH)
    except IOError as e:
        print('Fail to make DATA_PIPE')
        sys.exit()

    root = tkinter.Tk()
    root.title("Goldenway")
    root.geometry("1536x245+0+0")

    runmp = multiprocessing.Process(target = fifo_run)
    signal.signal(2, handler)

    runmp.start()
    MyAPP(root)
    root.mainloop()

    runmp.join()
    os.unlink(PIPE_PATH)
    os.unlink(DATA_PATH)
