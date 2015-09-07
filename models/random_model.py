__author__ = 'riko'


import random

import numpy as np

import tennis_model as tm
from tennis_model import overrides


class RandomModel(tm.TennisRankingModel):
    '''
    This is Random model.
    '''

    def __init__(self, **kwargs):
        '''
        Constructor.

        :return: void
        '''

        self.params = {}
        self.params.update(kwargs)
        super(self.__class__, self).__init__(**kwargs)
        self.player_rankings = {}
        self.name = "Random"

    @overrides(tm.TennisRankingModel)
    def run(self, data, verbose=False):
        '''
        Override function from superclass.

        :param data: Pandas dataframe on which to test model.
        :return: Updated dataframe.
        '''

        n = np.size(data["Winner"])
        probabilities = [random.random() for i in xrange(n)]
        bet_amount = [1.0 for i in xrange(n)]
        df = data.copy()
        df["win_prob"] = probabilities
        df["bet_amount"] = bet_amount

        return df