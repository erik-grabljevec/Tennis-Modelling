import data_tools as dt
import models

# SET SOME STUFF
train_data = dt.get_main_matches_data()
directory = "../graphical_tool/static/data.js"
n = 100

# ENJOY
m = models.DoubleEloModel()
m.create_data_js(train_data, n, directory)