import data_tools as dt

import numpy as np


data = dt.get_main_matches_data()

wsp_data = np.append(np.array(data["WSP1"]), np.array(data["WSP2"]))

predict_mean = np.average(wsp_data, axis=0)
predict_var = np.std(wsp_data, axis=0)

print "Mean: ", predict_mean
print "Var: ", predict_var