from edog_api import edog
import time
import numpy as np
import threading
import queue
import PySimpleGUI as sg
import serial
from scipy.interpolate import UnivariateSpline
import math as m


# : list[function, function, function, function]


def test_thread(robot, speed_in, steer_in, new, close):
    x = np.array([-2.0, -2.4, -2.8, -3.2, -3.6, -4.0, -
                  3.2, -0.8, 0.0, -0.4, -0.8, -1.2, -1.6, -2.0])
    y = np.array([6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 5.75,
                  5.7, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0])
    while (not new.is_set()) and (not close.is_set()):
        time.sleep(0.1)
    time_ini = time.time()
    time_ref = time.time() - time_ini
    while not close.is_set():
        speed = speed_in.get()
        steer = steer_in.get()
        new.clear()

        stop = False if speed else True
        if stop:
            ds = 0
            while (not new.is_set()) and (not close.is_set()):
                time.sleep(0.1)
            continue

        left = 1
        right = 1
        reverse = False
        if speed < 0:
            speed = 3.1 + speed
            reverse = True
        else:
            speed = 3.1 - speed

        if steer < 0:
            left = 1 + steer
        else:
            right = 1 - steer

        xf = [UnivariateSpline(np.linspace(0, speed, x.shape[0]), xi)
              for xi in [x*right, x*right, x*left, x*left]]
        [f.set_smoothing_factor(0.01) for f in xf]
        yf = [UnivariateSpline(np.linspace(0, speed, y.shape[0]), y)
              for _ in range(4)]
        [f.set_smoothing_factor(0.01) for f in yf]

        gap = [0.5, 0.25, 0.75, 0.0] if reverse else [0.5, 0.75, 0.25, 0.0]
        time_gap = [speed*g for g in gap]

        while (not new.is_set()) and (not close.is_set()):
            time_ref = time.time() - time_ini
            times = [((time_ref+g) % speed) if not reverse
                     else speed - ((time_ref+g) % speed)
                     for g in time_gap]

            points = [(fx(t), fy(t)) for fx, fy, t in zip(xf, yf, times)]

            robot.write(points)
            time.sleep(0.02)


ser = serial.Serial()
ser.baudrate = 921600
ser.port = 'COM4'
ser.open()
sg.theme('DarkGrey9')

layout_1 = [[sg.Slider(range=(-2.5, 2.5), default_value=0, resolution=0.1, k='speed', enable_events=True)],
            [sg.Slider(range=(-0.5, 0.5), default_value=0, resolution=0.1, k='steer', enable_events=True)]]

layout = [[sg.Frame(layout=layout_1, title='Control', size=(400, 400))]]

window = sg.Window('eDog Servo Test', layout, finalize=True)

endpwm = [122, 120, 656, 655, 600, 600, 110, 111]
inipwm = [620, 605, 141, 148, 106,  105, 642, 613]

robot = edog(ser, leg1=(0, 4), leg2=(1, 5), leg3=(2, 6),
             leg4=(3, 7), inipwm=inipwm, endpwm=endpwm)

speed_in = queue.Queue()
steer_in = queue.Queue()

new = threading.Event()
close = threading.Event()

thread = threading.Thread(target=test_thread,
                          args=(robot, speed_in, steer_in, new, close))

thread.start()

while True:
    event, values = window.read()
    match event:
        case sg.WIN_CLOSED:
            close.set()
            time.sleep(0.1)
            robot.set_position((-2, 6), (1, 1, 1, 1))
            time.sleep(0.1)
            ser.close()
            break
        case _:
            if event in {'speed', 'steer'}:

                speed_in.put(values['speed'])
                steer_in.put(values['steer'])
                time.sleep(0.1)
                new.set()
