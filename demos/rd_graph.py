'''
Create and save graph used in chapter Modfied glicko ranking system.
It shows how rating reliability depends on number of matches played.
'''

import matplotlib.pyplot as plt
import numpy as np


################################################################################
#   Constants.                                                                 #
################################################################################

N = 15
out_dir = "../../thesis_papers/Thesis/rd_graph.png"

################################################################################
#   Generate RD graph.                                                         #
################################################################################

def get_rd(x, rd_start=300, rd_end=100, rd_step=20):
    rd_sug = rd_start - x * rd_step
    return max(rd_sug, rd_end)

get_rd = np.vectorize(get_rd)

x = np.array([i for i in range(N+1)])
y = get_rd(x)
fig = plt.figure()

plt.plot(x, y, '-r')

fig.suptitle('', fontsize=20)
plt.xlim([0, N])
plt.ylim([0, 400])
plt.ylabel('Rating reliability (RD)', fontsize=10)
plt.xlabel('Number of matches played (m)', fontsize=10)

plt.savefig(out_dir)