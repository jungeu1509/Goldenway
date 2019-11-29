'''
#
# Team : Oh! Friends
# Project : Golden Way
# File : goldenway_img.py
# Author : 박소민
# Date : 2019.11.27
# Brief : 긴급 차량(구급차, 소방차) 영상 인식 프로세스
#
'''
import os
import sys
import signal 
import cv2
import time
from time import sleep
import subprocess
from multiprocessing import Process

# signal handler
def handler(signum, f):
    img_msg[2] = 'F'
    img_msg[3] = '3'
    fifo = open(S_PIPE_PATH, 'w')
    fifo.writelines(img_msg)
    fifo.close()
    
    print('> Image Process Ended!!')  
    os.unlink(S_PIPE_PATH)
    sys.exit()

# 카메라 연결 확인인
def cam_connect_check():
    # 카메라 연결 확인
    video_num = subprocess.check_output('ls /dev/video* | wc -l', shell=True)

    try:
        if int(len(video_num)) > 1:
            print('Camera connect success!')
    
    except SysError:
        print('Fail to excute')
        sys.exit()

    except OSError as err:
        print("OS error: {0}".format(err))

    except: 
        print('Camera connect fail! Check connection.')
        sys.exit()

# 좌측 카메라 처리 프로세스
def process_L():
    L_PIPE_PATH = "./img_msg_L.txt"
    LABEL_PATH = "./img_label_L.txt"
    DETECT_PATH = "./img_detect_L.txt"

    print('process_L start!')

    while True:
        # create_msg_L
        msg_L = ['none', '0x0']

        try:
            label_file = open(LABEL_PATH, '+r')
        except IOError:
            print('Failed to open file!')
            sys.exit()
        else:
            label_L = label_file.read()
            if label_L == 'none':
                label_file.close() 
            else:
                msg_L[0] = label_L
                label_file.seek(0)
                label_file.truncate()
                label_file.write('none')
                label_file.close()
                
                try:
                    detect_file = open(DETECT_PATH, '+r')
                except IOError:
                    print('Failed to open file!')
                    sys.exit()
                else:
                    detect_L = detect_file.read()
                    if detect_L == '0':
                        detect_file.close()
                    else:
                        msg_L[1] = '0x1'
                        detect_file.seek(0)
                        detect_file.truncate()
                        detect_file.write('0')
                        detect_file.close()
                        

        # send message
        try:
            fifo = open(L_PIPE_PATH, 'w')
        except IOError:
            print('Failed to open PIPE_L')
            sys.exit()
        else:
            fifo.writelines('\n'.join(msg_L))
            fifo.close()
            sleep(1)

    print('process_L finish!!')

# 우측 카메라 처리 프로세스
def process_R():
    R_PIPE_PATH = "./img_msg_R.txt"
    LABEL_PATH = "./img_label_R.txt"
    DETECT_PATH = "./img_detect_R.txt"

    print('process_R start!')

    while True:
        # create_msg_R 
        msg_R = ['none', '0x0']

        try:
            label_file = open(LABEL_PATH, '+r')
        except IOError:
            print('Failed to open file!')
            sys.exit()
        else:
            label_R = label_file.read()
            if label_R == 'none':
                label_file.close() 
            else:
                msg_R[0] = label_R
                label_file.seek(0)
                label_file.truncate()
                label_file.write('none')
                label_file.close()
                
                try:
                    detect_file = open(DETECT_PATH, '+r')
                except IOError:
                    print('Failed to open file!')
                    sys.exit()
                else:
                    detect_R = detect_file.read()
                    if detect_R == '0':
                        detect_file.close()
                    else:
                        msg_R[1] = '0xa'
                        detect_file.seek(0)
                        detect_file.truncate()
                        detect_file.write('0')
                        detect_file.close()
                        
        # send message
        try:
            fifo = open(R_PIPE_PATH, 'w')
        except IOError:
            print('Failed to open PIPE_L')
            sys.exit()
        else:
            fifo.writelines('\n'.join(msg_R))
            fifo.close()
            sleep(1)

    print('process_R finish!!')

# 메시지 전송 처리 프로세스
def process_send_msg():
    # 긴급 차량 종류
    emergency_car_classify = {  
                                'none':'0',
                                'ambulance':'1',
                                'firetruck':'2',
                                'complication':'3'
                                }

    # 긴급 차량 위치
    emergency_car_position = {
                                '0x0':'0',
                                '0x1':'1', 
                                '0xa':'2',
                                '0xb':'3'
                                }

    print('process_M start!')

    L_PIPE_PATH = "./img_msg_L.txt"
    R_PIPE_PATH = "./img_msg_R.txt"
    S_PIPE_PATH = "./IMG_MSG"

    try:
        os.mkfifo(S_PIPE_PATH)
    except IOError as e:
        print('Fail to make S_PIPE')
        sys.exit()
    else:
        img_msg = list('0200000000')

    while True:
        # input result to img_msg[]
        for i in range(15):
            img_msg[2] = '%X' %i
            for j in range(16):
                img_msg[3] = '%X' %j
                try:
                    L_fifo = open(L_PIPE_PATH, 'r')
                except IOError:
                    print('Failed to open L_PIPE')
                else:
                    msg_L = L_fifo.read().split()
                    L_fifo.close()

                try:
                    R_fifo = open(R_PIPE_PATH, 'r')
                except IOError:
                    print('Failed to open L_PIPE')
                else:
                    msg_R = R_fifo.read().split()
                    R_fifo.close()

                #combine_position()
                emergency_car_detect = hex(int(msg_L[1],16) + int(msg_R[1],16))
                img_msg[7] = emergency_car_position[emergency_car_detect] 
                
                #combine_label()
                if img_msg[7] == '0':
                    emergency_car_label = 'none'
                elif img_msg[7] == '1':
                    emergency_car_label = msg_L[0]
                elif img_msg[7] == '2':
                    emergency_car_label = msg_R[0]
                else:
                    if msg_L[0] == msg_R[0]:
                        emergency_car_label = msg_L[0]
                    else:
                        emergency_car_label = 'complication'
                
                img_msg[5] = emergency_car_classify[emergency_car_label]

                # send message
                try:
                    fifo = open(S_PIPE_PATH, 'w')
                    print('Send img_msg > '  + ''.join(img_msg))
                except IOError:
                    print('Failed to open S_PIPE')
                    sys.exit()
                else:
                    fifo.writelines(img_msg)
                    fifo.close()
                    sleep(1)
    print('process_M finish!!')


if __name__ == '__main__':

    L_PIPE_PATH = "./img_msg_L.txt"
    R_PIPE_PATH = "./img_msg_R.txt"
    S_PIPE_PATH = "./IMG_MSG"
    img_msg = list('0200000000')
    
    # 프로세스 객체 생성
    ps_L = Process(target=process_L, args=())
    ps_R = Process(target=process_R, args=())
    ps_M = Process(target=process_send_msg, args=())

    # Ctrl + C
    signal.signal(2, handler)   

    cam_connect_check()

    if int(subprocess.check_output("find /dev/ -name 'video0' | wc -l", shell=True)) == True:
        os.system('./darknet_L detector demo data/goldenway.data goldenway.cfg goldenway.weights -c 0 -i 0 &')
        ps_L.start()
        if int(subprocess.check_output("find /dev/ -name 'video1' | wc -l", shell=True)) == True:
            os.system('./darknet_R detector demo data/goldenway.data goldenway.cfg goldenway.weights -c 1 -i 0 &')
            ps_R.start()
    else: 
        print("Check Video Number!!")

    ps_M.start()

    # 프로세스 종료 대기
    ps_L.join()
    ps_R.join()
    ps_M.join()
