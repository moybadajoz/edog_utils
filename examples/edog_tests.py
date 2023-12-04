# This script implements a simple gait pattern that was derived from IK
# Author: J.-P. Ramirez-Paredes <jpiramirez@gmail.com> <jpi.ramirez@ugto.mx>
# University of Guanajuato, 2023

import PySimpleGUI as sg
import numpy as np
import time
from scipy.interpolate import UnivariateSpline
from api.edog_api import edog
from pyModbusTCP.client import ModbusClient


def animation(robot: edog, x: list[list, list, list, list], y: list[list, list, list, list], gap: list[float, float, float, float], t: list[float, float, float, float], reverse: list[bool, bool, bool, bool], et):
    """
    Anima el movimiento del robot interpolando las trayectorias de las patas.

    Parámetros:
    - robot: Objeto edog.
    - x: Lista de listas que representan las coordenadas x de las trayectorias de las cuatro patas.
    - y: Lista de listas que representan las coordenadas y de las trayectorias de las cuatro patas.
    - gap: Lista de valores que representan la fase de desfase (gap) para cada pata.
    - t: Lista de valores que representan el tiempo total de cada trayectoria para las cuatro patas.
    - reverse: Lista de booleanos que indica si se debe invertir la trayectoria de cada pata.
    - et: Tiempo total de ejecución de la animación.

    Notas:
    - Se utiliza interpolación univariante para suavizar las trayectorias.
    - El desfase 'gap' determina en qué punto de la trayectoria comienza cada pata.
    - La animación se ejecuta durante el tiempo especificado por 'et'.
    - Se utiliza la función 'write' del objeto 'robot' para enviar las posiciones calculadas.
    """
    # Crear funciones de interpolación para las coordenadas x e y de cada pata
    xf = [UnivariateSpline(np.linspace(0, t[i], len(x[i])), x[i], s=0.01)
          for i in range(4)]
    yf = [UnivariateSpline(np.linspace(0, t[i], len(y[i])), y[i], s=0.01)
          for i in range(4)]

    # Calcular el tiempo de desfase para cada pata
    tgap = [tt*(g % 1) for tt, g in zip(t, gap)]
    # Obtener el tiempo de inicio de la animación
    tini = time.time()
    # Bucle principal de la animación
    while (tref := time.time() - tini) < et:
        # Calcular los tiempos ajustados para cada pata
        times = [(tref+g) % tt for tt, g in zip(t, tgap)]
        # Calcular las coordenadas (x, y) para cada pata en el tiempo actual
        points = [(f_x(ti-tt if r else tt), f_y(ti-tt if r else tt))
                  for ti, tt, f_x, f_y, r in zip(t, times, xf, yf, reverse)]
        # Enviar las posiciones calculadas al robot
        robot.write(points)
        # Esperar un breve periodo de tiempo para mantener la frecuencia de actualización
        time.sleep(0.02)


# Definición de coordenadas x e y para el patrón de marcha
x = np.array([-2.0, -2.4, -2.8, -3.2, -3.6, -4.0, -
              3.2, -0.8, 0.0, -0.4, -0.8, -1.2, -1.6, -2.0])
y = np.array([6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 5.75,
             5.7, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0])

# Listas para almacenar coordenadas cargadas desde un archivo
xa = []
ya = []

# Configuración de parámetros de conexión Modbus TCP
SERVER_HOST = "192.168.4.1"  # IP del ESP32
SERVER_PORT = 502   # Puerto
IDX_REG = 0  # Índice del registro

# Creación del cliente Modbus
client = ModbusClient(host=SERVER_HOST, port=SERVER_PORT,
                      auto_open=True, debug=False)
client.timeout = 0.1

# Configuración del tema de PySimpleGUI
sg.theme('DarkAmber')

# Diseño de la interfaz gráfica
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

# Creación de la ventana
layout = [[sg.Frame(title='Position Test', layout=layout_l, size=(380, 375)),
           sg.Frame(title='Animation Test', layout=layout_r, size=(440, 375))],
          [sg.Button('Cancel')]]

window = sg.Window('eDog Servo Test', layout, finalize=True)

endpwm = [105, 120, 600, 655, 612, 600, 110, 111]
inipwm = [606, 605, 120, 148, 106,  105, 642, 665]

robot = edog(client, IDX_REG, leg1=(0, 4), leg2=(1, 5), leg3=(2, 6),
             leg4=(3, 7), inipwm=inipwm, endpwm=endpwm)

# Espera la interacción del usuario con la interfaz, leyendo los eventos y los valores
# asociados con esos evento
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel':
        break

    match event:
        case 'Cancel':
            break
        case sg.WIN_CLOSED:
            break
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
                animation(robot, [xa, xa, xa, xa], [
                    ya, ya, ya, ya], gap, ti, r, values['et'])
                time.sleep(0.1)
                robot.set_position((0, 6.5), (1, 1, 1, 1))

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
            for i in range(1, 5):
                if event == f'gap_l{i}':
                    window[f'gl{i}'].update(
                        value=f'Gap Leg {i}: {values[f"gap_l{i}"]*100:.0f}%')
                if event == f'speed_l{i}':
                    window[f'sl{i}'].update(
                        value=f'Speed Leg {i}: {3.1-values[f"speed_l{i}"]:.1f}')

# Cierre de la ventana y del cliente Modbus
window.close()
client.close()
