__author__ = 'riko'

import time
import calculations as calc

p = 0.70
q = 0.70

start = time.clock()
m1 = calc.prob_win_match(p, q)
m2 = calc.monte_carlo_match(p, q)
end = time.clock()

print m1
print m2
print "Time: ", end - start
