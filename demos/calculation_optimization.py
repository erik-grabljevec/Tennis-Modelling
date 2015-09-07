'''
Testing difference between cython and python impementation
of function in calculations module.
'''

__author__ = 'riko'


import time

import models.calculations as calc


def prob_win_game(p):
    '''
    Probability of player winning game.

    :param p: Probability of player winning point.
    :return: Probability of player winning game from 0 to 1
    '''

    nom = p**4 * (15 - 4 * p - (10. * p**2))
    den = 1 - 2 * p * (1 - p)
    return nom / den


start = time.clock()
p2 = prob_win_game(0.5)
end = time.clock()

print "Python implementation (ms): ", (end - start) * 1000


start = time.clock()
p2 = calc.prob_win_game(0.5)
end = time.clock()

print "Cython implementation (ms): ", (end - start) * 1000

print "Cpython makes expected 3x speed up on very simple function."