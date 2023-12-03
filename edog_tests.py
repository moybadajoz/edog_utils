# This script implements a simple gait pattern that was derived from IK
# Author: J.-P. Ramirez-Paredes <jpiramirez@gmail.com> <jpi.ramirez@ugto.mx>
# University of Guanajuato, 2023

from pickletools import long4
import PySimpleGUI as sg
import serial
import numpy as np
import time
import math as m
import scipy.interpolate as spi
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt
from edog_api import edog


# Arreglo para x
x = np.array([-2.0, -2.4, -2.8, -3.2, -3.6, -4.0, -
              3.2, -0.8, 0.0, -0.4, -0.8, -1.2, -1.6, -2.0])
#Arreglo para y 
y = np.array([6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 5.75,
             5.7, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0])


xa = []
ya = []

ser = serial.Serial()
ser.baudrate = 921600
ser.port = 'COM4'
ser.open()

sg.theme('DarkAmber')

layout_l = [[sg.Column([
    [sg.Text('Active legs')],
    [sg.Checkbox('Leg4', default=True, key='leg4', size=(8, 0), pad=((10, 10), (0, 0))), sg.Checkbox(
        'Leg1', default=True, key='leg1', size=(8, 0), pad=((10, 10), (0, 0)))],
    [sg.Checkbox('Leg3', default=True, key='leg3', size=(8, 0), pad=((10, 10), (20, 0))), sg.Checkbox(
        'Leg2', default=True, key='leg2', size=(8, 0), pad=((10, 10), (20, 0)))],
]), sg.Column([
    [sg.Text('Height: 6.5', justification='center', key='hg'),
     sg.Text('   X: 0', justification='center', key='xg')],
    [sg.Slider(range=(0, 9), default_value=6.5, resolution=0.1, change_submits=True,
               enable_events=True, key='SliderY', orientation='v'),
     sg.Slider(range=(-10, 10), default_value=0, resolution=0.1, change_submits=True,
               enable_events=True, key='SliderX', orientation='v')
     ],
])]]

layout_r = [[sg.Button('Load'),  sg.Input(size=(56, 20), key='Input')],
            [sg.ProgressBar(100, size=(60, 10),
                            key='loadbar', orientation='h', visible=False)],

            [sg.Text(f'Gap Leg 4: 0%', size=(26, 0), justification='center', key=f'gl4'),
             sg.Text(f'Gap Leg 1: 0%', size=(26, 0), justification='center', key=f'gl1')],
            [sg.Slider(range=(0, 1), default_value=0, resolution=0.01, key=f'gap_l4', orientation='h', size=(23, 20), disable_number_display=True, enable_events=True),
             sg.Slider(range=(0, 1), default_value=0, resolution=0.01, key=f'gap_l1', orientation='h', size=(23, 20), disable_number_display=True, enable_events=True)],
            [sg.Text(f'Speed Leg 4: 2.5', size=(26, 0), justification='center', key=f'sl4'),
             sg.Text(f'Speed Leg 1: 2.5', size=(26, 0), justification='center', key=f'sl1')],
            [sg.Slider(range=(3, 0.1), default_value=0.6, resolution=0.1, key=f'speed_l4', orientation='h', size=(23, 20), disable_number_display=True, enable_events=True),
             sg.Slider(range=(3, 0.1), default_value=0.6, resolution=0.1, key=f'speed_l1', orientation='h', size=(23, 20), disable_number_display=True, enable_events=True)],
            [sg.Checkbox(text=f'Reverse Leg 4', pad=((55, 55), (0, 0)), size=(10, 0), key='r_l4'),
             sg.Checkbox(text=f'Reverse Leg 1', pad=((55, 55), (0, 0)), size=(10, 0), key='r_l1')],

            [sg.Text(f'Gap Leg 3: 0%', size=(26, 0), justification='center', key=f'gl3'),
             sg.Text(f'Gap Leg 2: 0%', size=(26, 0), justification='center', key=f'gl2')],
            [sg.Slider(range=(0, 1), default_value=0, resolution=0.01, key=f'gap_l3', orientation='h', size=(23, 20), disable_number_display=True, enable_events=True),
             sg.Slider(range=(0, 1), default_value=0, resolution=0.01, key=f'gap_l2', orientation='h', size=(23, 20), disable_number_display=True, enable_events=True)],
            [sg.Text(f'Speed Leg 3: 2.5', size=(26, 0), justification='center', key=f'sl3'),
             sg.Text(f'Speed Leg 2: 2.5', size=(26, 0), justification='center', key=f'sl2')],
            [sg.Slider(range=(3, 0.1), default_value=0.6, resolution=0.1, key=f'speed_l3', orientation='h', size=(23, 20), disable_number_display=True, enable_events=True),
             sg.Slider(range=(3, 0.1), default_value=0.6, resolution=0.1, key=f'speed_l2', orientation='h', size=(23, 20), disable_number_display=True, enable_events=True)],
            [sg.Checkbox(text=f'Reverse Leg 3', pad=((55, 55), (0, 0)), size=(10, 0), key='r_l3'),
             sg.Checkbox(text=f'Reverse Leg 2', pad=((55, 55), (0, 0)), size=(10, 0), key='r_l2')],
            [sg.Text(f'Ejecution Time: 2.0s', key='ettxt', size=(16, 0)), sg.Slider(range=(0.1, 10), default_value=2.0, resolution=0.1, key=f'et',
                                                                                    orientation='h', size=(31, 20), disable_number_display=True, enable_events=True)],
            [sg.Button('Run')]
            ]

layout_lb = [[sg.Text('Speed: 2.5', key='SpeedTxt', size=(10, 0)), sg.Slider(range=(3, 0.1), default_value=0.6, resolution=0.1, key='Speed', orientation='h', size=(23, 20), disable_number_display=True, enable_events=True)],
             [sg.Text('Iterations: 2', key='ItTxt', size=(10, 0)), sg.Slider(range=(1, 10), default_value=3, resolution=1,
                                                                             key='n', orientation='h', size=(23, 20), disable_number_display=True, enable_events=True)],
             [sg.Button('Forward', size=(10, 0))],
             [sg.Button('Backward', size=(10, 0))],
             [sg.Button('Forward Left', size=(10, 0))],
             [sg.Button('Forward Right', size=(10, 0))],
             #  [sg.Slider(range=(-90, 90), default_value=15.5, resolution=0.1, change_submits=True,
             #             enable_events=True, key='osHip', orientation='h'),
             #   sg.Slider(range=(-90, 90), default_value=65.0, resolution=0.1, change_submits=True,
             #             enable_events=True, key='osKnee', orientation='h')]
             ]


# Diseño de interfaz grafica 
layout = [[sg.Column([[sg.Frame(title='Position Test', layout=layout_l, size=(380, 215))],
                      [sg.Frame(title='Mov Test', layout=layout_lb, size=(380, 205))]]
                     ),
           sg.Frame(title='Animation Test', layout=layout_r, size=(440, 425))],
          [sg.Button('Cancel')]]

window = sg.Window('eDog Servo Test', layout, finalize=True)

endpwm = [122, 120, 656, 655, 600, 600, 110, 111]
inipwm = [620, 605, 141, 148, 106,  105, 642, 613]

# se inicializa el robot 
robot = edog(ser, leg1=(0, 4), leg2=(1, 5), leg3=(2, 6),
             leg4=(3, 7), inipwm=inipwm, endpwm=endpwm)

offsetHip = 15.5
offsetKnee = 65.0
#Espera la interacción del usuario con la interfaz, leyendo los eventos y los valores 
# asociados con esos evento
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel':
        break
    # print('You entered: ', values)
    # print('Event: ', event)
    match event:
        case 'Cancel':
            break
        case sg.WIN_CLOSED:
            break
        case 'Forward':
            ti = [values[f'Speed'] for i in range(4)]
            r = [values[f'r_l{i+1}'] for i in range(4)]
            robot.animation_ind([x, x, x, x], [y, y, y, y], [0.5, 0.75, 0.25, 0.0],
                                ti, (False, False, False, False), values['n'])
            time.sleep(0.1)
            robot.set_position((-2, 6.0), (1, 1, 1, 1))
        case 'Backward':
            ti = [values[f'Speed'] for i in range(4)]
            r = [values[f'r_l{i+1}'] for i in range(4)]
            robot.animation_ind([x, x, x, x],
                                [y, y, y, y],
                                [0.5, 0.25, 0.75, 0.0],
                                ti, (True, True, True, True), values['n'])
            time.sleep(0.1)
            robot.set_position((-2, 6.0), (1, 1, 1, 1))
        case 'Forward Left':
            ti = [values[f'Speed'] for i in range(4)]
            r = [values[f'r_l{i+1}'] for i in range(4)]
            robot.animation_ind([x, x, x*0.5, x*0.5], [y, y, y, y], [0.5, 0.75, 0.25, 0.0],
                                ti, (False, False, False, False), values['n'])
            time.sleep(0.1)
            robot.set_position((-2, 6.0), (1, 1, 1, 1))
        case 'Forward Right':
            ti = [values[f'Speed'] for i in range(4)]
            r = [values[f'r_l{i+1}'] for i in range(4)]
            robot.animation_ind([x, x, x, x], [y, y, y, y], [0.75, 0.5, 0.25, 0.0],
                                ti, (True, True, False, False), values['n'])
            time.sleep(0.1)
            robot.set_position((-2, 6.0), (1, 1, 1, 1))
        case 'Load':
            try:
                dic = eval(values['Input'])
                xa = [x for c, *_, x in dic.values() if c]
                ya = [y for c, y, *_ in dic.values() if c]
                window['loadbar'].update(visible=True)
                for i in range(101):
                    window['loadbar'].update(i)
                    time.sleep(0.01)
                window['Input'].update('')
                window['loadbar'].update(visible=False)

            except:
                pass
        case 'Run':
            if len(xa) > 0 and len(ya) > 0:
                gap = [values[f'gap_l{i+1}'] for i in range(4)]
                ti = [values[f'speed_l{i+1}'] for i in range(4)]
                r = [values[f'r_l{i+1}'] for i in range(4)]
                robot.animation_ind([xa, xa, xa, xa], [
                                    ya, ya, ya, ya], gap, ti, r, values['et'])
                time.sleep(0.1)
                robot.set_position((0, 6.5), (1, 1, 1, 1))

        case 'Speed':
            window['SpeedTxt'].update(
                value=f'Speed: {3.1-values["Speed"]:.1f}')
        case 'n':
            window['ItTxt'].update(value=f'Iterations: {values["n"]:.0f}')
        case 'gap_l1':
            window['gl1'].update(
                value=f'Gap Leg 1: {values["gap_l1"]*100:.0f}%')
        case 'gap_l2':
            window['gl2'].update(
                value=f'Gap Leg 2: {values["gap_l2"]*100:.0f}%')
        case 'gap_l3':
            window['gl3'].update(
                value=f'Gap Leg 3: {values["gap_l3"]*100:.0f}%')
        case 'gap_l4':
            window['gl4'].update(
                value=f'Gap Leg 4: {values["gap_l4"]*100:.0f}%')
        case 'speed_l1':
            window['sl1'].update(
                value=f'Speed Leg 1: {3.1-values["speed_l1"]:.1f}')
        case 'speed_l2':
            window['sl2'].update(
                value=f'Speed Leg 2: {3.1-values["speed_l2"]:.1f}')
        case 'speed_l3':
            window['sl3'].update(
                value=f'Speed Leg 3: {3.1-values["speed_l3"]:.1f}')
        case 'speed_l4':
            window['sl4'].update(
                value=f'Speed Leg 4: {3.1-values["speed_l4"]:.1f}')
        case 'et':
            window['ettxt'].update(
                value=f'Ejecution Time: {values["et"]}s')
        case _:
            if event == 'SliderX' or event == 'SliderY':
                window['xg'].update(f"   X: {values['SliderX']:.1f}")
                window['hg'].update(f"Height: {values['SliderY']:.1f}")
                point = (values['SliderX'], values['SliderY'])
                robot.set_position(
                    point, legs=(values['leg1'], values['leg2'], values['leg3'], values['leg4']))
            if event == 'osHip' or event == 'osKnee':
                offsetHip = values['osHip']
                offsetKnee = values['osKnee']

window.close()
ser.close()
