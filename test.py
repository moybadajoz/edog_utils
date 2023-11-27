import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import UnivariateSpline

dic = {'P1': (True, 6.8, 0.0), 'P2': (True, 6.85, -0.25), 'P3': (True, 6.9, -0.5), 'P4': (True, 6.95, -0.75), 'P5': (True, 7.0, -1.0), 'P6': (True, 7.05, -1.25), 'P7': (True, 7.1, -1.5), 'P8': (True, 7.15, -1.75), 'P9': (True, 7.2, -2.0), 'P10': (True, 6.4, -2.0),
       'P11': (True, 5.6, 1.75), 'P12': (True, 6.4, 2.0), 'P13': (True, 6.45, 1.75), 'P14': (True, 6.5, 1.5), 'P15': (True, 6.55, 1.25), 'P16': (True, 6.6, 1.0), 'P17': (True, 6.65, 0.75), 'P18': (True, 6.7, 0.5), 'P19': (True, 6.75, 0.25), 'P20': (True, 6.8, 0.0)}
x = [x for c, y, x in dic.values() if c]
y = [y for c, y, x in dic.values() if c]

xc = UnivariateSpline(np.linspace(0, 2, len(x)), x)
yc = UnivariateSpline(np.linspace(0, 2, len(y)), y)
xc.set_smoothing_factor(0.02)
yc.set_smoothing_factor(0.02)
print(x)
print(y)
plt.plot(x, y, 'o')
colors = ['Blue', 'Orange', 'Red', 'Green']
t1 = np.linspace(0.29, 0.84, 100)
plt.plot(xc(t1), yc(t1), color=colors[0])
t2 = np.linspace(0.84, 1.17, 100)
plt.plot(xc(t2), yc(t2), color=colors[1])
t3 = np.linspace(1.17, 1.72, 100)
plt.plot(xc(t3), yc(t3), color=colors[2])
t4 = np.linspace(1.72, 2.0, 100)
plt.plot(xc(t4), yc(t4), color=colors[3])
t4 = np.linspace(0.0, 0.29, 100)
plt.plot(xc(t4), yc(t4), color=colors[3])


plt.show()
