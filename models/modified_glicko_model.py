__author__ = 'riko'


import tennis_model as tm
from tennis_model import overrides
import modified_glicko as mg


class ModifiedGlickoModel(tm.TennisRankingModel):
    '''
    This is Modified Glicko model. Idea is to continuously compare players and
    update their rankings accordingly.

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

        :param kwargs: Parameters passed to the model.
        :return: void.
        '''

        self.params = {"mu": 1500.0,
                       "start_sigma": 300.0,
                       "end_sigma": 100.0,
                       "c": 10.0,
                       "Q": 0.0057565
                       }
        super(self.__class__, self).__init__(**kwargs)
        self.name = "ModifiedGlicko"

    @overrides(tm.TennisRankingModel)
    def run(self, data, verbose=False):
        '''
        Override function from superclass.

        :param data: Pandas dataframe on which to run model.
        :return: void
        '''

        p = self.params
        glicko = mg.ModifiedGlicko(p["mu"], p["start_sigma"], p["end_sigma"], p["c"], p["Q"])

        r = self.player_rankings
        probabilities = []
        bet_amount = []
        for i, row in data.iterrows():
            name1 = row["Winner"]
            name2 = row["Loser"]

            if not r.get(name1, False):
                r[name1] = glicko.create_rating()
            if not r.get(name2, False):
                r[name2] = glicko.create_rating()

            prob = glicko.expect(r[name1], r[name2])
            probabilities.append(prob)

            s1 = r[name1].sigma
            s2 = r[name2].sigma
            s = r[name1].sigma_cap
            bet_amount.append((1./s1 + 1./s2) / (2. / s))

            r[name1], r[name2] = glicko.match(r[name1], r[name2], 1.0)

        self.player_rankings = r
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
        error = self.train(train_data, verbose)

        if verbose:
            print "Parameters: ", x
            print "Error: ", error
            print

        return error