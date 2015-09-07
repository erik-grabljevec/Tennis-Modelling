'''
This demo creates all tables used in chapter 2 of my thesis.
'''

__author__ = 'riko'


import calculations


p = 0.55
q = 0.59

pg = 1; qg = 1; pt = 1  # Dummy inits.


################################################################################
#   Functions for all levels of game.                                          #
################################################################################

memo1 = [[0 for i in range(5)] for j in range(5)]
memo2 = [[0 for i in range(8)] for j in range(8)]
memo3 = [[0 for i in range(7)] for j in range(7)]
memo4 = [[0 for i in range(4)] for j in range(4)]


def game(a=0, b=0):
    if a == 3 and b == 3:
        prob = p ** 2 / (p ** 2 + (1.0 - p) ** 2)
    elif a == 4:
        prob = 1.0
    elif b == 4:
        prob = 0.0
    else:
        prob = p * game(a+1, b) + (1.0 - p) * game(a, b+1)

    memo1[a][b] = prob
    return prob


def tiebreaker(a=0, b=0):
    if a == 6 and b == 6:
        p1 = p * (1.0 - q)
        p2 = q * (1.0 - p)
        prob = p1 / (p1 + p2)
    elif a == 7:
        prob = 1.0
    elif b == 7:
        prob = 0.0
    else:
        if ((a+b+1)/2)%2==0:
            prob = p * tiebreaker(a+1, b) + (1.0 - p) * tiebreaker(a, b+1)
        else:
            prob = (1.0 - q) * tiebreaker(a+1, b) + q * tiebreaker(a, b+1)

    memo2[a][b] = prob
    return prob


def set(a=0, b=0):
    if a == 5 and b == 5:
        prob = pg * (1 - qg) + (pg * qg + (1 - pg) * (1 - qg)) * pt
    elif a == 6:
        prob = 1.0
    elif b == 6:
        prob = 0.0
    else:
        if (a + b) % 2 == 0:
            prob = pg * set(a+1, b) + (1.0 - pg) * set(a, b+1)
        else:
            prob = qg * set(a, b+1) + (1.0 - qg) * set(a+1, b)

    memo3[a][b] = prob
    return prob


def match(a=0, b=0, best_of=3):
    win_score = (best_of + 1) / 2
    if a == win_score:
        prob =  1.0
    elif b == win_score:
        prob = 0.0
    else:
        prob = ps * match(a+1, b, best_of) + (1 - ps) * match(a, b+1, best_of)

    memo4[a][b] = prob
    return prob


def print_table(memo):
    N = len(memo)
    for i in range(N):
        print " ".join("%.2f" % j for j in memo[i])


################################################################################
#   Print all tables.                                                          #
################################################################################

# Game.
pg = game()
p_t = p; p = q; qg = game(); p = p_t
confirm = calculations._prob_win_game(p)
print "p:", p
print_table(memo1)
print "Confirming with calculations: ", confirm
print

# Tiebreaker.
pt = tiebreaker()
confirm = calculations._prob_win_tiebreaker(p, q)
print "pt:", pt
print_table(memo2)
print "Confirming with calculations: ", confirm
print

# Set.
ps = set()
confirm = calculations._prob_win_set(p, q)
print "pg, qg:", pg, qg
print_table(memo3)
print "Confirming with calculations: ", confirm
print

# Match.
pm = match(best_of=5)
confirm = calculations.prob_win_match(p, q, 5)
print "pm, ", pm
print_table(memo4)
print "Confirming with calculations: ", confirm
print