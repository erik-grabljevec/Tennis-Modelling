__author__ = 'riko'

import math

import calculations as calc
import ranking_systems as rs
import tennis_model as tm
from tennis_model import overrides

class DoubleEloModel(tm.TennisRankingModel):
    '''
    This is double Elo model.
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
        self.player_games = {}
        self.name = "DoubleElo"

    @overrides(tm.TennisRankingModel)
    def run(self, data, verbose=False):
        '''
        Override function from superclass.

        :param data: Pandas dataframe on which to test model.
        :return: void
        '''

        r = self.player_rankings
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
            if not r.get(name2, False):
                r[name2] = [elo.create_rating(), elo.create_rating()]

            p = elo.expect(r[name1][0], r[name2][1]) + edge
            q = elo.expect(r[name2][0], r[name1][1]) + edge

            win_prob = calc.prob_win_match(p, q, row["Best_of"])
            probabilities.append(win_prob)
            # probabilities.append(random.random())
            bet_amount.append(1)

            if name1 == "Novak Djokovic" and name2 == "Roger Federer":
                print p, " vs ", q


            g[name1] = g.get(name1, 0.0) + 1
            g[name2] = g.get(name2, 0.0) + 1

            """
            if g[name1]>100 and g[name2]>100:
                bet_amount.append(1)
            else:
                bet_amount.append(0)
            """

            r[name1][0], r[name2][1] = elo.match(r[name1][0], r[name2][1], wsp1 - edge)
            r[name2][0], r[name1][1] = elo.match(r[name2][0], r[name1][1], wsp2 - edge)

        self.player_rankings = r
        self.player_games = g

        if verbose:
            sez = sorted([[rt[0].rating, rt[1].rating, key] for key, rt in r.iteritems()], key=lambda x: x[0]+x[1], reverse=True)
            print '\n'.join(['{:>22s} {:8.1f} {:8.1f}'.format(str(p[2]), p[0], p[1]) for p in sez[:20]]) + "\n\n"

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
        error = self.train(train_data, verbose)

        if verbose:
            print "Parameters: ", x
            print "Error: ", error
            print
            print

        return error