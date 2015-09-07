"""
Generate graph of Kei Nikishori performance.
"""

__author__ = 'riko'


import pickle

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

import settings as stg


file = stg.ROOT_PATH + "data/kei_data.p"
data = pickle.load(open(file, "rb"))[55:]
dates = [x[0] for x in data]
atp = [int(x[1]) for x in data]
rating = [x[2] for x in data]

fig, ax = plt.subplots()
plt.ylim(max(atp), min(atp) - 2)

myFmt = mdates.DateFormatter("%Y-%m")
ax.xaxis.set_major_formatter(myFmt)

plt.plot(dates, atp, "r", label="Atp rank")
plt.plot(dates, rating, "b", label="Base model rank")
plt.legend(bbox_to_anchor=(1, 1),prop={'size':11}, loc=4, borderaxespad=0.)

plt.ylabel('Rank', fontsize=10)
plt.xlabel('Date', fontsize=10)

plt.gcf().autofmt_xdate()
plt.show()

