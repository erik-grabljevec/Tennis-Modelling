import data_tools as dt

import numpy as np
import matplotlib.pyplot as plt



surface = ['any', 'clay', 'hard', 'carpet', 'grass']
values = []

for s in surface:
    data = dt.get_main_matches_data(s)
    wsp_data = np.append(np.array(data["WSP1"]), np.array(data["WSP2"]))
    predict_mean = np.average(wsp_data, axis=0)
    values.append(predict_mean)


N = 4
ind = np.arange(N)    # the x locations for the groups
width = 0.35       # the width of the bars: can also be len(x) sequence

plt.bar(ind, values[1:], width, color='r')
plt.ylabel('Probability of winning point on serve')
plt.xticks(ind+width/2., surface[1:])
plt.axhline(values[0], color='k', linestyle='dashed', linewidth=2)
plt.ylim([0, 1])

plt.show()