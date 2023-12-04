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
