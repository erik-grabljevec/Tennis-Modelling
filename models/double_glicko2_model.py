__author__ = 'riko'

import math

import calculations as calc
import ranking_systems as rs
import tennis_model as tm
from tennis_model import overrides


class DoubleGlicko2Model(tm.TennisRankingModel):
    '''
    This is double Glicko2 model.
    '''

    def __init__(self, **kwargs):
        '''
        Constructor.

        :return: void
        '''

        self.params = {"mu": 1500.0,
                       "phi": 350.0,
                       "sigma":0.06,
                       "tau": 1,
                       "eps": 0.000001
                       }
        self.params.update(kwargs)
        super(self.__class__, self).__init__(**kwargs)
        self.player_rankings = {}
        self.name = "DoubleGlicko2"

    @overrides(tm.TennisRankingModel)
    def run(self, data, verbose=False):
        '''
        Override function from superclass.

        :param data: Pandas dataframe on which to test model.
        :return: void
        '''

        r = self.player_rankings
        p = self.params
        glicko = rs.Glicko2(p["mu"], p["phi"], p["sigma"], p["tau"], p["eps"])
        probabilities = []
        bet_amount = []
        P = []
        Q = []

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
                r[name1] = [glicko.create_rating(), glicko.create_rating()]
            if not r.get(name2, False):
                r[name2] = [glicko.create_rating(), glicko.create_rating()]

            p = glicko.expect(r[name1][0], r[name2][1])
            q = glicko.expect(r[name2][0], r[name1][1])
            P.append(p)
            Q.append(q)
            win_prob = calc.prob_win_match(p, q, row["Best_of"])
            probabilities.append(win_prob)
            bet_amount.append(1)

            r[name1][0], r[name2][1] = glicko.rate_1vs1(r[name1][0], r[name2][1], wsp1 )
            r[name2][0], r[name1][1] = glicko.rate_1vs1(r[name2][0], r[name1][1], wsp2)

        self.player_rankings = r

        if verbose:
            sez = sorted([[rt[0].mu, rt[1].mu, key] for key, rt in r.iteritems()], key=lambda x: x[0]+x[1], reverse=True)
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

        self.params["phi"] = x[0]
        self.params["sigma"] = x[1]
        self.params["tau"] = x[2]
        error = self.train(train_data, verbose)

        if verbose:
            print "Parameters: ", x
            print "Error: ", error
            print
            print

        return error
