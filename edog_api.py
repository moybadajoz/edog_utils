from scipy.interpolate import UnivariateSpline
import serial
import numpy as np
import time
import math as m


class edog():
    def __init__(self, client, IDX_REG, leg1: tuple[int, int], leg2: tuple[int, int], leg3: tuple[int, int], leg4: tuple[int, int], inipwm: list, endpwm: list):
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
        def __init__(self, hip: int, knee: int, inipwm: list[int, int], endpwm: list[int, int], position: list[float, float]):
            self.hip = self.servo(hip, inipwm[0], endpwm[0])
            self.knee = self.servo(knee, inipwm[1], endpwm[1])
            self.last_position = position

        class servo:
            def __init__(self, servo, inipwm, endpwm):
                self.servo = servo
                self.inipwm = inipwm
                self.endpwm = endpwm

            def _deg2pwm(self, ang: tuple[float, float]) -> tuple[int, int]:
                """
                Convierte un ángulo a un valor PWM para un motor específico.

                Args:
                    ang: El ángulo en grados.
                    motor: El número del motor (0, 1, 2, 3, 4, 5, 6 o 7).

                Returns:
                    El valor PWM para el motor especificado.
                """
                m = (self.endpwm-self.inipwm)/180
                return int(m*(ang+90)+self.inipwm)

        def _point2deg(self, point: tuple[float, float]) -> tuple[float, float]:
            """
            Convierte un punto 2D a sus valores de grados correspondientes.

            Args:
                point: Una tupla de dos números de punto flotante que representan el punto 2D.

            Returns:
                angHip: El valor del angulo de la cadera.
                angKnee: El valor del angulo de la rodilla.
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
            # angHip = angHip if abs(angHip) <= 90 else m.copysign(90, angHip)
            # angKnee = angKnee if abs(
            #     angKnee) <= 100 else m.copysign(100, angKnee)
            return angHip+11.5, angKnee+61.0

        def _point2pwm(self, point: tuple[float, float]) -> tuple[int, int]:
            '''
            convierte un punto (x, y) a pwm (hip, knee)

            Args: 
                point: (x, y)
                motors: (hip, knee)

            Returns:
                pwm: (hip pwm, knee pwm)
            '''
            ang = self._point2deg(point)
            return self.hip._deg2pwm(ang[0]), self.knee._deg2pwm(ang[1])

        def _get_servos(self):
            return self.hip.servo, self.knee.servo

    def write(self, points: list[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]]):
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
        self.client.write_multiple_registers(self.IDX_REG, sval) 
        self.leg1.last_position = points[0]
        self.leg2.last_position = points[1]
        self.leg3.last_position = points[2]
        self.leg4.last_position = points[3]

    def get_last_positions(self):
        return self.leg1.last_position, self.leg2.last_position, self.leg3.last_position, self.leg4.last_position

    def set_position(self, point: tuple[float, float], legs=(True, True, True, True)):
        '''
        Establece una posicion para todas las piernas dado un punto

        Args:
            point = punto (x, y) 
            legs = tupla que permite mover o no ciertas piernas
        '''
        points = [(point) if legs[i] else self.get_last_positions()[i]
                  for i in range(4)]
        self.write(points)

    def animation3(self, x, y, t, n, gap: list[float, float, float, float]):
        tt = np.linspace(0, t, len(x))
        xc = UnivariateSpline(tt, x)
        yc = UnivariateSpline(tt, y)

        xc.set_smoothing_factor(0.01)
        yc.set_smoothing_factor(0.01)

        iterations = 0
        tgap = [t*(g % 1) for g in gap]
        tini = time.time()
        tref = time.time() - tini
        while iterations < n:
            if (tref := time.time()-tini) >= t:
                iterations += 1
                tini = time.time()
                tref = time.time()-tini

            times = [(tref+g) % t for g in tgap]
            points = [(xc(i), yc(i)) for i in times]
            self.write(points)
            time.sleep(0.02)

    def animation_ind(self, x: list[list, list, list, list], y: list[list, list, list, list], gap: list[float, float, float, float], t: list[float, float, float, float], reverse: list[bool, bool, bool, bool], et):
        xf = [UnivariateSpline(np.linspace(0, t[i], len(x[i])), x[i])
              for i in range(4)]
        yf = [UnivariateSpline(np.linspace(0, t[i], len(y[i])), y[i])
              for i in range(4)]

        [f.set_smoothing_factor(0.01) for f in xf]
        [f.set_smoothing_factor(0.01) for f in yf]

        tgap = [tt*(g % 1) for tt, g in zip(t, gap)]
        tini = time.time()
        while (tref := time.time() - tini) < et:
            times = [(tref+g) % tt for tt, g in zip(t, tgap)]
            points = [(f_x(ti-tt if r else tt), f_y(ti-tt if r else tt))
                      for ti, tt, f_x, f_y, r in zip(t, times, xf, yf, reverse)]
            self.write(points)
            time.sleep(0.02)
