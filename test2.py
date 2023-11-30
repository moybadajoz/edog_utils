import numpy as np
import time
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

x = np.array([-2.0, -2.4, -2.8, -3.2, -3.6, -4.0,
              -3.2, -0.8, 0.0, -0.4, -0.8, -1.2, -1.6, -2.0])
y = -np.array([6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 5.75,
               5.7, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0])

t1 = 2
t2 = 1.5

yf = UnivariateSpline(np.linspace(0, t1, len(y)), y)
yf.set_smoothing_factor(0.01)
xf = UnivariateSpline(np.linspace(0, t1, len(x)), x)
xf.set_smoothing_factor(0.01)

yft = UnivariateSpline(np.linspace(0, t2, len(y)), y)
yft.set_smoothing_factor(0.01)
xft = UnivariateSpline(np.linspace(0, t2, len(x)), x)
xft.set_smoothing_factor(0.01)


def animate(i):
    xg = xf(np.linspace(0, t1, 120))
    yg = yf(np.linspace(0, t1, 120))

    plt.cla()
    plt.plot(x, y, 'o', color='Blue')
    plt.plot(xf(t[i] % t1), yf(t[i] % t1), 'o', color='Red')
    plt.plot(xft(t[i] % t2), yft(t[i] % t2), 'o', color='Red')
    plt.plot(xg, yg, color='Blue')


fig, ax = plt.subplots()

xg = xf(np.linspace(0, t1, 120))
yg = yf(np.linspace(0, t1, 120))
t = 23.231
dt = t2*(t/t1)-t
# plt.plot(x, y, 'o', color='Blue')
plt.plot(xg, yg, color='Blue')
plt.plot(xf(t % t1), yf(t % t1), 'o', color='Red')
plt.plot(xft((t+dt) % t2), yft((t+dt) % t2), 'o', color='Orange')
# anim = FuncAnimation(fig, animate, frames=120, interval=20)
plt.show()
