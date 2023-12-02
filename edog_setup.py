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

from pyModbusTCP.client import ModbusClient
import PySimpleGUI as sg
import serial
from pprint import pprint


def deg2pwm(ang, motor, inipwm, endpwm):
    """
    Convierte un ángulo a un valor PWM para un motor específico.

    Args:
        ang (float): El ángulo en grados.
        motor (int): El número del motor (0, 1, 2, 3, 4, 5, 6 o 7).
        inipwm (list): Lista de valores PWM iniciales para cada motor.
        endpwm (list): Lista de valores PWM finales para cada motor.

    Returns:
        int: El valor PWM para el motor especificado.
    """
    m = (endpwm[motor]-inipwm[motor])/180
    return int(m*(ang+90)+inipwm[motor])


# Crear instancia del cliente Modbus
SERVER_HOST = "192.168.4.1"  # ip del esp32
SERVER_PORT = 502   # port
IDX_REG = 0  # indice el registro
client = ModbusClient(host=SERVER_HOST, port=SERVER_PORT,
                      auto_open=True, debug=False)
client.timeout = 0.1

# Valores PWM iniciales y finales
endpwm = [105, 120, 600, 655, 612, 600, 110, 111]
inipwm = [606, 605, 120, 148, 106,  105, 642, 665]


# Configuración de la interfaz gráfica
sg.theme('DarkAmber')

layout = [[sg.Text('Set each servo for eDog')],
          [sg.Slider((-90, 90), 0, resolution=1)
           for _ in range(8)],  # Ángulos de servo
          [sg.Slider((50, 700), endpwm[i], resolution=1)
           for i in range(8)],  # Valores PWM finales
          [sg.Slider((50, 700), inipwm[i], resolution=1)
           for i in range(8)],  # Valores PWM iniciales
          [sg.Button('Ok'), sg.Button('Cancel')]]

window = sg.Window('eDog Servo Setup', layout)
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel':
        break
    print('You entered ', values)

    sval = [deg2pwm(values[motor], motor, values[16:], values[8:16:])
            for motor in range(8)]
    print(sval)

    client.write_multiple_registers(IDX_REG, sval)

window.close()
client.close()
