# edog_utils

Utilidades para el control de un robot cuadrúpedo por wifi.

Aquí solo se documentan las utilidades y ejemplos.<br>
Documentación de la API: [api.md](api/api.md)

## Requisitos

- `edog_setup.py`:

        - PySimpleGui
        - pyModbusTCP

- `edog_test.py`:<br>

        - PySimpleGui
        - numpy
        - scipy

- `edog_control.py`:<br>

        - PySimpleGui
        - numpy
        - scipy

- `edog_leg_trajectory.py`: <br>

        - PySimpleGui
        - numpy
        - matplotlib
        - scipy

## Ejemplos

### [edog_control.py](examples/edog_control.py)

Este script permite controlar el caminar del robot.
Cuenta con dos sliders, en uno se selecciona la velocidad y el otro la cantidad de giro.
Luego se presiona la dirección y mientras esté presionado el botón, el robot caminará.

### [edog_test.py](examples/edog_tests.py)

En este script se pueden probar las posiciones de las piernas, se pueden mover las piernas de manera
individual o en grupo. Se puede seleccionar la altura del robot y el desplazamiento hacia adelante y hacia atrás.<br>
Además, permite probar animaciones hechas por la utilidad [edog_leg_trajectory.py](others_utils\edog_leg_trajectory.py).<br>
Se puede ajustar el tiempo de ejecución de la animación, el desfase y velocidad de ejecución por pierna y si la animación irá
en reversa.

### [edog_setup.py](examples/edog_setup.py)

Permite ajustar el `inipwm` y el `endpwm` de los servos para que todas las piernas se muevan igual.

### [edog_leg_trajectory.py](others_utils\edog_leg_trajectory.py)

Permite visualizar cómo se comportará (ver la trayectoria) la animación de una pierna. El mínimo de puntos son 7, el máximo 20.
La animación siempre empezará en el punto activado con numeración más baja y terminará en el punto activado con numeración más alta.
La trayectoria que se muestra es la que intentará seguir el script ya que utiliza el mismo tipo de suavizado.

Al oprimir el botón `print`, se mostrará en consola los puntos en formato de implementación:<br>

```
x = [x1, x2, x3, ..., xn]
y = [y1, y2, y3, ..., yn]
```

y en formato de diccionario:<br>

```
{'P1': (True, 6.0, -2.0), 'P2': (True, 6.0, -2.4), 'P3': (True, 6.0, -2.8), 'P4': (True, 6.0, -3.2), 'P5': (True, 6.0, -3.6), 'P6': (True, 6.0, -4.0), 'P7': (False, 6.0, 0.0), 'P8': (True, 5.75, -3.2), 'P9': (True, 5.7, -0.8), 'P10': (False, 6.85, 0.0), 'P11': (False, 6.9, 0.0), 'P12': (False, 7.0, 0.0), 'P13': (False, 7.0, 0.0), 'P14': (False, 7.0, 0.0), 'P15': (True, 6.0, 0.0), 'P16': (True, 6.0, -0.4), 'P17': (True, 6.0, -0.8), 'P18': (True, 6.0, -1.2), 'P19': (True, 6.0, -1.6), 'P20': (True, 6.0, -2.0)}

```

Este último permite volver a cargarlo posteriormente en el programa para continuar en otro momento con la realización
de la animación, además de poder cargarlo en [edog_test.py](examples/edog_tests.py).
