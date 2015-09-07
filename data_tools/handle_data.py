'''
This module provides functions for data retrieval.
Set database connection information in file: settings.py
'''

__author__ = 'riko'


import datetime

import MySQLdb
import pandas as pd
import pandas.io.sql as psql

import settings as stg


################################################################################
#    Get DB data.                                                              #
################################################################################


try:
    db_data = stg.MYSQL_SETTINGS
except AttributeError:
    print "Could not load the database settings! Make sure you set them in settings.py"
    raise


################################################################################
#    Query functions.                                                          #
################################################################################


def any_query(query):
    '''
    Generic query.

    :param query: Database query that we want to retrieve.
    :return: A pandas dataframe of the SQL query.
    '''

    mysql_cn = MySQLdb.connect(**db_data)
    df = psql.read_sql(query, con=mysql_cn)
    mysql_cn.close()

    return df


def get_main_matches_data(surface="any"):
    '''
    Get main data on all matches.

    :param t_type:
    :return: Panda series with columns: Winner, Loser, WSP1, WSP2, Date.
                WSP1 means what % of serve player 1 won (anlog for WSP2).
    '''

    sql_q = '''
            SELECT Winner, Loser,
                    (W_1stWon + W_2ndWon)/(W_sv) as WSP1,
                    (L_1stWon + L_2ndWon)/(L_sv) as WSP2,
                    W_sv + L_sv as Serves,
                    Tournament,
                    Round,
                    Best_of,
                    Minutes,
                    Date,
                    Surface,
                    Score,
                    Winner_odds,
                    Loser_odds,
                    Winner_rank,
                    Loser_rank
                FROM Base
                WHERE W_sv != 0 AND L_sv != 0
            '''

    if surface != "any":
        sql_q += " AND Surface='%s'" % surface

    df_matches = any_query(sql_q)
    df_matches = df_matches.sort('Date')

    return df_matches


def get_players():
    '''

    :return: All players.
    '''

    sql_q = "SELECT * FROM Players"

    df_players = any_query(sql_q)
    df_players.drop_duplicates(inplace=True)

    return df_players


def get_tournaments():
    '''

    :return: All tournaments.
    '''

    sql_q = "SELECT * FROM Tournaments"

    df_tournaments = any_query(sql_q)
    df_tournaments.drop_duplicates(inplace=True)

    return df_tournaments


################################################################################
#    Filter functions.                                                         #
################################################################################


def filter_data_time_range(data, time_range=[datetime.date(2001, 1, 1), datetime.date.today()]):
    '''
    Filters data according to time range.

    :param data: Pandas dataframe we want to filter.
    :param time_range: Starting and ending time in datetime.date format.
    :return: Filtered data according to time range.
    '''

    return data[(data.Date >= time_range[0]) & (data.Date < time_range[1])]