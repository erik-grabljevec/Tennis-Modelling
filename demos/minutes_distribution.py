"""
Create probability distribution for Wimbeldon 2015 finals.
"""

__author__ = 'riko'


import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

import calculations as calc


p = 0.666
q = 0.640

points = np.array(calc.monte_carlo_points_list(p, q, 5, 10000))
fnc = np.vectorize(lambda x: 0.6757 * x - 1.257)
data = fnc(points)

mu, std = norm.fit(data)

print "Avg: ", mu, "Std: ", std

# Plot the histogram.
plt.hist(data, normed=True, alpha=0.6, color='b')
xmin, xmax = plt.xlim()
x = np.linspace(xmin, xmax, 100)
p = norm.pdf(x, mu, std)

plt.plot(x, p, '--k', linewidth=2)

plt.axvline(mu, color='k', linestyle='solid', linewidth=2, label="Expected length in minutes")
plt.axvline(176, color='r', linestyle='solid', linewidth=2, label= "Actual length in minutes")
plt.legend(bbox_to_anchor=(1, 1),prop={'size':11}, loc=1, borderaxespad=0.)

plt.xlabel('Match length in minutes', fontsize=10)
plt.ylabel('Probability density', fontsize=10)

plt.show()