import numpy as np
import math as m
from pyModbusTCP.client import ModbusClient


class edog():
    """
    Clase que representa un robot cuadrúpedo (cuadrúpedo).

    Parámetros:
    - client: Cliente para comunicarse con el hardware del robot.
    - IDX_REG: Índice de registro para escribir los valores PWM.
    - leg1, leg2, leg3, leg4: Tuplas que representan la configuración de cada pierna.
    - inipwm: Lista de valores PWM iniciales para cada servo.
    - endpwm: Lista de valores PWM finales para cada servo.
    """

    def __init__(self, client: ModbusClient, IDX_REG: int, leg1: tuple[int, int], leg2: tuple[int, int], leg3: tuple[int, int], leg4: tuple[int, int], inipwm: list, endpwm: list):
        self.client = client
        self.IDX_REG = IDX_REG
        self.leg1 = self.leg(leg1[0], leg1[1], [inipwm[leg1[0]], inipwm[leg1[1]]],
                             [endpwm[leg1[0]], endpwm[leg1[1]]], (0, 7))
        self.leg2 = self.leg(leg2[0], leg2[1], [inipwm[leg2[0]], inipwm[leg2[1]]],
                             [endpwm[leg2[0]], endpwm[leg2[1]]], (0, 7))
        self.leg3 = self.leg(leg3[0], leg3[1], [inipwm[leg3[0]], inipwm[leg3[1]]],
                             [endpwm[leg3[0]], endpwm[leg3[1]]], (0, 7))
        self.leg4 = self.leg(leg4[0], leg4[1], [inipwm[leg4[0]], inipwm[leg4[1]]],
                             [endpwm[leg4[0]], endpwm[leg4[1]]], (0, 7))

    class leg:
        """
        Clase interna que representa una pierna del robot.

        Parámetros:
        - hip: Número de servo para la cadera.
        - knee: Número de servo para la rodilla.
        - inipwm: Lista de valores PWM iniciales para los servos.
        - endpwm: Lista de valores PWM finales para los servos.
        - position: Lista de coordenadas (x, y) para la última posición de la pierna.
        """

        def __init__(self, hip: int, knee: int, inipwm: list[int, int], endpwm: list[int, int], position: list[float, float]):
            self.hip = self.servo(hip, inipwm[0], endpwm[0])
            self.knee = self.servo(knee, inipwm[1], endpwm[1])
            self.last_position = position

        class servo:
            """
            Clase interna que representa un servo.

            Parámetros:
            - servo: Número de servo.
            - inipwm: Valor PWM inicial.
            - endpwm: Valor PWM final.
            """

            def __init__(self, servo, inipwm, endpwm):
                self.servo = servo
                self.inipwm = inipwm
                self.endpwm = endpwm

            def _deg2pwm(self, ang: tuple[float, float]) -> tuple[int, int]:
                """
                Convierte un ángulo a un valor PWM para un motor específico.

                Args:
                    ang: El ángulo en grados.

                Returns:
                    El valor PWM para el motor especificado.
                """
                m = (self.endpwm-self.inipwm)/180
                pwm = int(m*(ang+90)+self.inipwm)

                return 0 if pwm < 0 else pwm

        def _point2deg(self, point: tuple[float, float]) -> tuple[float, float]:
            """
            Convierte un punto 2D a sus valores de grados correspondientes.

            Args:
                point: Una tupla de dos números de punto flotante que representan el punto 2D.

            Returns:
                angHip: El valor del angulo de la cadera.
                angKnee: El valor del angulo de la rodilla.
            """
            """
            Notas:
                - Para calcular los angulos utiliza imaginando un un triangulo rectangulo
                  para calcular el angulo de desface, el cual aparece cuando x != 0
                - Tambien se imagina un triangulo escaleno (para este caso), de lados de 5cm y 3.6cm
                    y la hipotenusa del triangulo rectangulo anterior.
                - Se limita el tamaño maximo y minimo de la hipotenusa ya que pueden colapsar
                    las ecuaciones trigonometricas siguientes.
                    Las limitaciones corresponden a la suma de los lados conocidos (la longitud de la
                    tibia y el femur) para el maximo, y la resta de estos para el minimo.
                - Tambien se limita la relacion entre x/h, ya que arcsin() solo trabaja (para este caso)
                    entre -1.0 < x < 1.0
                - Para el calculo de los angulos se utiliza la formula:
                    arccos((a^2+b^2-b^2)/(2*a*b))
                    siendo a y b los lados adyacentes al angulo
                    y c el lado opuesto
                - Al angulo de la cadera se le agrega el angulo de desface mientras que al angulo
                    de la rodilla se le resta pi, ya que, mientras que en triangulo un angulo de 0 gradros
                    se formaria cuando el femur y la tibia estan superpuestos, en el robot este se logra
                    al estirar completamente la pierna.
                - Al final se agregan un pequeño offset a los agulos para alinearlos correctamente.
            """
            y = point[1]
            x = -point[0]
            h = (x**2+y**2)**0.5
            h = h if h <= 8.6 else 8.6
            h = h if h >= 1.4 else 1.4
            p = x/h if abs(x/h) <= 1.0 else m.copysign(1.0, x)
            a_p = np.arcsin(p)
            a_a = np.arccos(((h**2)+25-12.96)/(10*h))
            a_b = np.arccos((25+12.96-(h**2))/(2*5*3.6))
            angHip = (a_p+a_a)*(180/np.pi)
            angKnee = (-np.pi+a_b)*(180/np.pi)
            return angHip+11.5, angKnee+61.0

        def _point2pwm(self, point: tuple[float, float]) -> tuple[int, int]:
            """
            Convierte un punto (x, y) a valores PWM (hip, knee).

            Args:
                point: (x, y)

            Returns:
                pwm: (hip pwm, knee pwm)
            """
            ang = self._point2deg(point)
            return int(self.hip._deg2pwm(ang[0])), int(self.knee._deg2pwm(ang[1]))

        def _get_servos(self) -> tuple[int, int]:
            """
            Devuelve los servos de una pierna

            Returns:
                servos: (servo cadera, servo rodilla)
            """
            return self.hip.servo, self.knee.servo

    def write(self, points: list[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]]) -> None:
        '''
        Procesa y envia las posiciones para las 4 piernas

        Args:
            points: lista de 4 tuplas [leg1, leg2, leg3, leg4]
                    cada tupla consta de (x, y)
        '''
        sval = np.zeros(8)
        sval[self.leg1._get_servos()[0]], sval[self.leg1._get_servos()[1]
                                               ] = self.leg1._point2pwm(points[0])
        sval[self.leg2._get_servos()[0]], sval[self.leg2._get_servos()[1]
                                               ] = self.leg2._point2pwm(points[1])
        sval[self.leg3._get_servos()[0]], sval[self.leg3._get_servos()[1]
                                               ] = self.leg3._point2pwm(points[2])
        sval[self.leg4._get_servos()[0]], sval[self.leg4._get_servos()[1]
                                               ] = self.leg4._point2pwm(points[3])
        sval = [int(n) for n in sval]
        self.client.write_multiple_registers(self.IDX_REG, sval)
        self.leg1.last_position = points[0]
        self.leg2.last_position = points[1]
        self.leg3.last_position = points[2]
        self.leg4.last_position = points[3]

    def get_positions(self) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]]:
        '''
        Retorna la posicion actual de las cuatro piernas del robot.

        Devuelve una tupla de cuatro elementos, donde cada elemento representa la posición (punto) de una pierna específica.

        Estructura de la tupla devuelta:
        - Primer elemento: Coordenadas (x, y) de la posición de la pierna 1.
        - Segundo elemento: Coordenadas (x, y) de la posición de la pierna 2.
        - Tercer elemento: Coordenadas (x, y) de la posición de la pierna 3.
        - Cuarto elemento: Coordenadas (x, y) de la posición de la pierna 4.
        '''
        return self.leg1.last_position, self.leg2.last_position, self.leg3.last_position, self.leg4.last_position

    def set_position(self, point: tuple[float, float], legs=(True, True, True, True)) -> None:
        '''
        Establece una posicion para todas las piernas dado un punto

        Args:
            point = punto (x, y) 
            legs = tupla que permite mover o no ciertas piernas
        '''
        points = [(point) if legs[i] else self.get_last_positions()[i]
                  for i in range(4)]
        self.write(points)
