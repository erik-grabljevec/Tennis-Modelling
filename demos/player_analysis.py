"""
Analyse player's performance on different surfaces.
"""

__author__ = 'riko'


import math

import numpy as np

from scipy.stats import norm
import matplotlib.pyplot as plt

import data_tools as dt
import models

NAME = "Andy Murray"


glicko = models.DoubleModifiedGlickoModel()

match = {}
wins = {}
ser = {}
ret = {}
count = {}
grass = []
n = 0

data = dt.get_main_matches_data()

for i, row in data.iterrows():
    if row["Winner"] == NAME:
        match[row["Surface"]] = match.get(row["Surface"], 0) + 1
        wins[row["Surface"]] = wins.get(row["Surface"], 0) + 1
        ser[row["Surface"]] = ser.get(row["Surface"], 0) + row["WSP1"]
        ret[row["Surface"]] = ret.get(row["Surface"], 0) + 1.0 - row["WSP2"]
        if row["Surface"] == "Grass":
            grass.append(row["WSP1"])
        n += 1
    if row["Loser"] == NAME:
        match[row["Surface"]] = match.get(row["Surface"], 0) + 1
        ser[row["Surface"]] = ser.get(row["Surface"], 0) + row["WSP2"]
        ret[row["Surface"]] = ret.get(row["Surface"], 0) + 1.0 - row["WSP1"]
        if row["Surface"] == "Grass":
            grass.append(row["WSP2"])
        n += 1

wins["All"] = wins["Hard"] + wins["Grass"] + wins["Carpet"] + wins["Clay"]
match["All"] = match["Hard"] + match["Grass"] + match["Carpet"] + match["Clay"]
ret["All"] = ret["Hard"] + ret["Grass"] + ret["Carpet"] + ret["Clay"]
ser["All"] = ser["Hard"] + ser["Grass"] + ser["Carpet"] + ser["Clay"]

print NAME, "n =", n
print "=================================="
print "Hard: ", 1.0 * wins["Hard"] / match["Hard"], 1.0 * ser["Hard"] / match["Hard"], 1.0 * ret["Hard"] / match["Hard"], match["Hard"]
print "Clay: ", 1.0 * wins["Clay"] / match["Clay"], 1.0 * ser["Clay"] / match["Clay"], 1.0 * ret["Clay"] / match["Clay"], match["Clay"]
print "Grass: ", 1.0 * wins["Grass"] / match["Grass"], 1.0 * ser["Grass"] / match["Grass"], 1.0 * ret["Grass"] / match["Grass"], match["Grass"]
print "Carpet: ", 1.0 * wins["Carpet"] / match["Carpet"], 1.0 * ser["Carpet"] / match["Carpet"], 1.0 * ret["Carpet"] / match["Carpet"], match["Carpet"]
print "All: ", 1.0 * wins["All"] / match["All"], 1.0 * ser["All"] / match["All"], 1.0 * ret["All"] / match["All"], match["All"]


n2 = match["Clay"] * 100
p = 1.0 * ser["Clay"] / match["Clay"]
predict_var = math.sqrt(p * (1.0 - p) / n2)
h = predict_var
interval = (p - h, p + h)
print "Interval: ", interval

# Fit a normal distribution to the data:
data = np.array(grass)
mu, std = norm.fit(data)
# std = math.sqrt(mu * (1.0 - mu) / (100.0 * np.size(data)))

# Plot the histogram.
plt.hist(data, normed=True, alpha=0.6, color='b')
xmin, xmax = plt.xlim()
x = np.linspace(xmin, xmax, 100)
p = norm.pdf(x, mu, std)

plt.plot(x, p, 'k', linewidth=2)

plt.xlim([0.5, 0.9])

plt.axvline(mu, color='k', linestyle='solid', linewidth=2, label="Average on grass")
plt.axvline(mu+std, color='k', linestyle='dashed', linewidth=2, label="First std interval")
plt.axvline(mu-std, color='k', linestyle='dashed', linewidth=2)
plt.axvline( 1.0 * ser["All"] / match["All"], color='r', linestyle='solid', linewidth=2, label="Overall average")
plt.legend(bbox_to_anchor=(1, 1),prop={'size':11}, loc=1, borderaxespad=0.)

plt.show()