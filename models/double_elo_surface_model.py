__author__ = 'riko'

import math

import numpy as np
import scipy as sp
import scipy.stats

import calculations as calc
import ranking_systems as rs
import tennis_model as tm
from tennis_model import overrides

ALPHA = 0.01
CONF = [0,0,0,0]+[sp.stats.t.ppf((1+ALPHA)/2., 100*n2-1) for n2 in xrange(5, 2000)]

class Surface(object):
    '''
    Wrapper for surface stats.
    '''

    def __init__(self):
        '''
        Constructor.
        '''

        self.ser = 0.0
        self.ret = 0.0
        self.n = 0

    def get(self):
        '''
        Get lower bound.
        '''

        if self.n == 0:
            return [0.0, 0.0]

        return self.ser / self.n, self.ret / self.n

    def update(self, ser, ret):
        '''
        Add.
        '''

        self.ser += ser
        self.ret += ret
        self.n += 1


class Player(object):
    '''
    Player stats wrapper.
    '''

    def __init__(self):
        '''
        Constructor.

        :return: void.
        '''

        self.surface = {}
        self.surface["All"] = Surface()

    def get_advantage(self, surface):
        '''
        Comment.
        '''

        ser_1, ret_1 = self.surface["All"].get()
        try: self.surface[surface]
        except: self.surface[surface] = Surface()
        ser_2, ret_2 = self.surface[surface].get()

        n = self.surface[surface].n
        n2 = 100 * n

        if n <= 5:
            return 0.0, 0.0, 1.0, 1.0

        p = ser_2
        predict_var = math.sqrt(p * (1.0 - p) / n2)
        h1 = predict_var * CONF[n]
        ser = (ser_2 - ser_1)

        p = ret_2
        predict_var = math.sqrt(p * (1.0 - p) / n2)
        h2 = predict_var * CONF[n]
        ret = (ret_2 - ret_1)

        return ser, ret, h1, h2

    def update(self, ser, ret, surface):
        '''
        comment
        '''

        self.surface["All"].update(ser, ret)
        try: self.surface[surface]
        except: self.surface[surface] = Surface()

        self.surface[surface].update(ser, ret)


class DoubleEloSurfaceModel(tm.TennisRankingModel):
    '''
    This is double surface Elo model.
    '''

    def __init__(self, **kwargs):
        '''
        Constructor.

        :return: void
        '''

        self.params = {"mu": 1500, "K": 11.35, "edge": 0.1}
        self.params.update(kwargs)
        super(self.__class__, self).__init__(**kwargs)
        self.player_rankings = {}
        self.surface_advantage = {}
        self.player_games = {}
        self.name = "DoubleEloSurface"

    @overrides(tm.TennisRankingModel)
    def run(self, data, verbose=False):
        '''
        Override function from superclass.

        :param data: Pandas dataframe on which to test model.
        :return: void
        '''

        r = self.player_rankings
        s = self.surface_advantage
        g = self.player_games

        elo = rs.Elo(self.params["mu"], self.params["K"])
        edge = self.params["edge"]
        probabilities = []
        bet_amount = []

        for i, row in data.iterrows():
            name1 = row["Winner"]
            name2 = row["Loser"]
            wsp1 = row["WSP1"]
            wsp2 = row["WSP2"]

            # If there is no data on serve win percentage, skip.
            if math.isnan(wsp1) or math.isnan(wsp2):
                probabilities.append(0.5)
                bet_amount.append(0)
                continue

            if not r.get(name1, False):
                r[name1] = [elo.create_rating(), elo.create_rating()]
                s[name1] = Player()
            if not r.get(name2, False):
                r[name2] = [elo.create_rating(), elo.create_rating()]
                s[name2] = Player()

            s1, r1, h11, h12 = s[name1].get_advantage(row["Surface"])
            s2, r2, h21, h22 = s[name2].get_advantage(row["Surface"])
            h1 = h11 + h22
            h2 = h12 + h21

            a1 = s1 - r2
            if a1 + h1 < 0.0: a1 += h1
            elif a1 - h1 > 0.0: a1 -= h1
            else: a1 = 0

            a2 = s2 - r1
            if a2 + h2 < 0.0: a2 += h2
            elif a2 - h2 > 0.0: a2 -= h2
            else: a2 = 0

            p = elo.expect(r[name1][0], r[name2][1]) + edge + a1
            q = elo.expect(r[name2][0], r[name1][1]) + edge + a2

            s[name1].update(wsp1, 1.0 - wsp2, row["Surface"])
            s[name2].update(wsp2, 1.0 - wsp1, row["Surface"])

            win_prob = calc.prob_win_match(p, q, row["Best_of"])

            g[name1] = g.get(name1, 0.0) + 1
            g[name2] = g.get(name2, 0.0) + 1

            """
            if g[name1]>5 and g[name2]>5:
                bet_amount.append(1)
            else:
                bet_amount.append(0)
            """

            bet_amount.append(1)
            probabilities.append(win_prob)

            r[name1][0], r[name2][1] = elo.match(r[name1][0], r[name2][1], wsp1 - edge)
            r[name2][0], r[name1][1] = elo.match(r[name2][0], r[name1][1], wsp2 - edge)

        self.surface_advantage = s
        self.player_rankings = r
        self.player_games = g

        if verbose:
            sez = sorted([[rt[0].rating, rt[1].rating, str(key)] for key, rt in r.iteritems()], key=lambda x: x[0]+x[1], reverse=True)
            print '\n'.join(['{:>22s} {:8.1f} {:8.1f}'.format(p[2], p[0], p[1]) for p in sez[:20]]) + "\n\n"

        df = data.copy()
        df["win_prob"] = probabilities
        df["bet_amount"] = bet_amount

        return df

    @overrides(tm.TennisRankingModel)
    def _train_params(self, x, train_data, verbose=False):
        '''
        Train model for given parameters.

        :param x: Parameters.
        :param train_data: Data on which to train.
        :param verbose: Log or not?
        :return: Error for given paramters "x".
        '''

        self.params["K"] = x[0]
        self.player_rankings = {}
        self.surface_advantage = {}
        error = self.train(train_data, verbose)

        if verbose:
            print "Parameters: ", x
            print "Error: ", error
            print
            print

        return error