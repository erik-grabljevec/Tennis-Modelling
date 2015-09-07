"""
Scatter plot of correlation of number of serves and length of match.
"""

__author__ = 'riko'


import matplotlib.pyplot as plt
import numpy as np

import data_tools as dt


data = dt.get_main_matches_data()

mask = (data["Serves"] != 0) & (data["Minutes"] != 0)
y = np.array(data["Minutes"][mask])
x = np.array(data["Serves"][mask])

N = np.size(x)

fig = plt.figure()
fit = np.polyfit(x,y,1)
fit_fn = np.poly1d(fit)
print fit_fn
plt.plot(x,y, 'bo', x, fit_fn(x), '--k')
plt.xlim([0, 400])
plt.ylim([0, 400])

plt.xlabel('Points played', fontsize=10)
plt.ylabel('Minutes played', fontsize=10)

plt.show()


