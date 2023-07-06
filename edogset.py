# This script can be used to calibrate the servos on the eDog robot.
# Motor Number    Joint
#      0          Front right hip
#      1          Rear right hip
#      2          Rear left hip
#      3          Front left hip
#      4          Front right knee
#      5          Rear right knee
#      6          Rear left knee
#      7          Front left knee
# Author: J.-P. Ramirez-Paredes <jpiramirez@gmail.com> <jpi.ramirez@ugto.mx>
# University of Guanajuato, 2023

import PySimpleGUI as sg
import serial

def deg2pwm(ang, motor):
    # minus 45
    inipwm = [255.0, 250.0, 505.0, 520.0, 570.0, 580.0, 200.0, 160.0]
    # plus 45
    endpwm = [505.0, 520.0, 230.0, 245.0, 335.0, 320.0, 425.0, 390.0]
    m = (endpwm[motor]-inipwm[motor])/90
    return int(m*(ang+45)+inipwm[motor])

sinit = [260, 255, 475, 495, 165, 180, 565, 550]

ser = serial.Serial() 
ser.baudrate = 9600
ser.port = '/dev/ttyUSB0'
ser.open()

sg.theme('DarkAmber')   
layout = [  [sg.Text('Set each servo for eDog')],
            [sg.Slider((-90,90), -25, resolution=5), sg.Slider((-90,90), -25, resolution=5), \
             sg.Slider((-90,90), -25, resolution=5), sg.Slider((-90,90), -25, resolution=5), \
             sg.Slider((-90,90), 45, resolution=5), sg.Slider((-90,90), 45, resolution=5), \
             sg.Slider((-90,90), 45, resolution=5), sg.Slider((-90,90), 45, resolution=5)],
            [sg.Button('Ok'), sg.Button('Cancel')] ]

window = sg.Window('eDog Servo Test', layout)
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': 
        break
    print('You entered ', values)
    print(event)
    for key in values:
    	print(deg2pwm(values[key], key))
    msg = ''
    for k in range(8):
        msg = msg + str(deg2pwm(values[k], k)) + ':'
    ser.write(msg.encode())

window.close()
ser.close()
