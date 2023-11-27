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

# servo	0	1	2	3	4	5	6	7
# ini	120	123	656	633	616	604	110	111
# end	620	630	141	127	106	95	635	617
# min	89	89	89	89	90	89	90	89
# max	672	674	674	673	677	673	678	674


import PySimpleGUI as sg
import serial
from pprint import pprint


def deg2pwm(ang, motor):
    # minus 45

    inipwm = [270.0, 275.0, 505.0, 535.0, 630.0, 604.0, 162.0, 160.0]
    # plus 45
    endpwm = [515.0, 518.0, 247.0, 275.0, 386.0, 354.0, 423.0, 390.0]
    m = (endpwm[motor]-inipwm[motor])/90
    return int(m*(ang+45)+inipwm[motor])


def deg2pwm2(ang, motor, inipwm, endpwm):
    m = (endpwm[motor]-inipwm[motor])/180
    return int(m*(ang+90)+inipwm[motor])


sinit = [310, 310, 443, 458, 452, 450, 312, 275]

ser = serial.Serial()
ser.baudrate = 921600
ser.port = 'COM4'
ser.open()

sg.theme('DarkAmber')
# plus 90
# minus 90
endpwm = [122, 120, 656, 655, 600, 600, 110, 111]
# plus 90
inipwm = [620, 605, 141, 148, 106,  105, 642, 613]
layout = [[sg.Text('Set each servo for eDog')],
          [sg.Slider((-90, 90), 0, resolution=1),
           sg.Slider((-90, 90), 0, resolution=1),
           sg.Slider((-90, 90), 0, resolution=1),
           sg.Slider((-90, 90), 0, resolution=1),
           sg.Slider((-90, 90), 0, resolution=1),
           sg.Slider((-90, 90), 0, resolution=1),
           sg.Slider((-90, 90), 0, resolution=1),
           sg.Slider((-90, 90), 0, resolution=1)],
          # endpwm
          [sg.Slider((50, 700), endpwm[0], resolution=1),
           sg.Slider((50, 700), endpwm[1], resolution=1),
           sg.Slider((50, 700), endpwm[2], resolution=1),
           sg.Slider((50, 700), endpwm[3], resolution=1),
           sg.Slider((50, 700), endpwm[4], resolution=1),
           sg.Slider((50, 700), endpwm[5], resolution=1),
           sg.Slider((50, 700), endpwm[6], resolution=1),
           sg.Slider((50, 700), endpwm[7], resolution=1)],
          # inipwm
          [sg.Slider((50, 700), inipwm[0], resolution=1),
           sg.Slider((50, 700), inipwm[1], resolution=1),
           sg.Slider((50, 700), inipwm[2], resolution=1),
           sg.Slider((50, 700), inipwm[3], resolution=1),
           sg.Slider((50, 700), inipwm[4], resolution=1),
           sg.Slider((50, 700), inipwm[5], resolution=1),
           sg.Slider((50, 700), inipwm[6], resolution=1),
           sg.Slider((50, 700), inipwm[7], resolution=1)],
          [sg.Button('Ok'), sg.Button('Cancel')]]

window = sg.Window('eDog Servo Test', layout)
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel':
        break
    print('You entered ', values)
    print(event)
    for k in list(values.keys())[0:8]:
        print(deg2pwm2(values[k], k, list(values.values())[
            16:], list(values.values())[8:16:]))
    msg = ''
    for k in range(8):
        msg = msg + \
            str(deg2pwm2(values[k], k, list(values.values())[
                16:], list(values.values())[8:16:])) + ':'
    ser.write(msg.encode())

window.close()
ser.close()
