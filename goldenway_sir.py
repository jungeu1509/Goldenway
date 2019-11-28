'''
#
# Team : Oh! Friends
# Project : Golden Way
# File : goldenway_img.py
# Author : 윤현호
# Date : 2019.11.27
# Brief : 사이렌 인식 프로세스
#
'''
import os
import sys
import signal 
import time
import pyaudio
import numpy as np
import subprocess
import matplotlib.pyplot as plt

from time import sleep
from multiprocessing import Process

# signal handler
def handler(signum, f):
    sir_msg[2] = 'F'
    sir_msg[3] = '2'
    fifo = open(S_PIPE_PATH, 'w')
    fifo.writelines(sir_msg)
    fifo.close()

    os.unlink(S_PIPE_PATH)
    sys.exit()

class SirenDetector:
    peak = [0, 1]
    data = []
    fftSig = []
    freq = []
    freqPeak = []
    np.set_printoptions(suppress=True)  # don't use scientific notation

    CHUNK = 4096  # number of data points to read at a time
    RATE = 44100  # time resolution of the recording device (Hz)

    ran3 = range(600, 700)
    ran4 = range(700, 800)
    ran5 = range(800, 900)
    ran6 = range(900, 1000)
    ran7 = range(1000, 1100)
    ran8 = range(1100, 1200)
    ran9 = range(1200, 1300)
    ran10 = range(1300, 1400)
    ran11 = range(1400, 1500)
    ranlist = []

    def __init__(self):
        self.p = pyaudio.PyAudio()  # start the PyAudio class
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=self.RATE,
                                  input=True,
                                  output=False,
                                  frames_per_buffer=self.CHUNK)  # uses default input device
        self.loop()

    # Main loop
    def loop(self):
        try:
            while True:
                self.data = self.audioinput()
                self.fft()
                self.sirenclass()

        except KeyboardInterrupt:
            self.p.close()

    # create a numpy array holding a single read of audio data
    def audioinput(self):  
        ret = self.stream.read(self.CHUNK)
        ret = np.fromstring(ret, dtype=np.int16)
        ret = ret * np.hanning(len(ret))  # smooth FFT results by windowing data
        return ret

    # perform Fourier transform & filtering by freq/pitch values
    def fft(self):  
        fftSig = abs(np.fft.fft(self.data).real)
        fftSig = fftSig[:int(len(fftSig)/2)]  # keep only first half
        self.fftSig = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in fftSig]

        freq = np.fft.fftfreq(self.CHUNK, 1.0/self.RATE)
        self.freq = freq[:int(len(freq)/2)]  # keep only first half

        for index, i in enumerate(self.freq):  # set fft value under 400 Hz and above 1500 Hz to 0
            if i <= 600 or i >= 1500:
                self.fftSig[index] = 0

        if np.max(self.fftSig) < 30000:  # set fft of signal values under 180000 to 0
            self.freqPeak = 0
        else:
            self.freqPeak = self.freq[np.where(self.fftSig == np.max(self.fftSig))[0][0]]+1  # freq peak extraction
        self.peak.append(self.freqPeak)  # peak array update. will create a list of peak values

    # siren classification
    def sirenclass(self):  
        # result pipe create
        R_PIPE_PATH = "./sir_detect_result.txt"
        detected_result = 'none'
        msg_R = ['none']
        
        for j in range(0, len(self.peak)):  # access to last element of peak frequency list
            if j == (len(self.peak) - 1):
                if int(self.peak[j]) in self.ran3:
                    self.ranlist.append(3)
                elif int(self.peak[j]) in self.ran4:
                    self.ranlist.append(4)
                elif int(self.peak[j]) in self.ran5:
                    self.ranlist.append(5)
                elif int(self.peak[j]) in self.ran6:
                    self.ranlist.append(6)
                elif int(self.peak[j]) in self.ran7:
                    self.ranlist.append(7)
                elif int(self.peak[j]) in self.ran8:
                    self.ranlist.append(8)
                elif int(self.peak[j]) in self.ran9:
                    self.ranlist.append(9)
                elif int(self.peak[j]) in self.ran10:
                    self.ranlist.append(10)
                elif int(self.peak[j]) in self.ran11:
                    self.ranlist.append(11)
                else:
                    self.ranlist.clear()
               
                # checking the list of elements to determine the siren pattern
                if len(self.ranlist) >= 15 and 11 not in self.ranlist:
                    detected_result = 'siren'
                else:
                    detected_result = 'none'

                msg_R[0] = detected_result

        try:
            fifo = open(R_PIPE_PATH, 'w')
        except IOError:
            print('Failed to open R_PIPE')
        else:
            fifo.writelines(msg_R)
            fifo.close()

# 메시지 전송 처리 프로세스
def process_send_msg():
    # result_dictionary
    emergency_sir_classify = {
                            'none':'0',
                            'siren':'1'
                            }

    print('process_M start!')

    # create PIPE
    R_PIPE_PATH = "./sir_detect_result.txt"
    S_PIPE_PATH = "./SIR_MSG"
    
    try:
        os.mkfifo(S_PIPE_PATH)
    except IOError as e:
        print('Fail to make S_PIPE')
        sys.exit()
    else:
        sir_msg = list('0100000000')

    while True:
        # input result to sir_msg[]
        for i in range(15):
            sir_msg[2] = '%X' %i
            for j in range(16):
                sir_msg[3] = '%X' %j
                try:
                    R_fifo = open(R_PIPE_PATH, 'r')
                except IOError:
                    print('Failed to open R_PIPE')
                else:
                    msg_R = R_fifo.read()
                    R_fifo.close()

                try:
                    sir_msg[5] = emergency_sir_classify[msg_R]
                except KeyError:
                    sir_msg[5] = emergency_sir_classify['none']

                # send message
                try:
                    fifo = open(S_PIPE_PATH, 'w')
                    print('Send sir_msg > '  + ''.join(sir_msg))
                except IOError:
                    print('Failed to open S_PIPE')
                    sys.exit()
                else:
                    fifo.writelines(sir_msg)
                    fifo.close()
                    sleep(1)
    print('process_M finish!!')

if __name__ == "__main__":
    sir_msg = list('0100000000')
    R_PIPE_PATH = "./sir_detect_result.txt"
    S_PIPE_PATH = "./SIR_MSG"

    # Ctrl + C
    signal.signal(2, handler)   

    # 프로세스 객체 생성
    ps_M = Process(target=process_send_msg, args=())
    ps_M.start()

    SirenDetector()

    # 프로세스 종료 대기
    ps_M.join() 
