__author__ = 'riko'


import math

import calculations as calc
import tennis_model as tm
from tennis_model import overrides


class Player(object):
    '''
    Wraper for stats we need to store for each player in Barnett model.
    '''

    def __init__(self):
        '''
        Constructor.

        :return: void
        '''

        self.ser = 0.6
        self.ret = 0.4
        self.n = 1

    def add(self, ser, ret):
        '''
        Add functions.
        '''

        self.ser += ser
        self.ret += ret
        self.n += 1

    def get(self):
        '''
        Get function.
        '''

        return self.ser / self.n, self.ret / self.n


class BarnettModel(tm.TennisRankingModel):
    '''
    This is Barnett model.
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
        self.name = "Barnett"

    @overrides(tm.TennisRankingModel)
    def run(self, data, verbose=False):
        '''
        Override function from superclass.

        :param data: Pandas dataframe on which to test model.
        :return: void
        '''

        r = self.player_rankings
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
                r[name1] = Player()
            if not r.get(name2, False):
                r[name2] = Player()

            s1, r1 = r[name1].get()
            s2, r2 = r[name2].get()

            p = s1 + r2 - 0.4
            q = s2 + r1 - 0.4

            win_prob = calc.prob_win_match(p, q, row["Best_of"])
            probabilities.append(win_prob)
            bet_amount.append(1)

            r[name1].add(wsp1, 1.0 - wsp2)
            r[name2].add(wsp2, 1.0 - wsp1)

        self.player_rankings = r

        if verbose:
            sez = sorted([[rt.get()[0], rt.get()[1], key] for key, rt in r.iteritems()], key=lambda x: x[0]+x[1], reverse=True)
            print '\n'.join(['{:>22s} {:8.5f} {:8.5f}'.format(p[2], p[0], p[1]) for p in sez[:20]]) + "\n\n"

        df = data.copy()
        df["win_prob"] = probabilities
        df["bet_amount"] = bet_amount

        return df

