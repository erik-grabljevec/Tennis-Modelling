import models

import data_tools as dt


model = models.DoubleModifiedGlickoModel()

data = dt.get_main_matches_data()

models.analyse_ranking_model(model, report_name="elo_re", verbose=True)