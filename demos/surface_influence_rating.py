import data_tools as dt

import numpy as np
import matplotlib.pyplot as plt

import models


glicko = models.DoubleModifiedGlickoModel()

surface = ['any', 'clay', 'hard', 'carpet', 'grass']
values = []

for s in surface:
    data = dt.get_main_matches_data(s)
    data = glicko.test(data)
    values.append(np.average(data["ret"]))


N = 4
ind = np.arange(N)    # the x locations for the groups
width = 0.35       # the width of the bars: can also be len(x) sequence

plt.bar(ind, values[1:], width, color='r')
plt.ylabel('Average return rating of a winner')
plt.xticks(ind+width/2., surface[1:])
plt.axhline(values[0], color='k', linestyle='dashed', linewidth=2)
plt.ylim([1400, 1600])

plt.show()
