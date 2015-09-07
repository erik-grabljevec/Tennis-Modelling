'''
Get game probability.
Testing recursive approach vs analytical.
Same example can be found in thesis.
'''


import calculations as calc
import random


def recursive(p, a=0, b=0):
    '''

    :param p: Probability of winning point.
    :return: Probability of winning game.
    '''

    if a == 3 and b == 3:
        return p**2 / (p**2 + (1-p)**2)
    elif a == 4:
        return 1.0
    elif b == 4:
        return 0.0
    else:
        return p * recursive(p, a+1, b) + (1-p) * recursive(p, a, b+1)


def monte_carlo(N, p):
    '''

    :param N: number of runs
    :param p: Probability of winning point.
    :return: Probability of winning game.
    '''

    def monte_carlo_run(p):
        a = 0
        b = 0
        while (a < 4 and b < 4) or abs(a - b) < 2:
            r = random.random()
            if r < p: a += 1
            else: b += 1
        return a > b

    count = 0
    for i in xrange(N):
        count += 1 if monte_carlo_run(p) else 0

    return 1. * count / N


# Lets test code from thesis for example in thesis p=0.54
p = 0.54
a = recursive(p)
b = calc.prob_win_game(p)
c = monte_carlo(1000000, p)

print "Results for game probability with point probability, p = 0.54"
print "Recursive: ", a
print "Analytical: ", b
print "Monte carlo: ", c