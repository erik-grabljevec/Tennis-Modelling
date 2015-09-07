import models

import data_tools as dt


model = models.DoubleEloModel()

data = dt.get_main_matches_data("Grass")

models.analyse_ranking_model(model, report_name="double_elo_sur", verbose=True)