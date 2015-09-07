'''
Collection of all models.
All models should be derived from TennisModel in tennis_model.py.
This will enable universal training and testing.
'''

__author__ = 'riko'
__all__ = ['calculations']

from barnett_model import BarnettModel
from double_elo_model import DoubleEloModel
from double_elo_surface_model import DoubleEloSurfaceModel
from double_glicko2_model import DoubleGlicko2Model
from double_modified_glicko_model import DoubleModifiedGlickoModel
from modified_glicko_model import ModifiedGlickoModel
from random_model import RandomModel

from analysis import *
from tennis_model import *

