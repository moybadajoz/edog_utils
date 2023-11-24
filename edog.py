# This script implements a simple gait pattern that was derived from IK
# Author: J.-P. Ramirez-Paredes <jpiramirez@gmail.com> <jpi.ramirez@ugto.mx>
# University of Guanajuato, 2023

from pickletools import long4
import PySimpleGUI as sg
import serial
import numpy as np
import time
import math as m


class edog():
    def __init__(self, ser: serial.serialwin32.Serial, leg1: tuple[int, int], leg2: tuple[int, int], leg3: tuple[int, int], leg4: tuple[int, int], inipwm: list, endpwm: list):
        self.ser = ser
        self.leg1 = leg1
        self.leg2 = leg2
        self.leg3 = leg3
        self.leg4 = leg4
        self.inipwm = inipwm
        self.endpwm = endpwm
        self.last_position = [(0, 7), (0, 7), (0, 7), (0, 7)]

    def _deg2pwm(self, ang: float, motor: int) -> tuple[int, int]:
        """
        Convierte un ángulo a un valor PWM para un motor específico.

        Args:
            ang: El ángulo en grados.
            motor: El número del motor (0, 1, 2, 3, 4, 5, 6 o 7).

        Returns:
            El valor PWM para el motor especificado.
        """
        # # minus 90
        # endpwm = [122, 120, 656, 655, 600, 600, 110, 111]
        # # plus 90
        # inipwm = [620, 605, 141, 148, 106,  105, 642, 613]
        m = (self.endpwm[motor]-self.inipwm[motor])/180
        return int(m*(ang+90)+self.inipwm[motor])

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
        angHip += 18.5
        angKnee += 57

        angHip = angHip if abs(angHip) <= 90 else m.copysign(90, angHip)
        angKnee = angKnee if abs(angKnee) <= 90 else m.copysign(90, angKnee)
        return angHip, angKnee

    def _point2pwm(self, point: tuple[float, float], motors: tuple[int, int]) -> tuple[int, int]:
        '''
        convierte un punto (x, y) a pwm (hip, knee)

        Args: 
            point: (x, y)
            motors: (hip, knee)

        Returns:
            pwm: (hip pwm, knee pwm)
        '''
        ang = self._point2deg(point)
        pwms = tuple([self._deg2pwm(a, m) for a, m in zip(ang, motors)])
        return pwms

    def _write(self, points: list[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]]):
        '''
        Procesa y envia las posiciones para las 4 piernas

        Args:
            points: lista de 4 tuplas [leg1, leg2, leg3, leg4]
                    cada tupla consta de (x, y)
        '''
        sval = np.zeros(8)
        sval[self.leg1[0]], sval[self.leg1[1]
                                 ] = self._point2pwm(points[0], self.leg1)
        sval[self.leg2[0]], sval[self.leg2[1]
                                 ] = self._point2pwm(points[1], self.leg2)
        sval[self.leg3[0]], sval[self.leg3[1]
                                 ] = self._point2pwm(points[2], self.leg3)
        sval[self.leg4[0]], sval[self.leg4[1]
                                 ] = self._point2pwm(points[3], self.leg4)
        msg = f'{sval[0]:.0f}:{sval[1]:.0f}:{sval[2]:.0f}:{sval[3]:.0f}:{sval[4]:.0f}:{sval[5]:.0f}:{sval[6]:.0f}:{sval[7]:.0f}:'
        ser.write(msg.encode())
        self.last_position = list(points)

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

    def set_position(self, point: tuple[float, float], legs=(True, True, True, True)):
        '''
        Establece una posicion para todas las piernas dado un punto

        Args:
            point = punto (x, y) 
            legs = tupla que permite mover o no ciertas piernas
        '''
        points = [(point) if legs[i] else self.last_position[i]
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


# qseq = np.array([[0, -0.4, -0.8, -1.2, -1.6, -2,  -2, -0.6, 0.6,   2, 2, 2, 1.6, 1.2, 0.8, 0.4],
#                  [7,    7,  7,    7,  7,  7, 6.5,    6,   6, 6.5, 7, 7, 7, 7, 7, 7]])

# qseq = np.array([[3.00, 2.33, 1.66, 1.00, 0.33, -0.33, -1.00, -1.66, -2.33, -3.00, -3.00, -3.00, 0.00, 3.00, 3.00],
#                  [8.00, 8.00, 8.00, 8.00, 8.00,  8.00,  8.00,  8.00,  8.00,  8.00,  7.00,  6.00, 6.00, 6.00, 7.00]])


# sinit = [380, 385, 367, 382, 452, 450, 321, 275]

# sservo = {'Leg1': (0, 4), 'Leg2': (1, 5), 'Leg3': (2, 6), 'Leg4': (3, 7)}
# goffset = {'Leg1': 0, 'Leg2': 10, 'Leg3': 0, 'Leg4': 10}


ser = serial.Serial()
ser.baudrate = 9600
ser.port = 'COM4'
ser.open()

sg.theme('DarkAmber')
layout = [[sg.Text('Set each servo for eDog')],
          [sg.Checkbox('Leg1', default=True, key='leg1'), sg.Checkbox('Leg2', default=True, key='leg2'),
           sg.Checkbox('Leg3', default=True, key='leg3'), sg.Checkbox('Leg4', default=True, key='leg4')],
          [sg.Button('D'), sg.Button('R')],
          [sg.Slider((3, 10), 7, resolution=0.1, change_submits=True, enable_events=True, key='SliderY'),
           sg.Slider((-10, 10), 0, resolution=0.1, change_submits=True, enable_events=True, key='SliderX')],
          [sg.Button('Cancel')]]


window = sg.Window('eDog Servo Test', layout)

endpwm = [122, 120, 656, 655, 600, 600, 110, 111]
inipwm = [620, 605, 141, 148, 106,  105, 642, 613]

robot = edog(ser, leg1=(0, 4), leg2=(1, 5), leg3=(2, 6),
             leg4=(3, 7), inipwm=inipwm, endpwm=endpwm)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel':
        break
    print('You entered: ', values)
    print('Event: ', event)
    match event:
        case 'Cancel':
            break
        case sg.WIN_CLOSED:
            break
        case _:
            if event == 'SliderX' or event == 'SliderY':
                point = (values['SliderX'], values['SliderY'])
                robot.set_position_all(
                    point, legs=(values['leg1'], values['leg2'], values['leg3'], values['leg4']))
            pass

window.close()
ser.close()
