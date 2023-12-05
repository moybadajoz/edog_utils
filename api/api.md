# Documentación de la API de edog

## Requerimientos

- numpy
- pyModbusTCP

Instala las dependencias con: <br>
`pip install numpy pyModbusTCP`

## Clases

### 1. `edog`

Representa el robot cuadrúpedo.

#### Parámetros:

- `cliente`: Cliente de pyModbusTCP para la comunicación con el robot.
- `IDX_REG`: Índice de los registros de PWM.
- `leg1, leg2, leg3, leg4`: Tuplas que representan el número de servo de cada pierna (cadera, rodilla).
- `inipwm`: Lista de valores PWM que representan el límite a 90° de cada servo.
- `endpwm`: Lista de valores PWM que representan el límite a -90° de cada servo.

Nota: el orden de inipwm y endpwm será leg1[0], leg1[1], leg2[0], leg2[1], ..., leg4[1].

### 2. Clase `Leg`

Representa una pierna del robot. Una clase interna dentro de `edog`.

#### Parámetros:

- `hip`: Número de servo para la cadera.
- `knee`: Número de servo para la rodilla.
- `inipwm`: Lista de valores PWM que representan el límite a 90° de cada servo.
- `endpwm`: Lista de valores PWM que representan el límite a -90° de cada servo.

### 3. Clase `Servo`

Representa un servo individual. Una clase interna dentro de `Leg`.

#### Parámetros:

- `servo`: Número de servo.
- `inipwm`: Valor PWM a 90° del servo.
- `endpwm`: Valor PWM a -90° del servo.

## Métodos

### 1. `write`

Procesa y envía posiciones para las cuatro piernas.

#### Parámetros

- `points`: Lista de cuatro tuplas, cada una representando la posición x, y de una pierna.

### 2. `get_positions`

Devuelve la posición actual de las cuatro piernas.

#### Devuelve:

- Tupla de 4 elementos, cada uno representando las coordenadas (x, y) de la posición actual de cada una de las piernas.

### 3. `set_position`

Establece una posición para las piernas indicadas basándose en un punto dado.

#### Parámetros:

- `point`: Tupla que representa las coordenadas (x, y).
- `legs`: Tupla que permite mover o restringir ciertas piernas (por defecto es True para todas las piernas).

## Ejemplo

```
from api.edog_api import edog
from pyModbusTCP.client import ModbusClient


SERVER_HOST = "192.168.4.1"  # IP del ESP32
SERVER_PORT = 502   # Puerto
IDX_REG = 0  # Índice del registro

client = ModbusClient(host=SERVER_HOST, port=SERVER_PORT,
                      auto_open=True, debug=False)

endpwm = [105, 120, 600, 655, 612, 600, 110, 111]
inipwm = [606, 605, 120, 148, 106,  105, 642, 665]

robot = edog(client=client, IDX_REG=IDX_REG, leg1=(0, 4), leg2=(1, 5), leg3=(2, 6),
             leg4=(3, 7), inipwm=inipwm, endpwm=endpwm)

robot.set_position((-2, 6), (1, 1, 1, 1))

client.close()
```

---

Authors: <br>
Moises Badajoz Martinez <moisesbadajoz36@gmail.com><br>
Paola Lizbet Cabrera Oros <pl.cabreraoros@ugto.mx><br>

University of Guanajuato, 2023
