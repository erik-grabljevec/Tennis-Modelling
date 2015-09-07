__author__ = 'riko'


import matplotlib.pyplot as plt
import data_tools as dt
import models

import numpy as np
import scipy as sp
import scipy.stats


glicko = models.DoubleModifiedGlickoModel()
data = dt.get_main_matches_data()

df = glicko.test(data)

y = np.append(np.array(df["WSP1"]), np.array(df["WSP2"]))
x = np.append(np.array(df["p"]), np.array(df["q"]))

x_avg = np.average(x)
y_avg = np.average(y)

predict_mean = np.average(x - y, axis=0)
predict_var = np.std(x - y, axis=0)
h = predict_var * sp.stats.t.ppf((1+0.95)/2., np.size(x) - 1)
predict_conf95 = (predict_mean - h, predict_mean + h)

print "Average: ", predict_mean
print "Var: ", predict_var
print "Conf95: ", predict_conf95


fig = plt.figure()
fit = np.polyfit(x,y,1)
fit_fn = np.poly1d(fit)
plt.plot(x, y, 'bo')

plt.xlim([0, 1])
plt.ylim([0, 1])

plt.xlabel('Expected probability', fontsize=10)
plt.ylabel('Actual probability', fontsize=10)

plt.axvline(x_avg, color='k', linestyle='dashed', linewidth=2)
plt.axhline(y_avg, color='k', linestyle='dashed', linewidth=2)

plt.show()

