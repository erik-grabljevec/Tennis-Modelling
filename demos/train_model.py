'''
Train parameters of modified glicko ranking system.
'''


import data_tools as dt
import models

'''
start_sigma = 50.0
end_sigma = 40.0
c = 2.0

approx = [start_sigma, end_sigma, c]

data = dt.get_main_matches_data()
mg = models.DoubleModifiedGlickoModel()
mg.train_params(data, approx, verbose=True)
'''

K = 20.0
approx = [K]

data = dt.get_main_matches_data()
mg = models.DoubleEloModel()
mg.train_params(data, approx, verbose=True)