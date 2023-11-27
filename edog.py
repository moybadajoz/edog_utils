# This script implements a simple gait pattern that was derived from IK
# Author: J.-P. Ramirez-Paredes <jpiramirez@gmail.com> <jpi.ramirez@ugto.mx>
# University of Guanajuato, 2023

from pickletools import long4
import PySimpleGUI as sg
import serial
import numpy as np
import time
import math as m
from scipy.interpolate import UnivariateSpline
import scipy.interpolate as spi
import matplotlib.pyplot as plt


class edog():
    def __init__(self, ser: serial.serialwin32.Serial, leg1: tuple[int, int], leg2: tuple[int, int], leg3: tuple[int, int], leg4: tuple[int, int], inipwm: list, endpwm: list):
        self.ser = ser
        self.leg1 = self.leg(leg1[0], leg1[1], [inipwm[leg1[0]], inipwm[leg1[1]]],
                             [endpwm[leg1[0]], endpwm[leg1[1]]], (0, 7))
        self.leg2 = self.leg(leg2[0], leg2[1], [inipwm[leg2[0]], inipwm[leg2[1]]],
                             [endpwm[leg2[0]], endpwm[leg2[1]]], (0, 7))
        self.leg3 = self.leg(leg3[0], leg3[1], [inipwm[leg3[0]], inipwm[leg3[1]]],
                             [endpwm[leg3[0]], endpwm[leg3[1]]], (0, 7))
        self.leg4 = self.leg(leg4[0], leg4[1], [inipwm[leg4[0]], inipwm[leg4[1]]],
                             [endpwm[leg4[0]], endpwm[leg4[1]]], (0, 7))

    class leg:
        def __init__(self, hip: int, knee: int, inipwm: list[int, int], endpwm: list[int, int], position: list[float, float]):
            self.hip = self.servo(hip, inipwm[0], endpwm[0])
            self.knee = self.servo(knee, inipwm[1], endpwm[1])
            self.last_position = position

        class servo:
            def __init__(self, servo, inipwm, endpwm):
                self.servo = servo
                self.inipwm = inipwm
                self.endpwm = endpwm

            def _deg2pwm(self, ang: tuple[float, float]) -> tuple[int, int]:
                """
                Convierte un ángulo a un valor PWM para un motor específico.

                Args:
                    ang: El ángulo en grados.
                    motor: El número del motor (0, 1, 2, 3, 4, 5, 6 o 7).

                Returns:
                    El valor PWM para el motor especificado.
                """
                m = (self.endpwm-self.inipwm)/180
                return int(m*(ang+90)+self.inipwm)

        def _point2deg(self, point: tuple[float, float]) -> tuple[float, float]:
            """
            Convierte un punto 2D a sus valores de grados correspondientes.

            Args:
                point: Una tupla de dos números de punto flotante que representan el punto 2D.

            Returns:
                angHip: El valor del angulo de la cadera.
                angKnee: El valor del angulo de la rodilla.
            """
            y = point[1]
            x = -point[0]
            h = (x**2+y**2)**0.5
            h = h if h <= 10 else 10
            alpha = np.arccos((h/2)/5)
            angp = np.arctan(x/y)
            angHip = (angp+alpha)*(180/np.pi)
            angKnee = (2.0*((np.pi/2.0)-alpha)-np.pi)*(180/np.pi)
            angHip += 20
            angKnee += 57

            angHip = angHip if abs(angHip) <= 90 else m.copysign(90, angHip)
            angKnee = angKnee if abs(
                angKnee) <= 100 else m.copysign(100, angKnee)
            return angHip, angKnee

        def _point2pwm(self, point: tuple[float, float]) -> tuple[int, int]:
            '''
            convierte un punto (x, y) a pwm (hip, knee)

            Args: 
                point: (x, y)
                motors: (hip, knee)

            Returns:
                pwm: (hip pwm, knee pwm)
            '''
            ang = self._point2deg(point)
            return self.hip._deg2pwm(ang[0]), self.knee._deg2pwm(ang[1])

        def _get_servos(self):
            return self.hip.servo, self.knee.servo

    def _write(self, points: list[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]]):
        '''
        Procesa y envia las posiciones para las 4 piernas

        Args:
            points: lista de 4 tuplas [leg1, leg2, leg3, leg4]
                    cada tupla consta de (x, y)
        '''
        sval = np.zeros(8)
        sval[self.leg1._get_servos()[0]], sval[self.leg1._get_servos()[1]
                                               ] = self.leg1._point2pwm(points[0])
        sval[self.leg2._get_servos()[0]], sval[self.leg2._get_servos()[1]
                                               ] = self.leg2._point2pwm(points[1])
        sval[self.leg3._get_servos()[0]], sval[self.leg3._get_servos()[1]
                                               ] = self.leg3._point2pwm(points[2])
        sval[self.leg4._get_servos()[0]], sval[self.leg4._get_servos()[1]
                                               ] = self.leg4._point2pwm(points[3])
        msg = f'{sval[0]:.0f}:{sval[1]:.0f}:{sval[2]:.0f}:{sval[3]:.0f}:{sval[4]:.0f}:{sval[5]:.0f}:{sval[6]:.0f}:{sval[7]:.0f}:'
        ser.write(msg.encode())
        self.leg1.last_position = points[0]
        self.leg2.last_position = points[1]
        self.leg3.last_position = points[2]
        self.leg4.last_position = points[3]

    def get_last_positions(self):
        return self.leg1.last_position, self.leg2.last_position, self.leg3.last_position, self.leg4.last_position

    def animation(self, mov_l1: list, mov_l2: list, mov_l3: list, mov_l4: list, iterations=1) -> None:
        '''
        Realiza una animacion completa, envia directamente el mensaje al robot

        Args:
            mov_l1 = lista de movimientos para la pierna 1 lista[[x1, x2, x3, ..., xn], [y1, y2, y3, ..., yn]]
            mov_l2 = lista de movimientos para la pierna 2 lista[[x1, x2, x3, ..., xn], [y1, y2, y3, ..., yn]]
            mov_l3 = lista de movimientos para la pierna 3 lista[[x1, x2, x3, ..., xn], [y1, y2, y3, ..., yn]]
            mov_l4 = lista de movimientos para la pierna 4 lista[[x1, x2, x3, ..., xn], [y1, y2, y3, ..., yn]]
            n = numero de repeticiones de la animacion, default = 1
        '''
        for _ in range(iterations):
            for points in zip(zip(mov_l1[0], mov_l1[1]), zip(mov_l2[0], mov_l2[1]), zip(mov_l3[0], mov_l3[1]), zip(mov_l4[0], mov_l4[1])):
                self._write(points)
                time.sleep(0.0166)

    def set_position(self, point: tuple[float, float], legs=(True, True, True, True)):
        '''
        Establece una posicion para todas las piernas dado un punto

        Args:
            point = punto (x, y) 
            legs = tupla que permite mover o no ciertas piernas
        '''
        points = [(point) if legs[i] else self.get_last_positions()[i]
                  for i in range(4)]
        self._write(points)

    def set_position_(self, point: list[float, float], leg: tuple[float, float]):
        '''
        Establece una posicion para una pierna dado un punto

        Args:
            point = punto (x, y) 
            leg   = pierna (hip, knee)
        '''
        points = self.last_position.copy()
        for i, l in enumerate([self.leg1, self.leg2, self.leg3, self.leg4]):
            if l == leg:
                points[i] = point
        self._write(points)

    def animation2(self, xc, yc, t, n):
        ti = time.time()
        iterations = 1
        while iterations <= n:
            tt = time.time()-ti
            point = (spi.splev(tt, xc, der=0), spi.splev(tt, yc, der=0))
            if tt >= t:
                ti = time.time()
                iterations += 1
            self.set_position(point, (1, 1, 1, 1))
            time.sleep(0.015)

    def animation3(self, x, y, t, n, gap: list[float, float, float, float]):
        tt = np.linspace(0, t, len(x))
        xc = UnivariateSpline(tt, x)
        yc = UnivariateSpline(tt, y)

        xc.set_smoothing_factor(0.01)
        yc.set_smoothing_factor(0.01)

        iterations = 0
        tgap = [t*(g % 1) for g in gap]
        tini = time.time()
        tref = time.time() - tini
        while iterations < n:
            if (tref := time.time()-tini) >= t:
                iterations += 1
                tini = time.time()
                tref = time.time()-tini

            times = [(tref+g) % t for g in tgap]
            points = [(xc(i), yc(i)) for i in times]
            self._write(points)
            time.sleep(0.02)

    def animation_ind(self, x: list[list, list, list, list], y: list[list, list, list, list], gap: list[float, float, float, float], t: list[float, float, float, float], reverse: list[bool, bool, bool, bool], et):
        xf = [UnivariateSpline(np.linspace(0, t[i], len(x[i])), x[i][::-1] if reverse[i] else x[i])
              for i in range(4)]
        yf = [UnivariateSpline(np.linspace(0, t[i], len(y[i])), y[i][::-1] if reverse[i] else y[i])
              for i in range(4)]

        [f.set_smoothing_factor(0.01) for f in xf]
        [f.set_smoothing_factor(0.01) for f in yf]

        tgap = [tt*(g % 1) for tt, g in zip(t, gap)]
        tini = time.time()
        while (tref := time.time() - tini) < et:
            times = [(tref+g) % tt for tt, g in zip(t, tgap)]
            points = [(f_x(tt), f_y(tt))
                      for tt, f_x, f_y in zip(times, xf, yf)]
            self._write(points)
            time.sleep(0.02)


x = [0.0, -0.5, -1.0, -1.5, -2.0, -1.6, 1.6, 2.0, 1.5, 1.0, 0.5, 0.0]
y = [6.8, 6.9, 7.0, 7.2, 7.4, 6.2, 5.5, 6.4, 6.5, 6.6, 6.7, 6.8]

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
    [sg.Slider(range=(3, 10), default_value=6.5, resolution=0.1, change_submits=True,
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
             [sg.Button('Forward Right', size=(10, 0))]]


layout = [[sg.Column([[sg.Frame(title='Position Test', layout=layout_l, size=(380, 215))],
                      [sg.Frame(title='Mov Test', layout=layout_lb, size=(380, 205))]]
                     ),
           sg.Frame(title='Animation Test', layout=layout_r, size=(440, 425))],
          [sg.Button('Cancel')]]

window = sg.Window('eDog Servo Test', layout, finalize=True)

endpwm = [122, 120, 656, 655, 600, 600, 110, 111]
inipwm = [620, 605, 141, 148, 106,  105, 642, 613]

robot = edog(ser, leg1=(0, 4), leg2=(1, 5), leg3=(2, 6),
             leg4=(3, 7), inipwm=inipwm, endpwm=endpwm)
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
            robot.animation3(x, y, values['Speed'],
                             values['n'], (0, 0.5, 0, 0.5))
            robot.set_position((0, 6.5), (1, 1, 1, 1))
        case 'Backward':
            robot.animation3(x[::-1], y[::-1], values['Speed'],
                             values['n'], (0, 0.5, 0, 0.5))
            robot.set_position((0, 6.5), (1, 1, 1, 1))
        case 'Forward Left':
            xl = np.array([0.0, -0.25, -0.5, -0.75, -1.0, -1.25, -1.5, -1.75, -2.0, -
                           1.6, 0.65, 1.85, 1.75, 1.5, 1.25, 1.0, 0.75, 0.5, 0.25, 0.0])
            yl = np.array([6.8, 6.85, 6.9, 6.95, 7.0, 7.05, 7.1, 7.1, 7.0, 6.0,
                           5.5, 6.2, 6.4, 6.5, 6.55, 6.6, 6.65, 6.7, 6.75, 6.8])
            t = [values['Speed'] for _ in range(4)]
            robot.animation_ind([xl, xl, xl*0.0, xl*0.0], [yl, yl, yl, yl], [0, .6, 0, .6],
                                t, (False, False, False, False), values['n'])
            time.sleep(0.05)
            robot.set_position((0, 6.5), (1, 1, 1, 1))
        case 'Forward Right':
            xl = np.array([0.0, -0.25, -0.5, -0.75, -1.0, -1.25, -1.5, -1.75, -2.0, -
                           1.6, 0.65, 1.85, 1.75, 1.5, 1.25, 1.0, 0.75, 0.5, 0.25, 0.0])
            yl = np.array([6.8, 6.85, 6.9, 6.95, 7.0, 7.05, 7.1, 7.1, 7.0, 6.0,
                           5.5, 6.2, 6.4, 6.5, 6.55, 6.6, 6.65, 6.7, 6.75, 6.8])
            t = [values['Speed'] for _ in range(4)]
            robot.animation_ind([xl, xl*0.1, xl*0.2, xl], [yl, yl, yl, yl], [0, .5, 0, .5],
                                t, (True, True, False, False), values['n'])
            time.sleep(0.05)
            robot.set_position((0, 6.5), (1, 1, 1, 1))
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
                time.sleep(0.05)
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
                window['xg'].update(f"   X: {values['SliderX']:.0f}")
                window['hg'].update(f"Height: {values['SliderY']:.1f}")
                point = (values['SliderX'], values['SliderY'])
                robot.set_position(
                    point, legs=(values['leg1'], values['leg2'], values['leg3'], values['leg4']))


window.close()
ser.close()
