'''
authors:    Moises Badajoz Martinez <moisesbadajoz36@gmail.com>
            Paola Lizbet Cabrera Oros <pl.cabreraoros@ugto.mx>

University of Guanajuato, 2023
'''
from api.edog_api import edog
import time
import numpy as np
import threading
import queue
# libreria para crear la interfaz grafica para controlar el robot
import PySimpleGUI as sg
from scipy.interpolate import UnivariateSpline
from pyModbusTCP.client import ModbusClient


# funcion para crear el movimeinto del robot en velocidad u direccion
def walk_thread(robot, speed_in, steer_in, new, close):
    """
    Función principal del hilo de caminar del robot.
    Recibe comandos de velocidad y dirección, y controla el movimiento del robot en función de estos comandos.

    Args:
        robot: Instancia de la clase Edog que representa el robot.
        speed_in: Cola de entrada para la velocidad.
        steer_in: Cola de entrada para la dirección.
        new: Evento que indica que hay nuevos comandos disponibles.
        close: Evento que indica que el hilo debe cerrarse.
    """
    # Coordenadas x e y para la trayectoria de caminar
    x = np.array([-2.0, -2.4, -2.8, -3.2, -3.6, -4.0, -
                  3.2, -0.8, 0.0, -0.4, -0.8, -1.2, -1.6, -2.0])
    y = np.array([6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 5.75,
                  5.7, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0])
    # Esperar hasta que se indique que hay nuevos comandos o que el hilo debe cerrarse
    while (not new.is_set()) and (not close.is_set()):
        time.sleep(0.1)
    # Bucle principal del hilo
    while not close.is_set():
        # Limpiar el evento 'new' para esperar nuevos comandos
        new.clear()
        # Obtener comandos de velocidad y dirección de las colas
        # lee hasta obtener el ultimo enviado
        while not speed_in.empty():
            speed = speed_in.get()
        while not steer_in.empty():
            steer = steer_in.get()

        # Verificar si el robot debe detenerse
        stop = False if speed else True
        if stop:
            # Esperar hasta que se indique que hay nuevos comandos o que el hilo debe cerrarse
            while (not new.is_set()) and (not close.is_set()):
                time.sleep(0.1)
            continue
        # Ajustar la velocidad y la dirección según la dirección de movimiento
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
        # Crear funciones de interpolación para las coordenadas x e y
        xf = [UnivariateSpline(np.linspace(0, speed, x.shape[0]), xi)
              for xi in [x*right, x*right, x*left, x*left]]
        [f.set_smoothing_factor(0.01) for f in xf]
        yf = [UnivariateSpline(np.linspace(0, speed, y.shape[0]), y)
              for _ in range(4)]
        [f.set_smoothing_factor(0.01) for f in yf]
        # Configurar la brecha entre las patas según la dirección de movimiento
        gap = [0.5, 0.25, 0.75, 0.0] if reverse else [0.5, 0.75, 0.25, 0.0]
        time_gap = [speed*g for g in gap]

        # Tomar el tiempo inicial
        time_ini = time.time()
        # Bucle para calcular las posiciones de las patas y actualizar el robot
        while (not new.is_set()) and (not close.is_set()):
            # Calcular el tiempo de referencia y los tiempos para cada pata
            time_ref = time.time() - time_ini
            times = [((time_ref+g) % speed) if not reverse else speed -
                     ((time_ref+g) % speed) for g in time_gap]
            # Calcular las posiciones de las patas en función del tiempo
            points = [(fx(t), fy(t)) for fx, fy, t in zip(xf, yf, times)]
            # Actualizar la posición del robot
            robot.write(points)
            # Esperar antes de la próxima iteración
            time.sleep(0.02)


# Crear una instancia del robot eDog
SERVER_HOST = "192.168.4.1"  # IP del ESP32
SERVER_PORT = 502   # Puerto
IDX_REG = 0  # Índice del registro

client = ModbusClient(host=SERVER_HOST, port=SERVER_PORT,
                      auto_open=True, debug=False)
client.timeout = 0.1
sg.theme('DarkGrey9')

layout_1 = [[sg.Text('Speed: 0.1', p=(60, 0), k='speedtxt')],
            [sg.Slider(range=(0.1, 2.5), default_value=0,
                       resolution=0.1, k='speed', enable_events=True,
                       p=(85, 5), disable_number_display=True)],
            [sg.Text("Steer: 0.0", p=(60, (10, 0)), k='steertxt')],
            [sg.Slider(range=(-0.5, 0.5), default_value=0,
                       resolution=0.1, k='steer', enable_events=True,
                       orientation='h',  disable_number_display=True)],
            [sg.RealtimeButton(sg.SYMBOL_UP, k='forward',
                               size=(10, 2), p=(52, 5))],
            [sg.RealtimeButton(sg.SYMBOL_DOWN, k='backward', size=(10, 2), p=(52, 5))]]

layout = [[sg.Frame(layout=layout_1, title='Control', size=(193, 370))]]

window = sg.Window('eDog Servo Control', layout)

endpwm = [105, 120, 600, 655, 612, 600, 110, 111]
inipwm = [606, 605, 120, 148, 106,  105, 642, 665]

robot = edog(client=client, IDX_REG=IDX_REG, leg1=(0, 4), leg2=(1, 5), leg3=(2, 6),
             leg4=(3, 7), inipwm=inipwm, endpwm=endpwm)

speed_in = queue.Queue(-1)
steer_in = queue.Queue(-1)

new = threading.Event()
close = threading.Event()

# Iniciar hilo de caminar
thread = threading.Thread(target=walk_thread, args=(
    robot, speed_in, steer_in, new, close))
thread.start()

# Bucle principal
update = True
while True:
    event, values = window.read(timeout=100)
    match event:
        case sg.WIN_CLOSED:
            # Cerrar la aplicación y detener el hilo de caminar
            close.set()
            time.sleep(0.1)
            robot.set_position((-2, 6), (1, 1, 1, 1))
            time.sleep(0.1)
            client.close()
            break
        case 'forward':
            # Enviar comandos de avance al robot
            if update:
                speed_in.put(values['speed'])
                steer_in.put(values['steer'])
                new.set()
                update = False

        case 'backward':
            # Enviar comandos de retroceso al robot
            if update:
                speed_in.put(-values['speed'])
                steer_in.put(values['steer'])
                new.set()
                update = False
        case sg.TIMEOUT_EVENT:
            # Detener el robot cuando no hay comandos
            speed_in.put(0.0)
            steer_in.put(0.0)
            new.set()
            robot.set_position((-2, 6), (1, 1, 1, 1))
            update = True
        case _:
            # Actualizar la interfaz gráfica y los valores de velocidad y dirección
            if event in {'speed', 'steer'}:
                window['speedtxt'].update(f'Speed: {values["speed"]:.1f}')
                window['steertxt'].update(f'Steer: {values["steer"]:.1f}')
                update = True
