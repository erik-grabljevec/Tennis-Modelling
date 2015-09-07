__author__ = 'riko'


import math

import numpy as np

import calculations as calc
import ranking_systems as rs
import tennis_model as tm
from tennis_model import overrides


class Player(object):
    '''
    Class containing all data about the tennis player including specific
    ratings used in this model.
    '''

    def __init__(self, name, mg_att, mg_def):
        '''
        Constructor.

        :param mg_att: Modified glicko ranking for serve of player.
        :param mg_def: Modified glicko ranking for return of player.
        :return: void
       '''

        self.name = name
        self.mg_att = mg_att
        self.mg_def = mg_def

    def get_info(self):
        '''
        Returns most important information on player as a list.

        :return: List [name, att, def] where att is serve strength rating and
                  def is return strength rating.
        '''

        return (self.name, self.mg_att.rating, self.mg_def.rating)

    def __repr__(self):
        '''
        Overriden representation function. It takes information from method
        get_info and turns it into a string.

        :return: String representation of player.
        '''

        args = self.get_info()
        return "Player %s, att: %d, def: %d" % args


class Match(object):
    '''
    This is class that creates new Players and also plays them against one
    another.
    '''

    def __init__(self, mu=1500, sigma_start=350,
                 sigma_cap=100, c=100, Q=1.0/200):
        '''
        Constructor.

        :param mu: Mean value.
        :param sigma_start: Starting sigma.
        :param sigma_cap: Final sigma.
        :param c: Sigma decrementing factor.
        :param Q: Rating modification factor.
        :return: void
        '''

        self.mu = mu
        self.sigma_start = sigma_start
        self.sigma_cap = sigma_cap
        self.c = c
        self.Q = Q
        self.glicko = rs.ModifiedGlicko(mu, sigma_start, sigma_cap, c, Q)

    def create_player(self, name=None, mu=None, sigma_start=None,
                      sigma_cap=None,c=None):
        '''
        Creates new class Player. Parameters that are not provided will
        be given default values.

        :param mu: Mean value.
        :param sigma_start: Starting sigma.
        :param sigma_cap: Final sigma.
        :param c: Sigma decrementing factor.
        :return: New Ranking class with provided parameters.
        '''

        if name is None:
            name = 'Unknown'
        if mu is None:
            mu = self.mu
        if sigma_start is None:
            sigma_start = self.sigma_start
        if sigma_cap is None:
            sigma_cap = self.sigma_cap
        if c is None:
            c = self.c

        a = self.glicko.create_rating(mu, sigma_start, sigma_cap, c)
        d = self.glicko.create_rating(mu, sigma_start, sigma_cap, c)

        return Player(name, a, d)

    def match(self, player1, player2, result1, result2):
        '''
        Matches player1 vs player2 and modifies all ratings according to
        double modified glicko model.

        :param player1: Class player for player1
        :param player2: Class player for player2
        :param result1: What serve % did player1 win against player2
        :param result2: What serve % did player2 win against player1
        :return: Tuple of updates classes player1 and player2
        '''

        a = player1.mg_att
        r = player2.mg_def
        player1.mg_att, player2.mg_def = self.glicko.match(a, r, result1)

        a = player2.mg_att
        r = player1.mg_def
        player2.mg_att, player1.mg_def = self.glicko.match(a, r, result2)

        return player1, player2

    def expect(self, player1, player2):
        '''
        Expected result of player1 going against player2.

        :param player1: Class player for player1
        :param player2: Class player for player2
        :return: Tuple (result1, result2) of expected serve wins for player1
                  and player2.
                  e.g.: Result1 is % of serve that player1 is expected
                        to win over player2.
        '''

        result1 = self.glicko.expect(player1.mg_att, player2.mg_def)
        result2 = self.glicko.expect(player2.mg_att, player1.mg_def)

        return result1, result2

    def win_probabilities(self, player1, player2, best_of=3):
        '''
        Calculates fair betting odds according to our model and returns them
        as tuple.

        :param player1: Class player for player1
        :param player2: Class player for player2
        :param best_of: How many sets we are playing
        :return: Tuple (odds1, odds2), representing fair odds for player
                    one or two winning
        '''

        p, q = self.expect(player1, player2)

        win_prob = calc.prob_win_match(p, q, best_of)

        return (win_prob, 1 - win_prob, p, q)


class DoubleModifiedGlickoModel(tm.TennisRankingModel):
    '''
    This is double Glicko2 model. Idea is to continuously compare players and
    update their rankings accordingly. However there is a twist, as each player
    has two rankings - serve and return ranking. Each match is then looked at
    as two matches and there are 4 rankings updated.

    Idea of the model is to use large data that is available to ranking models,
    while having more insight into match as we can do point by point analysis.

    The two rankings of each player are updated based on the results of the
    previous match in a Bayesian fashion with some simplifications.

    Parameters of the model:
    * mu - starting rating
    * sigma_start - starting sigma of a player
    * sigma_end - smallest possible sigma player can have
    * c - sigma modification factor
    * Q - rating modification factor
    '''

    def __init__(self, **kwargs):
        '''
        Constructor.

        :return: void
        '''

        self.params = {"mu": 1500.0,
                      "start_sigma": 55.0,
                      "end_sigma": 45.7,
                      "c": 9.3,
                      "Q": 0.0057565
                       }
        self.params.update(kwargs)
        super(self.__class__, self).__init__(**kwargs)
        self.player_rankings = {}
        self.player_games = {}
        self.name = "DoubleModifiedGlicko"

    @overrides(tm.TennisRankingModel)
    def run(self, data, verbose=False):
        '''
        Override function from superclass.

        :param data: Pandas dataframe on which to test model.
        :return: void
        '''

        r = self.player_rankings
        p = self.params
        g = self.player_games
        glicko = Match(p["mu"], p["start_sigma"], p["end_sigma"], p["c"], p["Q"])
        probabilities = []
        bet_amount = []
        P = []
        Q = []
        ser_list = []
        ret_list = []

        for i, row in data.iterrows():
            name1 = row["Winner"]
            name2 = row["Loser"]
            wsp1 = row["WSP1"]
            wsp2 = row["WSP2"]

            # If there is no data on serve win percentage, skip.
            if math.isnan(wsp1) or math.isnan(wsp2):
                probabilities.append(0.51)
                bet_amount.append(0)
                continue

            if not r.get(name1, False):
                r[name1] = glicko.create_player(name1)
            if not r.get(name2, False):
                r[name2] = glicko.create_player(name2)

            p1, p2, p, q = glicko.win_probabilities(r[name1], r[name2], row["Best_of"])
            probabilities.append(p1)
            bet_amount.append(1)
            s1 = r[name1].mg_att.sigma
            s2 = r[name2].mg_att.sigma
            s = r[name1].mg_att.sigma_cap


            r1, r2 = glicko.match(r[name1], r[name2], wsp1, wsp2)
            r[name1], r[name2] = r1, r2

            ret, ser = r1.mg_def.rating, r1.mg_att.rating


        self.player_rankings = r
        self.player_games = g

        if verbose:
            self.top_n_players(20, True)

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

        self.params["start_sigma"] = x[0]
        self.params["end_sigma"] = x[1]
        self.params["c"] = x[2]
        self.player_rankings = {}
        error = self.train(train_data, verbose)

        if verbose:
            print "Parameters: ", x
            print "Error: ", error
            print
            print

        return error

    def top_n_players(self, n, verbose=False):
        '''
        Get list of top n players according to their rating.

        :param n: Number of players we want to get.
        :param verbose: Log or not.
        :return: Sorted list of top n players.
        '''

        sez = [player.get_info() for id, player in self.player_rankings.iteritems()]
        sez = sorted(sez, key=lambda x: x[1] + x[2], reverse=True)

        if verbose:
            for p in sez[:n]:
                print '{:>22s} {:8.1f} {:8.1f}'.format(str(p[0]), p[1], p[2])

        top_n = [p[0] for p in sez[:n]]

        return top_n

    def create_data_js(self, train_data, n, directory):
        '''

        :param n:
        :return:
        '''

        train_data.sort("Date")
        self.train(train_data)
        top_n = self.top_n_players(n)

        lt = ""
        tc = 0
        tours = []

        ranking = {}
        data = {}
        p = self.params
        glicko = Match(p["mu"], p["start_sigma"], p["end_sigma"], p["c"], p["Q"])

        for name in top_n:
            ranking[name] = glicko.create_player(name)
            data[name] = {"rating": [{"return": 1500, "serve": 1500}], "name": name}

        for i, row in train_data.iterrows():
            name1 = row["Winner"]
            name2 = row["Loser"]
            wsp1 = row["WSP1"]
            wsp2 = row["WSP2"]

            # If there is no data on serve win percentage, skip.
            if math.isnan(wsp1) or math.isnan(wsp2):
                continue

            if not ranking.get(name1, False):
                ranking[name1] = glicko.create_player(name1)
            if not ranking.get(name2, False):
                ranking[name2] = glicko.create_player(name2)

            r1, r2 = glicko.match(ranking[name1], ranking[name2], wsp1, wsp2)
            ranking[name1], ranking[name2] = r1, r2

            if (name1 in top_n or name2 in top_n) and row["Tournament"] != lt:
                lt = row["Tournament"]
                tc += 1
                tours.append({"text": lt + " " + str(row["Date"]), "value": tc, "games": []})
                for name in top_n:
                    r = ranking[name]
                    ret, ser = int(r.mg_def.rating), int(r.mg_att.rating)
                    data[name]["rating"].append({"return": ret, "serve": ser})

            if len(tours) and row["Tournament"] == lt:
                game = "%s | %s vs %s: %s." % (row["Round"], name1, name2, row["Score"])
                tours[-1]["games"].append(game)

        alpha = 0.05
        for key, value in data.iteritems():
            points = len(value["rating"])
            ret = np.array([float(x["return"]) for x in data[key]["rating"]])
            ser = np.array([float(x["serve"]) for x in data[key]["rating"]])
            ret = calc.smooth_time_series_exp(ret, alpha)
            ser = calc.smooth_time_series_exp(ser, alpha)
            new_rating = [{"return": r, "serve": s} for r, s in zip(ret, ser)]
            data[key]["rating"] = new_rating

        sez = sorted([value for key, value in data.iteritems()])
        
        with open(directory, 'w') as f:
            f.write("data = ")
            f.write(str(sez))
            f.write("\n")
            f.write("n_points = ")
            f.write(str(points))
            f.write("\n")
            f.write("tours = ")
            f.write(str(tours))

"""
Example

m = Match()
modg = mg.ModifiedGlicko()
p1 = m.create_player("A")
p2 = m.create_player("B")

p1, p2 = m.match(p1, p2, 0.4, 0.55)
p1, p2 = m.match(p1, p2, 0.6, 0.75)
p1, p2 = m.match(p1, p2, 0.8, 0.9)
p1, p2 = m.match(p1, p2, 0.2, 0.3)
p1, p2 = m.match(p1, p2, 0.4, 0.55)
p1, p2 = m.match(p1, p2, 0.6, 0.75)
p1, p2 = m.match(p1, p2, 0.8, 0.9)
p1, p2 = m.match(p1, p2, 0.2, 0.8)

print p1
print p2
print p1.mg_att.sigma
print "Expect: ", m.expect(p1, p2)
print "Impact: ", modg.impact(p1.mg_att)
print "Probability: ", m.win_probabilities(p1, p2)

"""