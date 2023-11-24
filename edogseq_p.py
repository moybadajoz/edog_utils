# This script implements a simple gait pattern that was derived from IK
# Author: J.-P. Ramirez-Paredes <jpiramirez@gmail.com> <jpi.ramirez@ugto.mx>
# University of Guanajuato, 2023

from pickletools import long4
import PySimpleGUI as sg
import serial
import numpy as np
import time
import math as m


def deg2pwm(ang: float, motor: int):
    """
    Convierte un ángulo a un valor PWM para un motor específico.

    Args:
        ang: El ángulo en grados.
        motor: El número del motor (0, 1, 2, 3, 4, 5, 6 o 7).

    Returns:
        El valor PWM para el motor especificado.
    """
    # minus 90
    endpwm = [122, 120, 656, 655, 600, 600, 110, 111]
    # plus 90
    inipwm = [620, 605, 141, 148, 106,  105, 642, 613]
    m = (endpwm[motor]-inipwm[motor])/180
    return int(m*(ang+90)+inipwm[motor])


def convertir_rango(limite_inferior_entrada, limite_superior_entrada, limite_inferior_salida, limite_superior_salida, valor_entrada):
    """
    Convierte un valor de entrada de un rango a otro.

    Args:
      limite_inferior_entrada: El limite inferior del rango de entrada.
      limite_superior_entrada: El limite superior del rango de entrada.
      limite_inferior_salida: El limite inferior del rango de salida.
      limite_superior_salida: El limite superior del rango de salida.
      valor_entrada: El valor de entrada a convertir.

    Returns:
      El valor de entrada convertido.
    """

    # Calculamos el factor de escala.

    factor_escala = (limite_superior_salida - limite_inferior_salida) / \
        (limite_superior_entrada - limite_inferior_entrada)

    # Convertimos el valor de entrada.

    valor_convertido = limite_inferior_salida + \
        factor_escala * (valor_entrada - limite_inferior_entrada)

    return valor_convertido


def point2deg(point: tuple[float, float]):
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


def point2pwm(point: tuple[float, float], motors: tuple[int, int]):
    '''
    convierte un punto (x, y) a pwm (hip, knee)

    Args: 
        point: (x, y)
        motors: (hip, knee)

    Returns:
        pwm: (hip pwm, knee pwm)
    '''
    ang = point2deg(point)
    pwms = tuple([deg2pwm(a, m) for a, m in zip(ang, motors)])
    return pwms


def animation(ser: serial.serialwin32.Serial, leg1: tuple[int, int], leg2: tuple[int, int], leg3: tuple[int, int], leg4: tuple[int, int], mov_l1: list, mov_l2: list, mov_l3: list, mov_l4: list, n=1):
    '''
    Realiza una animacion completa, envia directamente el mensaje al robot

    Args:
        ser = serial del robot
        leg1 = tupla de motores para la pierna 1 (hip, knee)
        leg2 = tupla de motores para la pierna 2 (hip, knee)
        leg3 = tupla de motores para la pierna 3 (hip, knee)
        leg4 = tupla de motores para la pierna 4 (hip, knee)
        mov_l1 = lista de movimientos para la pierna 1 lista[[x1, x2, x3, ..., xn], [y1, y2, y3, ..., yn]]
        mov_l2 = lista de movimientos para la pierna 2 lista[[x1, x2, x3, ..., xn], [y1, y2, y3, ..., yn]]
        mov_l3 = lista de movimientos para la pierna 3 lista[[x1, x2, x3, ..., xn], [y1, y2, y3, ..., yn]]
        mov_l4 = lista de movimientos para la pierna 4 lista[[x1, x2, x3, ..., xn], [y1, y2, y3, ..., yn]]
        n = numero de repeticiones de la animacion, default = 1
    '''
    for _ in range(n):
        for l1, l2, l3, l4 in zip(zip(mov_l1[0], mov_l1[1]), zip(mov_l2[0], mov_l2[1]), zip(mov_l3[0], mov_l3[1]), zip(mov_l4[0], mov_l4[1])):
            sval[leg1[0]], sval[leg1[1]] = point2pwm(l1, leg1)
            sval[leg2[0]], sval[leg2[1]] = point2pwm(l2, leg2)
            sval[leg3[0]], sval[leg3[1]] = point2pwm(l3, leg3)
            sval[leg4[0]], sval[leg4[1]] = point2pwm(l4, leg4)
            msg = f'{sval[0]}:{sval[1]}:{sval[2]}:{sval[3]}:{sval[4]}:{sval[5]}:{sval[6]}:{sval[7]}:'
            ser.write(msg.encode())


qseq = np.array([[0, -0.4, -0.8, -1.2, -1.6, -2,  -2, -0.6, 0.6,   2, 2, 2, 1.6, 1.2, 0.8, 0.4],
                 [7,    7,  7,    7,  7,  7, 6.5,    6,   6, 6.5, 7, 7, 7, 7, 7, 7]])

qseq = np.array([[3.00, 2.33, 1.66, 1.00, 0.33, -0.33, -1.00, -1.66, -2.33, -3.00, -3.00, -3.00, 0.00, 3.00, 3.00],
                 [8.00, 8.00, 8.00, 8.00, 8.00,  8.00,  8.00,  8.00,  8.00,  8.00,  7.00,  6.00, 6.00, 6.00, 7.00]])


sinit = [380, 385, 367, 382, 452, 450, 321, 275]

sservo = {'Leg1': (0, 4), 'Leg2': (1, 5), 'Leg3': (2, 6), 'Leg4': (3, 7)}
goffset = {'Leg1': 0, 'Leg2': 10, 'Leg3': 0, 'Leg4': 10}

ser = serial.Serial()
ser.baudrate = 9600
ser.port = 'COM4'
ser.open()
print(type(ser))

sg.theme('DarkAmber')
layout = [[sg.Text('Set each servo for eDog')],
          [sg.Button('All'), sg.Button('9 test'),
           sg.Button('4 test'), sg.Button('Cancel')],
          [sg.Button('D'), sg.Button('R')],
          [sg.Slider((3, 10), 5, resolution=0.1, change_submits=True), sg.Slider((-10, 10), 0, resolution=0.1, change_submits=True)]]


window = sg.Window('eDog Servo Test', layout)
prevH = 0
prevV = 5
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel' or event == 'Ok':
        break
    print('You entered ', values)
    sval = [380, 385, 367, 382, 452, 450, 321, 275]
    if event == 'All':
        print('All')
        for _ in range(10):
            for k in range(0, qseq.shape[1], 1):
                for lkey in sservo:
                    q1 = deg2pwm(qseq[0, (k+goffset[lkey]) %
                                      qseq.shape[1]], sservo[lkey][0])
                    q2 = deg2pwm(qseq[1, (k+goffset[lkey]) %
                                      qseq.shape[1]], sservo[lkey][1])
                    sval[sservo[lkey][0]] = q1
                    sval[sservo[lkey][1]] = q2
                msg = ''
                for k in range(8):
                    msg = msg + str(sval[k]) + ':'
                ser.write(msg.encode())
            for lkey in sservo:
                q1 = deg2pwm(qseq[0, len(qseq)], sservo[lkey][0])
                q2 = deg2pwm(qseq[1, len(qseq)], sservo[lkey][1])
                sval[sservo[lkey][0]] = q1
                sval[sservo[lkey][1]] = q2
            msg = ''
        for k in range(8):
            msg = msg + str(sval[k]) + ':'
        ser.write(msg.encode())
    elif event == '4 test':
        for p in zip(np.linspace(2, -2, 30), np.linspace(5, 5, 30)):
            ang = point2deg(p)
            print(p)
            for i in range(4):
                sval[i] = deg2pwm(ang[0], i)
                sval[i+4] = deg2pwm(ang[1], i+4)
            msg = ''
            for k in range(8):
                msg = msg + str(sval[k]) + ':'
            ser.write(msg.encode())
        for p in zip(np.linspace(-2, 2, 30), np.linspace(5, 5, 30)):
            ang = point2deg(p)
            print(p)
            for i in range(4):
                sval[i] = deg2pwm(ang[0], i)
                sval[i+4] = deg2pwm(ang[1], i+4)
            msg = ''
            for k in range(8):
                msg = msg + str(sval[k]) + ':'
            ser.write(msg.encode())
    elif event == '9 test':
        for p in zip(np.linspace(prevH, values[1], 30), np.linspace(prevV, values[0], 30)):
            for i in range(4):
                sval[i], sval[i+4] = point2pwm(p, (i, i+4))
            msg = ''
            for k in range(8):
                msg = msg + str(sval[k]) + ':'
            ser.write(msg.encode())
        prevV = values[0]
        prevH = values[1]
    elif event == 'D':
        goffset = {
            'Leg1': 0, 'Leg2': qseq.shape[1]//2, 'Leg3': 0, 'Leg4': qseq.shape[1]//2}
        l1 = qseq
        l3 = qseq
        l2 = np.array([np.roll(qseq[0], goffset['Leg2']),
                      np.roll(qseq[1], goffset['Leg2'])])
        l4 = np.array([np.roll(qseq[0], goffset['Leg4']),
                      np.roll(qseq[1], goffset['Leg4'])])
        animation(ser, sservo['Leg1'], sservo['Leg2'],
                  sservo['Leg3'], sservo['Leg4'], l1, l2, l3, l4, 3)
        animation(ser, sservo['Leg1'], sservo['Leg2'],
                  sservo['Leg3'], sservo['Leg4'], [[0], [7]], [
                  [0], [7]], [[0], [7]], [[0], [7]], 1)
    elif event == 'R':
        goffset = {
            'Leg1': 0, 'Leg2': qseq.shape[1]//2, 'Leg3': 0, 'Leg4': qseq.shape[1]//2}
        l1 = qseq[::, ::-1]
        l3 = qseq[::, ::-1]
        l2 = np.array([np.roll(qseq[0][::-1], goffset['Leg2']),
                      np.roll(qseq[1][::-1], goffset['Leg2'])])
        l4 = np.array([np.roll(qseq[0][::-1], goffset['Leg4']),
                      np.roll(qseq[1][::-1], goffset['Leg4'])])
        animation(ser, sservo['Leg1'], sservo['Leg2'],
                  sservo['Leg3'], sservo['Leg4'], l1, l2, l3, l4, 3)
        animation(ser, sservo['Leg1'], sservo['Leg2'],
                  sservo['Leg3'], sservo['Leg4'], [[0], [7]], [
                  [0], [7]], [[0], [7]], [[0], [7]], 1)
    else:
        for i in range(4):
            sval[i], sval[i +
                          4] = point2pwm((values[1], values[0]), (i, i+4))
        msg = ''
        for k in range(8):
            msg = msg + str(sval[k]) + ':'
        ser.write(msg.encode())
        print(msg)
        prevV = values[0]
        prevH = values[1]

window.close()
ser.close()
