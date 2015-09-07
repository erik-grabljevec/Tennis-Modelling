__author__ = 'riko'

import calculations as calc
import numpy as np


A = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
A = calc.smooth_time_series(A, 0.5)

print A