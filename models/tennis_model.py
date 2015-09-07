'''
A general tennis_model, from which all other models are implemented.
It is used for training, testing and parameter setting.
'''


__author__ = 'riko'


import numpy as np
import scipy.optimize as sco


def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider


class TennisRankingModel(object):
    '''
    General tennis model. Other models are derived from it.
    '''

    def __init__(self, **kwargs):
        '''
        Constructor.

        :param params: Parameter of the model.
        :return:
        '''

        self.params.update(kwargs)
        self.player_rankings = {}
        self.surface_advantage = {}
        self.player_games = {}

    def reset_rankings(self):
        '''
        Resets player rankings.

        :return: void.
        '''

        self.player_rankings = {}

    def train(self, train_data, verbose=False):
        '''
        Override function from superclass.

        :param test_data: Pandas dataframe on which to train model.
        :return: void
        '''

        self.player_rankings = {}
        self.surface_advantage = {}
        self.player_games = {}
        df = self.run(train_data, verbose)

        return np.sum(-np.log(df["win_prob"]))

    def test(self, test_data, verbose=False):
        '''
        Override function from superclass.

        :param test_data: Pandas dataframe on which to test model.
        :return: void
        '''

        return self.run(test_data, verbose)

    def run(self, data, verbose=False):
        '''
        Override function from superclass.

        :param data: Pandas dataframe on which to run model.
        :return: void
        '''

        raise Exception("Implement this function!")

    def train_params(self, train_data, approx, verbose=False):
        '''
        Train parameters of the model.
        NOTE: _train_params function should return error on train data.

        :param train_data: Data to train parameters on.
        :param approx: Approximation of parameters of the model.
        :param verbose: Log or not?
        :return: Optimized parameters (at best global at worst local optimum).
        '''

        res = sco.minimize(self._train_params, approx,
                           (train_data, verbose), method='Nelder-Mead')
        return res

    def _train_params(self, x, train_data, verbose=False):
        '''
        Function to be implemented in derived class, used by train_params.
        Make sure that this function returns error on provided train set.

        :param x: Parameters to the model.
        :param train_data: Data to train params on.
        :param verbose: Log or not?
        :return: Error, for given parameters.
        '''

        raise Exception("Implement this function!")