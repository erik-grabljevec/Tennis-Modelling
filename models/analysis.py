'''
Collection of functions that analyse models derived from TennisModel.
'''


__author__ = 'riko'


import datetime
import math

import numpy as np
import scipy as sp
import scipy.stats

import data_tools as dt
import settings as stg


def np_latex_table(a):
    '''
    Returns inner part of latex table.

    :param a: Numpy array.
    :return: Latex table as a string.
    '''

    if len(a.shape) > 2:
        raise ValueError('bmatrix can at most display two dimensions')
    lines = np.array_str(a, precision=5).replace('[', '').replace(']', '').splitlines()
    return "\n".join(['  ' + ' & '.join(l.split()) + r'\\' for l in lines])


def latex_year_table(a):
    '''
    Returns a LaTeX table used in analysis ranking model function.

    :param a: Numpy array.
    :return: LaTeX table as a string.
    '''

    string = r"""
$
\begin{array}{*{4}{r}}
    2012 & 2013 & 2014 & 2015 \\
    \hline
    """
    string += np_latex_table(a)
    string += r"""
\end{array}
$"""

    return string

def weighted_avg_and_std(values, weights):
    '''
    Calculate weighted average and variance.

    :param values: Values to calculate on.
    :param weights: Weights used.
    :return: Tuple (average, std.).
    '''
    average = np.average(values, weights=weights)
    variance = np.average((values-average)**2, weights=weights)  # Fast and numerically precise
    return (average, math.sqrt(variance))


def test_profitability(data, K=0.0):
    '''
    Tests profitability of betting strategy.

    :param data: Dataframe on which we want to test profitability. It
                    needs columns "win_prob" and "bet_amount" - from 0 to 1
    :return: Tuple (taken, bet, ret), taken - how many bets have we placed,
                bet - how much we bet, ret - how much we earn
    '''

    v_df = data
    bet_on_p1_mask = ( K + 1.0 / np.array(v_df["win_prob"]) < np.array(v_df["Winner_odds"]) ) * data["bet_amount"]
    bet_on_p2_mask = ( K + 1.0 / (1.-np.array(v_df["win_prob"])) < np.array(v_df["Loser_odds"]) ) * data["bet_amount"]
    ret = np.sum(v_df[bet_on_p1_mask > 0]["Winner_odds"] * data["bet_amount"])
    bet_amount = np.sum(bet_on_p1_mask) + np.sum(bet_on_p2_mask)
    bets_done = np.sum(bet_on_p1_mask > 0) + np.sum(bet_on_p2_mask > 0)
    if bet_amount == 0:
        return 1, 1, 1
    return bets_done, bet_amount, ret


def test_correct_predictions(data):
    '''
    Returns how many predictions were correct.

    :param data: Dataframe on which to test.
    :return: Percentage of correct prediction, those are predictions
             with probability predicted > 0.5
    '''

    return np.sum(data["win_prob"] > 0.5) / (1. * np.sum(data["win_prob"] > 0))

def test_error(data):
    '''

    :param data:
    :return:
    '''

    return np.sum(-np.log(data["win_prob"]))

def test_bias(data):
    '''

    :param data:
    :return:
    '''

    return np.sum(1.0 - data["win_prob"]) / (1.0 * np.size(data["win_prob"]))

def test_sqme(data):
    '''

    :param data:
    :return:
    '''

    return  np.sum((1.0 - data["win_prob"]) ** 2) / (1.0 * np.size(data["win_prob"]))

def analyse_ranking_model(model, report_name="report", verbose=False):
    '''
    READ BEFORE USE:
    Provides full analysis of model that uses ranking. It will work by first
    training on years from 2003 - 2011 and then test on 2012, 2013, 2014 and
    2015. One must make sure that train and test functions are implemented
    as to allow such steps to be performed.

    Model must be derived from TennisModel, so read its comments as well and
    implement accordingly.

    This function will create ready to use latex version of report. If you
    set verbose to True then you will also get results in console.

    :param model: Model one wants to analyse.
    :param report_name: Name of report. It will have timestamp appended.
    :param verbose: If True results will be printed in console as well.
    :return: void.
    '''

    bets_taken = np.zeros((4))
    betting_result = np.zeros((4))
    correct_predict = np.zeros((4))

    if verbose:
        print "Starting analysis. Loading data."

    data = dt.get_main_matches_data()

    if verbose:
        print "Training."

    df = model.test(data, verbose)
    train_error = test_error(df)
    train_bias = test_bias(df)
    train_sqme = test_sqme(df)

    train_range = [datetime.date(2003, 1, 1), datetime.date(2012, 1, 1)]
    train_data = dt.filter_data_time_range(data, train_range)
    model.train(train_data, verbose)

    if verbose:
        print "Testing:"

    for year in xrange(2012, 2016):
        if verbose:
            print "Year", year

        test_range = [datetime.date(year, 1, 1), datetime.date(year+1, 1, 1)]
        test_data = dt.filter_data_time_range(data, test_range)
        df = model.test(test_data, verbose)

        r = test_profitability(df)
        bets_taken[year-2012] = r[0]
        betting_result[year-2012] = r[2] / r[1] - 1.0
        correct_predict[year-2012] = test_correct_predictions(df)

    predict_mean = np.average(correct_predict, axis=0)
    predict_var = np.std(correct_predict, axis=0)
    h = predict_var * sp.stats.t.ppf((1+0.95)/2., 3)
    predict_conf95 = (predict_mean - h, predict_mean + h)

    profit_mean, profit_var = weighted_avg_and_std(betting_result, bets_taken)
    h = profit_var * sp.stats.t.ppf((1+0.95)/2., 3)
    profit_conf95 = (profit_mean - h, profit_mean + h)


    if verbose:
        print "Done. Printing result."
        print
        print "Model:", model.name
        print
        print "Parameters:"
        print model.params
        print
        print "Train error:", train_error
        print
        print "Train bias: ", train_bias
        print
        print "Train sqme: ", train_sqme
        print
        print
        print "Correct predict"
        print correct_predict
        print
        print "Predict mean:", predict_mean
        print
        print "Predict std:", predict_var
        print
        print
        print "Bets taken"
        print bets_taken
        print
        print "Betting results"
        print betting_result
        print
        print "ROI mean:", profit_mean
        print
        print "ROI std:", profit_var
        print
        print "95% confidence interval:", profit_conf95


    path = stg.ROOT_PATH + "/reports/" + report_name + \
            " - " + str(datetime.datetime.now()) + ".txt"

    with open(path, 'w') as f:
        f.write(r"\textbf{Model name:} ")
        f.write(model.name)
        f.write(r" \\" + " \n")
        f.write(r"\textbf{Description:} ")
        f.write(r" \\" + " \n")
        f.write(r"\textbf{Parameters:}" + r" \\")
        f.write("\n")
        f.write(r"\[ " + str(model.params).replace(r"'", "").replace(r"_", r"\_").replace("{", "").replace("}", "") + r" \] \\" + "\n")
        f.write(r"\textbf{Error:}" + " %.5f" % train_error + r" \\")
        f.write("\n")
        f.write(r"\textbf{Bias:}" + " %.5f" % train_bias + r" \\")
        f.write("\n")
        f.write(r"\textbf{Sqme:}" + " %.5f\n" % train_sqme)
        f.write(r"\\" + "\n" + r"\\ \\" + "\n")
        f.write(r"\textbf{Correct predict percentage:} \\ \\")
        f.write(latex_year_table(correct_predict))
        f.write(r" \\ \\" + "\n")
        f.write(r"\textbf{Predict mean:}" + " %.5f" % predict_mean + r" \\")
        f.write("\n")
        f.write(r"\textbf{Predict std:}" +  " %.5f" % predict_var + r" \\")
        f.write("\n")
        f.write(r"\textbf{Predict 95\% confidence interval:}" + " (%.5f, %.5f)" % predict_conf95)
        f.write("\n" + r"\\" + "\n" + r"\\ \\" + "\n")
        f.write(r"\textbf{Bets placed:}" + r" \\ \\")
        f.write(latex_year_table(bets_taken).replace(".", ""))
        f.write(r" \\ \\" + "\n")
        f.write(r"\textbf{Betting ROI:}" + r" \\ \\")
        f.write(latex_year_table(betting_result))
        f.write(r" \\ \\" + "\n")
        f.write(r"\textbf{ROI mean:}" + " %.5f" % profit_mean + r" \\" + "\n")
        f.write(r"\textbf{ROI std:}" + " %.5f" % profit_var + r" \\" + "\n")
        f.write(r"\textbf{ROI 95\% confidence interval:}" + " (%.5f, %.5f)" % profit_conf95 + r" \\" + "\n\n")





