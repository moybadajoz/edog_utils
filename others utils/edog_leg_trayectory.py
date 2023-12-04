import PySimpleGUI as sg
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.interpolate import UnivariateSpline


# Funcion para graficar los puntos en X y Y y trazar trayectoras
def graph(x, y):
    """
    Grafica puntos y curvas suavizadas a partir de las coordenadas proporcionadas.

    Args:
        x (list): Lista de coordenadas x.
        y (list): Lista de coordenadas y.
    """
    # Limpiar el área de la gráfica
    axes.cla()
    # Graficar puntos
    axes.plot(x, -np.array(y), 'o')

    # Si hay más de 6 puntos, realizar suavizado y graficar curvas
    if len(x) > 6:
        tt = np.linspace(0, 40, len(x))
        xc = UnivariateSpline(tt, x)
        yc = UnivariateSpline(tt, y)
        xc.set_smoothing_factor(0.02)
        yc.set_smoothing_factor(0.02)

        # Graficar curvas suavizadas
        for i in range(3):
            tt = np.linspace(5+(10*i), 5+(10*(i+1)), 200)
            axes.plot(xc(tt), -yc(tt))
        tt = np.linspace(35, 40, 100)
        axes.plot(xc(tt), -yc(tt), color='Blue')
        tt = np.linspace(0, 5, 100)
        axes.plot(xc(tt), -yc(tt), color='Blue')

    # Configurar límites y cuadrícula
    axes.set_xlim(min(x)-1, max(x)+1)
    axes.set_ylim(-max(y)-1, -min(y)+1)
    axes.grid(True)
    # Actualizar la visualización de la gráfica
    figure_canvas_agg.draw()


# Configuración del tema de PySimpleGUI
sg.theme('DarkAmber')
# Diseño de la interfaz gráfica
layout_l = [[sg.Canvas(key='canvas', size=(400, 400))]]
layout_r = [[sg.Checkbox(text=f'P{i+1}', key=f'P{i+1}', default=True if i < 7 else False, enable_events=True),
             sg.Slider(range=(3, 10), default_value=7, resolution=0.05,
                       key=f'P{i+1}Y', orientation='h', enable_events=True),
             sg.Slider(range=(-10, 10), default_value=0, resolution=0.05,
                       key=f'P{i+1}X', orientation='h', enable_events=True)
             ]
            for i in range(0, 20)]

layout_col = [[sg.Column(layout=layout_r, p=0, scrollable=True, vertical_scroll_only=True, size=(440, 450))],
              [sg.Button('Load', pad=((10, 10), (10, 0))), sg.Input(key='In', size=(55, 20), pad=((0, 0), (10, 0)))]]

# Creación de la ventana
window = sg.Window(title='Frecuencia',
                   layout=[[sg.Frame(layout=layout_l, p=0, title='Graph', size=(550, 510)),
                            sg.Frame(layout=layout_col, title='Points', size=(460, 510))],
                           [sg.Button(button_text='Print', key='Print'),
                            sg.Button(button_text='Cancel', key='Cancel')]
                           ],
                   finalize=True)

# Obtención del objeto de la gráfica
canvas = window['canvas'].TKCanvas
figure = Figure()
axes = figure.add_subplot()
figure.subplots_adjust(top=0.95, right=0.95, bottom=0.07, left=0.1)
figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
figure_canvas_agg.draw()
figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)

# Graficar puntos iniciales
graph([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [
      7.1, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0])

# Bucle principal del programa
while True:
    event, values = window.read()

    # Salir si se cierra la ventana
    if event == sg.WIN_CLOSED or event == 'Cancel':
        break

    # Imprimir las coordenadas de los puntos seleccionados
    elif event == 'Print':
        checks = [values[f'P{i+1}'] for i in range(20)]
        x = [values[f'P{i+1}X'] for i in range(20) if checks[i]]
        y = [values[f'P{i+1}Y'] for i in range(20) if checks[i]]
        print(f'x = {x}')
        print(f'y = {y}')

        # imprimir en formato de diccionario para guardar el estado
        x = [values[f'P{i+1}X'] for i in range(20)]
        y = [values[f'P{i+1}Y'] for i in range(20)]

        dic = {f'P{i+1}': v for i, v in enumerate(zip(checks, y, x))}
        print(dic, '\n')

    # Cargar puntos desde la entrada de texto
    elif event == 'Load':
        try:
            dic = eval(values['In'])
            for k, v in dic.items():
                window[f'{k}'].update(v[0])
                window[f'{k}Y'].update(v[1])
                window[f'{k}X'].update(v[2])
            x = [x for c, _, x in dic.values() if c]
            y = [y for c, y, _ in dic.values() if c]
            graph(x, y)
            window['In'].update('')
        except:
            pass
    # Actualizar la gráfica cuando se modifican los controles
    elif event:
        checks = [values[f'P{i+1}'] for i in range(20)]
        if checks.count(True) < 7:
            window[event].update(True)
        checks = [values[f'P{i+1}'] for i in range(20)]
        x = [values[f'P{i+1}X'] for i in range(20) if checks[i]]
        y = [values[f'P{i+1}Y'] for i in range(20) if checks[i]]
        graph(x, y)

# Cerrar la ventana al finalizar
window.close()

# {'P1': (True, 6.8, 0.0), 'P2': (True, 6.9, -0.5), 'P3': (True, 7.0, -1.0), 'P4': (True, 7.1, -1.5), 'P5': (True, 7.2, -2.0), 'P6': (True, 6.2, -1.6), 'P7': (False, 7.0, 0.0), 'P8': (False, 7.0, 0.0), 'P9': (False, 7.0, 0.0), 'P10': (False, 7.0, 0.0), 'P11': (False, 7.0, 0.0), 'P12': (False, 7.0, 0.0), 'P13': (False, 7.0, 0.0), 'P14': (False, 7.0, 0.0), 'P15': (True, 5.5, 1.6), 'P16': (True, 6.4, 2.0), 'P17': (True, 6.5, 1.5), 'P18': (True, 6.6, 1.0), 'P19': (True, 6.7, 0.5), 'P20': (True, 6.8, 0.0)}
# {'P1': (True, 6.8, 0.0), 'P2': (True, 6.85, -0.25), 'P3': (True, 6.9, -0.5), 'P4': (True, 6.95, -0.75), 'P5': (True, 7.0, -1.0), 'P6': (True, 7.05, -1.25), 'P7': (True, 7.1, -1.5), 'P8': (True, 7.15, -1.75), 'P9': (True, 7.2, -2.0), 'P10': (True, 6.4, -2.0), 'P11': (True, 5.6, 1.75), 'P12': (True, 6.4, 2.0), 'P13': (True, 6.45, 1.75), 'P14': (True, 6.5, 1.5), 'P15': (True, 6.55, 1.25), 'P16': (True, 6.6, 1.0), 'P17': (True, 6.65, 0.75), 'P18': (True, 6.7, 0.5), 'P19': (True, 6.75, 0.25), 'P20': (True, 6.8, 0.0)}
# {'P1': (True, 6.8, 0.0), 'P2': (True, 6.9, -0.5), 'P3': (True, 7.0, -1.0), 'P4': (True, 7.1, -1.5), 'P5': (True, 7.2, -2.0), 'P6': (True, 5.9, -0.4), 'P7': (False, 5.5, 0.25), 'P8': (False, 5.65, 0.0), 'P9': (False, 7.0, 0.0), 'P10': (False, 7.0, 0.0), 'P11': (False, 7.0, 0.0), 'P12': (False, 7.0, 0.0), 'P13': (False, 7.0, 0.0), 'P14': (False, 7.0, 0.0), 'P15': (False, 5.5, 1.6), 'P16': (True, 6.4, 2.0), 'P17': (True, 6.5, 1.5), 'P18': (True, 6.6, 1.0), 'P19': (True, 6.7, 0.5), 'P20': (True, 6.8, 0.0)}
# walk(? {'P1': (True, 6.0, -2.0), 'P2': (True, 6.0, -2.4), 'P3': (True, 6.0, -2.8), 'P4': (True, 6.0, -3.2), 'P5': (True, 6.0, -3.6), 'P6': (True, 6.0, -4.0), 'P7': (False, 6.0, 0.0), 'P8': (True, 5.75, -3.2), 'P9': (True, 5.7, -0.8), 'P10': (False, 6.85, 0.0), 'P11': (False, 6.9, 0.0), 'P12': (False, 7.0, 0.0), 'P13': (False, 7.0, 0.0), 'P14': (False, 7.0, 0.0), 'P15': (True, 6.0, 0.0), 'P16': (True, 6.0, -0.4), 'P17': (True, 6.0, -0.8), 'P18': (True, 6.0, -1.2), 'P19': (True, 6.0, -1.6), 'P20': (True, 6.0, -2.0)}
