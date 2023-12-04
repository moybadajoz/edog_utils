# edog_utils

Utilidades para el control de un robot cuadrupedo por wifi

Aqui solo se documenta las utilidades y ejemplos.<br>
Documentacion de la api: [api.md](api/api.md)

## Requisitos

- `edog_setup.py`:

        - PySimpleGui
        - pyModbusTCP

- `edog_test.py`:<br>

        - PySimpleGui
        - numpy
        - scypy

- `edog_control.py`:<br>

        - PySimpleGui
        - numpy
        - scypy

- `edog_leg_trayectory.py`: <br>

        - PySimpleGui
        - numpy
        - matplotlib
        - scypy

## Ejemplos

### [edog_control.py](examples/edog_control.py)

Este script permite controlar el caminar del robot.
Cuenta con dos sliders, en uno se selecciona la velocidad y el otro la cantidad de giro,
luego se presiona la direccion y mientras este presionado el boton, el robot caminara

### [edog_test.py](examples/edog_tests.py)

En este script se puede probar las posiciones de las piernas, se pueden las piernas de manera
individual o en grupo, se puede seleccionar la altura del robot y el desplazamiento hacia adelante y hacia atras.<br>
Ademas permite probar animaciones hechas por la utilidad [edog_leg_trayectory.py](others_utils\edog_leg_trayectory.py)<br>
se puede ajustar el tiempo de ejecucion de la animacion el desface y velocidad de ejecucion por pierna y si la animacion ira
en reversa.

### [edog_setup.py](examples/edog_setup.py)

Permite ajustar el `inipwm` y el `endpwm` de los servos para que todas las piernas se muevan igual.

### [edog_leg_trayectory.py](others_utils\edog_leg_trayectory.py)

Permite visualizar como se comportara (ver la trayectoria) la animacion de una pierna, el minimo de puntos son 7, el maximo 20,
la animacion siempre empezara en el punto activado con numeracion mas baja y terminara en el punto activado con numeracion mas alta,
la trayectoria que se muestra es la que intentara seguir el script ya que utiliza el mismo tipo de suavisado.

Al oprimir el boton `print` se mostrara en consola los puntos en formato de implementacion<br>

```
x = [x1, x2, x3, ..., xn]
y = [y1, y2, y3, ..., yn]
```

y en formato de diccionario

```
{'P1': (True, 6.0, -2.0), 'P2': (True, 6.0, -2.4), 'P3': (True, 6.0, -2.8), 'P4': (True, 6.0, -3.2), 'P5': (True, 6.0, -3.6), 'P6': (True, 6.0, -4.0), 'P7': (False, 6.0, 0.0), 'P8': (True, 5.75, -3.2), 'P9': (True, 5.7, -0.8), 'P10': (False, 6.85, 0.0), 'P11': (False, 6.9, 0.0), 'P12': (False, 7.0, 0.0), 'P13': (False, 7.0, 0.0), 'P14': (False, 7.0, 0.0), 'P15': (True, 6.0, 0.0), 'P16': (True, 6.0, -0.4), 'P17': (True, 6.0, -0.8), 'P18': (True, 6.0, -1.2), 'P19': (True, 6.0, -1.6), 'P20': (True, 6.0, -2.0)}

```

este ultimo permite volver a cargalo posteriormente de nuevo en el programa para continuar en otro momento con la realizacion
de la animacion, ademas de poder cargarlo en [edog_test.py](examples/edog_tests.py).
