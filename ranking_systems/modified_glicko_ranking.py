'''
This file contains modified glicko ranking system.
It is inspired by glicko2 model found on next link:
https://github.com/sublee/glicko2/blob/master/glicko2.py
'''


__author__ = 'riko'


import copy
import math


class Rating(object):
    '''
    Wrapper class containing all information needed about a rating.
    '''

    def __init__(self, mu, sigma_start, sigma_cap, c):
        '''
        Constructor.
        :param mu: Mean value.
        :param sigma_start: Starting sigma.
        :param sigma_cap: Smallest possible sigma.
        :param c: Sigma decrementing factor.
        :return:
        '''

        self.rating = mu
        self.c = c
        self.sigma_start = sigma_start
        self.sigma_cap = sigma_cap
        self.t = 0
        self.sigma = self.get_sigma()

    def get_sigma(self):
        '''
        Gets current sigma of this rating.
        :return: Current sigma of rating.
        '''

        s_2 = self.sigma_start - self.t * self.c
        result = max(s_2, self.sigma_cap)
        return 1.0 * result

    def update(self, new_rating):
        '''
        Updates parameters after a match.
        :return:
        '''

        self.rating = new_rating
        self.t += 1
        self.sigma = self.get_sigma()

    def __repr__(self):
        '''
        Overridden function for representation.
        :return: Representation of rating with string.
        '''

        return "Rating %d with variance %d." % (self.rating, self.sigma)


class ModifiedGlicko(object):
    '''
    This is modified glicko ranking system which allows for any result
    between 0 and 1.
    There is also a small twist on variance updates. It can
    never be increased, it starts at some starting value and converges towards
    final value. This is believed to be sufficent for tennis modelling as
    players don't tend to be quitting and returning often as might be the case
    with for example online chess.
    '''

    def __init__(self, mu=1500, sigma_start=350,
                 sigma_cap=100, c=20, Q=0.0057565):
        '''
        Constructor.
        :param mu: Mean value.
        :param sigma_start: Starting sigma.
        :param sigma_cap: Final sigma.
        :param c: Sigma decrementing factor.
        :param Q: Rating modification factor.
        :return:
        '''

        self.mu = mu
        self.sigma_start = sigma_start
        self.sigma_cap = sigma_cap
        self.c = c
        self.Q = Q

    def create_rating(self, mu=None, sigma_start=None, sigma_cap=None, c=None):
        '''
        Creates new class Ranking. Parameters that are not provided will
        be given default values.
        :param mu: Mean value.
        :param sigma_start: Starting sigma.
        :param sigma_cap: Final sigma.
        :param c: Sigma decrementing factor.
        :return: New Ranking class with provided parameters.
        '''

        if mu is None:
            mu = self.mu
        if sigma_start is None:
            sigma_start = self.sigma_start
        if sigma_cap is None:
            sigma_cap = self.sigma_cap
        if c is None:
            c = self.c

        return Rating(mu, sigma_start, sigma_cap, c)

    def impact(self, rating):
        """
        The original form is `g(RD)`. This function reduces the impact of
        games as a function of an opponent's RD.
        """

        sqr = 1 + (3 * self.Q ** 2 * (rating.sigma ** 2) / (math.pi ** 2))
        return 1 / math.sqrt(sqr)

    def expect(self, rating1, rating2):
        '''
        Expected score.
        :param rating1: First rating.
        :param rating2: Second rating.
        :return: Expected score for player with rating1 when players
                 with rating1 and rating2 compete.
        '''

        impact = self.impact(rating2)
        exponent = -impact * (rating1.rating - rating2.rating) / 400
        result = 1.0 / (1 + 10 ** exponent)
        return result

    def rate(self, rating, other_rating, result):
        '''
        Return new rating after rating wins/loses against other_rating with
        result "result".
        :param rating: Rating that we rate.
        :param other_rating: Opponents rating.
        :param result: How much did rating score vs other rating; from 0 to 1
        :return: New rating for player with rating "rating".
        '''

        E = self.expect(rating, other_rating)
        impact = self.impact(other_rating)
        d = math.sqrt( 1.0 / (self.Q**2 * impact**2 * E * (1 - E)) )
        change = (self.Q / (1/rating.sigma**2 + 1/d**2)) * impact * (result - E)
        new_rating = rating.rating + change

        rating_result = copy.copy(rating)
        rating_result.update(new_rating)

        return rating_result

    def match(self, rating1, rating2, result):
        '''
        Update ratings rating1 and rating2 after match with result "result".
        :param rating1: First rating.
        :param rating2: Second rating,
        :param result: How much rating1 scored vs rating2.
        :return: Tuple containing new values for rating1 and rating2.
        '''

        return [self.rate(rating1, rating2, result),
                self.rate(rating2, rating1, 1.0 - result)]

"""
mg = ModifiedGlicko(1500, 300, 100, 20)
p1 = mg.create_rating()
p2 = mg.create_rating()

p1.rating = 1700
p2.rating = 1525
p1.t = 19
p2.t = 5
p1.update(1500)
p2.update(1700)

print p1
print p2
print mg.impact(p2)
print mg.expect(p1, p2)

p1, p2 = mg.match(p1, p2, 0.75)

print "---------------"
print p1
print p2
"""