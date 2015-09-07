'''
This file implements Elo ranking system.
How Elo ranking system works can be read here:
https://en.wikipedia.org/wiki/Elo_rating_system
'''


__author__ = 'riko'

import copy


class Rating(object):
    '''
    Wrapper class containing all information needed about a rating.
    '''

    def __init__(self, rating):
        '''
        Constructor.

        :param rating: Start value.
        :return:
        '''

        self.rating = rating

    def update(self, new_rating):
        '''
        Updates parameters after a match.
        :return:
        '''

        change = new_rating - self.rating
        self.rating += change

    def __repr__(self):
        '''
        Overridden function for representation.
        :return: Representation of rating with string.
        '''

        return "Rating %d." % self.rating


class Elo(object):
    '''
    Elo ranking system. Originally used for ranking of chess players.
    '''

    def __init__(self, mu=1500, K=32):
        '''
        Constructor.

        :param mu: Mean value.
        :param K: Rating modification factor.
        :return:
        '''

        self.mu = mu
        self.K = K

    def create_rating(self, rating=None):
        '''
        Creates new class Ranking. Parameters that are not provided will
        be given default values.

        :param rating: Mean value.
        :return: New Rating class with provided parameters.
        '''

        if rating is None:
            rating = self.mu

        return Rating(rating)

    def expect(self, rating1, rating2):
        '''
        Expected score.

        :param rating1: First rating.
        :param rating2: Second rating.
        :return: Expected score for player with rating1 when players
                 with rating1 and rating2 compete.
        '''

        exponent = -(rating1.rating - rating2.rating) / 400
        result = 1.0 / (1.0 + 10.0 ** exponent)

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
        new_rating = rating.rating + self.K * (result - E)
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
