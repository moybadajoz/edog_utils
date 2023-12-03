# Documentacion edog api

## Requerimientos

- numpy
- pyModbusTCP

Instala las dependencias con: <br>
`pip install numpy pyModBusTCP`

## Clases

### 1. `edog`

Representa el robot cuadrupedo.

#### Parametros:

- `cliente`: Cliente de pyModbusTPC para la comunicación con el robot.
- `IDX_REG`: Indice de los registros de PWM.
- `leg1, leg2, leg3, leg4`: Tuplas que representan el numero de servo de cada pierna (cadera, rodilla).
- `inipwm`: Lista de valores PWM que representan el limite a -90° de cada servo.
- `endpwm`: Lista de valores PWM que representan el limite a 90° de cada servo.

nota: el orden de inipwm y endpwm sera leg1[0], leg1[1], leg2[0], leg2[1], ..., leg4[1].

### 2. Clase `Leg`

Representa una pierna del robot. Una clase interna dentro de `edog`.

#### Parametros:

- `hip`: Número de servo para la cadera.
- `knee`: Número de servo para la rodilla.
- `inipwm`: Lista de valores PWM que representan el limite a -90° de cada servo.
- `endpwm`: Lista de valores PWM que representan el limite a 90° de cada servo.

### 3. Clase `servo`

Representa un servo individual. Una clase interna dentro de `leg`.

#### Parametros:

- `servo`: Número de servo.
- `inipwm`: Valor PWM a -90° del servo.
- `endpwm`: Valor PWM a 90° del servo.

## Métodos

### 1. `write`

Procesa y envia posiciones para las cuatro piernas.

#### Parametros

- `points`: Lista de cuatro tuplas, cada una representando la posicion x, y de una pierna.

### 2. `get_positions`

Devuelve la posicion actual de las cuatro piernas.

#### Devuelve:

- Tupla de 4 elementos, cada uno representando las coordnadas (x, y) de la posicion actual de cada una de las piernas.

### 3. `set_position`

Establece una posicion para las piernas indicadas basandose en un punto dado.

#### Parametros:

- `point`: Tupla que representa las coordenadas (x, y).
- `legs`: Tupla que permite mover o restringir ciertas piernas (por defecto es True para todas las piernas).
