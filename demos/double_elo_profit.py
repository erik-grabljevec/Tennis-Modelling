#!/usr/bin/python
# coding: utf-8
"""
Generate graph of profit against Stratagem data for 2012.
"""

__author__ = 'riko'


import datetime

import matplotlib.pyplot as plt
import numpy as np
import pickle

import data_tools as dt
import models
import settings as stg


model = models.DoubleEloSurfaceModel()

file = stg.ROOT_PATH + "data/stratagem_data.p"
data = pickle.load(open(file, "rb" ))

bo3_mask = (data["match_type"] == "bo3")
data = data.rename(columns={"ID1":"Winner", "ID2":"Loser",
                            "DATE_G_y":"Date", "K1":"Winner_odds",
                            "K2":"Loser_odds", "match_type":"Best_of",
                            "ID_C": "Surface"})
data["Best_of"][bo3_mask] = 3
data["Best_of"][~bo3_mask] = 5
data = data.sort("Date")

model = models.DoubleEloSurfaceModel()

train_range = [datetime.date(2003, 1, 1), datetime.date(2012, 1, 1)]
train_data = dt.filter_data_time_range(data, train_range)
model.train(train_data, True)

test_range = [datetime.date(2012, 1, 1), datetime.date(2013, 1, 1)]
test_data = dt.filter_data_time_range(data, test_range)
df = model.test(test_data, True)

n = np.size(df["bet_amount"])
print "n: ", n

v_df = df
bet_on_p1_mask = ( 1.0 / np.array(v_df["win_prob"]) < np.array(v_df["Winner_odds"]) ) * df["bet_amount"]
bet_on_p2_mask = ( 1.0 / (1.-np.array(v_df["win_prob"])) < np.array(v_df["Loser_odds"]) ) * df["bet_amount"]
ret = np.sum(v_df[bet_on_p1_mask > 0]["Winner_odds"] * df["bet_amount"])
bet_amount = np.sum(bet_on_p1_mask) + np.sum(bet_on_p2_mask)
bets_done = np.sum(bet_on_p1_mask > 0) + np.sum(bet_on_p2_mask > 0)
r = bets_done, bet_amount, ret

print "bets taken: ", r[0]
print "return: ", r[2] / r[1] - 1.0

result = np.cumsum(bet_on_p1_mask * (v_df["Winner_odds"]-1) - bet_on_p2_mask, axis=0)

x = [i for i in range(1, np.size(result) + 1)]

# Draw this s*it.

fig, ax = plt.subplots()
plt.plot(x, result, '-r')

ax.yaxis.grid(True, which='major')

plt.xlabel('Match number', fontsize=10)
plt.ylabel('Comulative profit', fontsize=10)

plt.show()