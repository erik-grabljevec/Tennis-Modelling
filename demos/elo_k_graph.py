"""
Generate graph of Double Elo model's error for given K.
"""

__author__ = 'riko'


import matplotlib.pyplot as plt
import numpy as np

import data_tools as dt
import models


elo = models.DoubleEloModel()

train_data = dt.get_main_matches_data()

x = np.array([1.0 * i / 4 for i in range(4, 120)])
y = np.array([elo._train_params([p], train_data, verbose=True) for p in x])
fig = plt.figure()

plt.plot(x, y, '-r')

fig.suptitle('', fontsize=20)
plt.ylabel('Improved model error', fontsize=10)
plt.xlabel('K', fontsize=10)

plt.show()