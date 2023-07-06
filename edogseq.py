# This script implements a simple gait pattern that was derived from IK
# Author: J.-P. Ramirez-Paredes <jpiramirez@gmail.com> <jpi.ramirez@ugto.mx>
# University of Guanajuato, 2023

import PySimpleGUI as sg
import serial
import numpy as np
import time

def deg2pwm(ang, motor):
    # minus 45
    inipwm = [255.0, 250.0, 505.0, 520.0, 570.0, 580.0, 200.0, 160.0]
    # plus 45
    endpwm = [505.0, 520.0, 230.0, 245.0, 335.0, 320.0, 425.0, 390.0]
    m = (endpwm[motor]-inipwm[motor])/90
    return int(m*(ang+45)+inipwm[motor])
    
qseq = np.array([[-35, -36, -38, -39, -41, -42, -44, -45, -46, -48, -49, -50, -52,
        -53, -54, -55, -57, -58, -59, -60, -59, -60, -60, -60, -60, -60,
        -59, -59, -58, -57, -56, -56, -54, -53, -52, -51, -49, -48, -46,
        -44, -43, -41, -39, -37, -35, -33, -32, -29, -27, -24, -21, -19,
        -18, -15, -13, -10,  -7,  -5,  -3,   0,   0,  -1,  -4,  -6,  -8,
        -10, -12, -14, -16, -17, -19, -21, -23, -25, -26, -28, -30, -32,
        -33, -35],
       [ 75,  75,  75,  74,  74,  74,  74,  73,  72,  72,  71,  71,  70,
         69,  69,  68,  68,  67,  66,  65,  63,  67,  70,  73,  75,  77,
         80,  81,  83,  85,  86,  88,  89,  90,  91,  92,  93,  93,  94,
         94,  95,  95,  95,  95,  95,  94,  94,  93,  92,  90,  87,  83,
         83,  80,  80,  75,  72,  70,  67,  64,  64,  63,  66,  67,  68,
         69,  70,  70,  71,  72,  72,  73,  73,  74,  74,  74,  75,  75,
         75,  75]])


sinit = [310, 310, 443, 458, 335, 320, 425, 390]


sservo = {'Leg1': (0,4), 'Leg2':(1,5), 'Leg3':(2,6), 'Leg4':(3,7)}
goffset = {'Leg1': 0, 'Leg2': 40, 'Leg3': 0, 'Leg4': 40}

ser = serial.Serial() 
ser.baudrate = 9600
ser.port = '/dev/ttyUSB0'
ser.open()

sg.theme('DarkAmber')  
layout = [  [sg.Text('Set each servo for eDog')],
            [sg.Button('Leg1'), sg.Button('Leg2'),sg.Button('Leg3'),sg.Button('Leg4')],
            [sg.Button('All'), sg.Button('Cancel')] ]


window = sg.Window('eDog Servo Test', layout)
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel' or event == 'Ok': 
        break
    print('You entered ', values)
    sval = [310, 310, 443, 458, 335, 320, 425, 390]
    if event == 'All':
        print('All')
        for k in range(0, qseq.shape[1], 1):
            for lkey in sservo:
                q1 = deg2pwm(qseq[0,(k+goffset[lkey])%qseq.shape[1]], sservo[lkey][0])
                q2 = deg2pwm(qseq[1,(k+goffset[lkey])%qseq.shape[1]], sservo[lkey][1])
                sval[sservo[lkey][0]] = q1
                sval[sservo[lkey][1]] = q2
            msg = ''
            for k in range(8):
                msg = msg + str(sval[k]) + ':'
            ser.write(msg.encode())
        for lkey in sservo:
            q1 = deg2pwm(qseq[0,40], sservo[lkey][0])
            q2 = deg2pwm(qseq[1,40], sservo[lkey][1])
            sval[sservo[lkey][0]] = q1
            sval[sservo[lkey][1]] = q2
        msg = ''
        for k in range(8):
            msg = msg + str(sval[k]) + ':'
        ser.write(msg.encode())
    else:
        femur = sservo[event][0]
        tibia = sservo[event][1]
        for k in range(0, qseq.shape[1], 4):
            p1 = deg2pwm(qseq[0,k], femur)
            p2 = deg2pwm(qseq[1,k], tibia)
            sval[femur] = p1
            sval[tibia] = p2
            msg = ''
            for k in range(8):
                msg = msg + str(sval[k]) + ':'
            ser.write(msg.encode())

window.close()
ser.close()
