'''
Collection of functions that calculate expected match probabilities,
durations, distributions etc.
It is implemented as effectively as possible using numpy and cython.
Inspired by Stratagem idd_point.pyx
'''
# cython: profile=True
# cython: wraparound=False
# cython: boundscheck=False
# cython: cdivision=True
# cython: nonecheck=False


__author__ = 'riko'

import random

import numpy as np

cimport numpy as np
cimport cython

DTYPE = np.int
ctypedef np.int_t DTYPE_t


################################################################################
#     Sub-functions.                                                           #
################################################################################


cdef double prob_win_game(double p):
    '''
    Probability of player winning game.

    :param p: Probability of player winning point.
    :return: Probability of player winning game from 0 to 1
    '''

    cdef double den = 1 - 2 * p * (1 - p)
    return p**4 * ( 15 - 4 * p - (10 * p**2)/den )


def _prob_win_game(double p):
    '''
    Probability of player winning game.

    :param p: Probability of player winning point.
    :return: Probability of player winning game from 0 to 1
    '''

    cdef double den = 1 - 2 * p * (1 - p)
    return p**4 * ( 15 - 4 * p - (10 * p**2)/den )


cdef two_adventage(double p, double q):
    '''
    Probability for winning tiebreak from 6-6

    :param p: Probability of the player1 winning serve point
    :param q: Probability of the player2 winning serve point
    :return: Probability for winning tiebreak from 6-6
    '''

    cdef double nom = p * (1.0 - q)
    cdef double den = 1.0 - (p * q + (1.0 - p) * (1.0 - q))
    return nom / den


@cython.boundscheck(False)
cdef prob_win_tiebreaker(double p, double q):
    '''
    Probability of winning tiebreaker (when set is 6-6)

    :param p: Probability of player1 winning serve point
    :param q: Probability of player2 winning serve point
    :return: Probability of player1 winning the tiebreaker.
    '''

    cdef np.ndarray[DTYPE_t, ndim=2] A = np.array([
                                                [1, 3, 0, 4, 0, 0],
                                                [3, 3, 1, 4, 0, 0],
                                                [4, 4, 0, 3, 1, 0],
                                                [6, 3, 2, 4, 0, 0],
                                                [16, 4, 1, 3, 1, 0],
                                                [6, 5, 0, 2, 2, 0],
                                                [10, 2, 3, 5, 0, 0],
                                                [40, 3, 2, 4, 1, 0],
                                                [30, 4, 1, 3, 2, 0],
                                                [4, 5, 0, 2, 3, 0],
                                                [5, 1, 4, 6, 0, 0],
                                                [50, 2, 3, 5, 1, 0],
                                                [100, 3, 2, 4, 2, 0],
                                                [50, 4, 1, 3, 3, 0],
                                                [5, 5, 0, 2, 4, 0],
                                                [1, 1, 5, 6, 0, 0],
                                                [30, 2, 4, 5, 1, 0],
                                                [150, 3, 3, 4, 2, 0],
                                                [200, 4, 2, 3, 3, 0],
                                                [75, 5, 1, 2, 4, 0],
                                                [6, 6, 0, 1, 5, 0],
                                                [1, 0, 6, 6, 0, 1],
                                                [36, 1, 5, 5, 1, 1],
                                                [225, 2, 4, 4, 2, 1],
                                                [400, 3, 3, 3, 3, 1],
                                                [225, 4, 2, 2, 4, 1],
                                                [36, 5, 1, 1, 5, 1],
                                                [1, 6, 0, 0, 6, 1]
                                                    ], dtype=DTYPE)

    cdef double d = two_adventage(p, q)
    cdef Py_ssize_t i;
    cdef double result = 0.

    with nogil:
        for i in xrange(28):
            result += A[i, 0]*p**A[i, 1]*(1.-p)**A[i, 2]*(1.-q)**A[i, 3]*(q)**A[i, 4]*d**A[i, 5]

    return result


@cython.boundscheck(False)
def _prob_win_tiebreaker(double p, double q):
    '''
    Probability of winning tiebreaker (when set is 6-6)

    :param p: Probability of player1 winning serve point
    :param q: Probability of player2 winning serve point
    :return: Probability of player1 winning the tiebreaker.
    '''

    cdef np.ndarray[DTYPE_t, ndim=2] A = np.array([
        [1, 3, 0, 4, 0, 0],
        [3, 3, 1, 4, 0, 0],
        [4, 4, 0, 3, 1, 0],
        [6, 3, 2, 4, 0, 0],
        [16, 4, 1, 3, 1, 0],
        [6, 5, 0, 2, 2, 0],
        [10, 2, 3, 5, 0, 0],
        [40, 3, 2, 4, 1, 0],
        [30, 4, 1, 3, 2, 0],
        [4, 5, 0, 2, 3, 0],
        [5, 1, 4, 6, 0, 0],
        [50, 2, 3, 5, 1, 0],
        [100, 3, 2, 4, 2, 0],
        [50, 4, 1, 3, 3, 0],
        [5, 5, 0, 2, 4, 0],
        [1, 1, 5, 6, 0, 0],
        [30, 2, 4, 5, 1, 0],
        [150, 3, 3, 4, 2, 0],
        [200, 4, 2, 3, 3, 0],
        [75, 5, 1, 2, 4, 0],
        [6, 6, 0, 1, 5, 0],
        [1, 0, 6, 6, 0, 1],
        [36, 1, 5, 5, 1, 1],
        [225, 2, 4, 4, 2, 1],
        [400, 3, 3, 3, 3, 1],
        [225, 4, 2, 2, 4, 1],
        [36, 5, 1, 1, 5, 1],
        [1, 6, 0, 0, 6, 1]
    ], dtype=DTYPE)

    cdef double d = two_adventage(p, q)
    cdef Py_ssize_t i;
    cdef double result = 0.

    with nogil:
        for i in xrange(28):
            result += A[i, 0]*p**A[i, 1]*(1.-p)**A[i, 2]*(1.-q)**A[i, 3]*(q)**A[i, 4]*d**A[i, 5]

    return result


@cython.boundscheck(False)
cdef double prob_win_set(double p, double q):
    '''
    Probability of winning set.

    :param p: Probability of player1 winning serve point.
    :param q: Probability of player2 winning serve point.
    :return: Probability of player1 winning the set.
    '''

    cdef np.ndarray[DTYPE_t, ndim=2] G = np.array([
                                                [1, 3, 0, 3, 0, 0],
                                                [3, 3, 1, 3, 0, 0],
                                                [3, 4, 0, 2, 1, 0],
                                                [6, 2, 2, 4, 0, 0],
                                                [12, 3, 1, 3, 1, 0],
                                                [3, 4, 0, 2, 2, 0],
                                                [4, 2, 3, 4, 0, 0],
                                                [24, 3, 2, 3, 1, 0],
                                                [24, 4, 1, 2, 2, 0],
                                                [4, 5, 0, 1, 3, 0],
                                                [5, 1, 4, 5, 0, 0],
                                                [40, 2, 3, 4, 1, 0],
                                                [60, 3, 2, 3, 2, 0],
                                                [20, 4, 1, 2, 3, 0],
                                                [1, 5, 0, 1, 4, 0],
                                                [1, 0, 5, 5, 0, 1],
                                                [25, 1, 4, 4, 1, 1],
                                                [100, 2, 3, 3, 2, 1],
                                                [100, 3, 2, 2, 3, 1],
                                                [25, 4, 1, 1, 4, 1],
                                                [1, 5, 0, 0, 5, 1]
                                                    ], dtype=DTYPE)

    cdef double gp = prob_win_game(p)
    cdef double gq = prob_win_game(q)
    cdef double tb = prob_win_tiebreaker(p, q)
    cdef double gt = gp * (1 - gq) + tb * ( gp * gq + (1 - gp) * (1 - gq) )

    cdef Py_ssize_t i

    cdef double total = 0.
    with nogil:
        for i in xrange(21):
            total += G[i, 0]*gp**G[i, 1]*(1-gp)**G[i, 2]*(1-gq)**G[i, 3]*gq**G[i, 4]*gt**G[i,5]

    return total


@cython.boundscheck(False)
def _prob_win_set(double p, double q):
    '''
    Probability of winning set.

    :param p: Probability of player1 winning serve point.
    :param q: Probability of player2 winning serve point.
    :return: Probability of player1 winning the set.
    '''

    cdef np.ndarray[DTYPE_t, ndim=2] G = np.array([
        [1, 3, 0, 3, 0, 0],
        [3, 3, 1, 3, 0, 0],
        [3, 4, 0, 2, 1, 0],
        [6, 2, 2, 4, 0, 0],
        [12, 3, 1, 3, 1, 0],
        [3, 4, 0, 2, 2, 0],
        [4, 2, 3, 4, 0, 0],
        [24, 3, 2, 3, 1, 0],
        [24, 4, 1, 2, 2, 0],
        [4, 5, 0, 1, 3, 0],
        [5, 1, 4, 5, 0, 0],
        [40, 2, 3, 4, 1, 0],
        [60, 3, 2, 3, 2, 0],
        [20, 4, 1, 2, 3, 0],
        [1, 5, 0, 1, 4, 0],
        [1, 0, 5, 5, 0, 1],
        [25, 1, 4, 4, 1, 1],
        [100, 2, 3, 3, 2, 1],
        [100, 3, 2, 2, 3, 1],
        [25, 4, 1, 1, 4, 1],
        [1, 5, 0, 0, 5, 1]
    ], dtype=DTYPE)

    cdef double gp = prob_win_game(p)
    cdef double gq = prob_win_game(q)
    cdef double tb = prob_win_tiebreaker(p, q)
    cdef double gt = gp * (1 - gq) + tb * ( gp * gq + (1 - gp) * (1 - gq) )

    cdef Py_ssize_t i

    cdef double total = 0.
    with nogil:
        for i in xrange(21):
            total += G[i, 0]*gp**G[i, 1]*(1-gp)**G[i, 2]*(1-gq)**G[i, 3]*gq**G[i, 4]*gt**G[i,5]

    return total


@cython.boundscheck(False)
cdef int sim_game(double p):
    '''
    Simulate game.

    :param p: Probability of player 1 winning on serve.
    :return: Hashed info on result and points played.
    '''

    cdef double r
    cdef int a = 0
    cdef int b = 0

    while (a<4 and b<4) or abs(a-b)<2:
        r = random.random()
        if r < p: a += 1
        else: b += 1

    return 1000*(a>b)+a+b


@cython.boundscheck(False)
cdef sim_tiebreaker(double p, double q):
    '''
    Simulate tiebreaker.

    :param p: Probability of player 1 winning on serve.
    :param q: Probability of player 2 winning on serve.
    :return: Hashed info on result and points played.
    '''

    cdef double r
    cdef int a = 0
    cdef int b = 0

    while (a<7 and b<7) or abs(a-b)<2:
        r = random.random()
        if ((a+b+1)/2)%2==0:
            if r<p: a += 1
            else: b += 1
        else:
            if r<q: b += 1
            else: a += 1

    return 1000*(a>b)+a+b


@cython.boundscheck(False)
cdef int sim_set(double p, double q):
    '''
    Simulate set.

    :param p: Probability of player 1 winning on serve.
    :param q: Probability of player 2 winning on serve.
    :return: Hashed info on result and points played.
    '''

    cdef int temp
    cdef int a = 0
    cdef int b = 0
    cdef int s = 0
    cdef int r, result

    while a <= 6 and b <= 6:
        if (a==6 or b==6) and abs(a-b)>=2:
            break

        if a == b == 6:
            temp = sim_tiebreaker(p, q)
        else:
            temp = sim_game(p) if (a+b)%2==0 else sim_game(1.0 - q)

        result, serve = temp/1000, temp%1000
        s += serve
        r = 1 if result else 0
        a += r
        b += (1 - r)

    return 1000*(a>b)+s


@cython.boundscheck(False)
cdef int sim_match(double p, double q, int best_of):
    '''
    Simulate match.

    :param p: Probability of player 1 winning on serve.
    :param q: Probability of player 2 winning on serve.
    :param best_of: How many sets are played.
    :return: Hashed info on result and points played.
    '''

    cdef int win_result = (best_of + 1) / 2
    cdef int a = 0
    cdef int b = 0
    cdef int s = 0
    cdef int result, serve

    while a < win_result and b < win_result:
        temp = sim_set(p, q)
        result, serve = temp/1000, temp%1000
        s += serve
        r = 1 if result else 0
        a += r
        b += (1 - r)

    return 1000*(a>b)+s


################################################################################
#     Externally called functions.                                             #
################################################################################


@cython.boundscheck(False)
def prob_win_match(double p, double q, best_of=3):
    '''
    Probability of winning a match.

    :param p: Probability of player1 winning serve point.
    :param q: Probability of player2 winning serve point.
    :param best_of: On how many sets is match decided.
    :return: Probability of player1 winning the match.
    '''

    cdef double s = prob_win_set(p, q)

    if best_of == 3:
        return s**2 * (1 + 2 * (1-s))
    elif best_of == 5:
        return s**3 * (1 + 3 * (1-s) + 6 * (1-s)**2)


@cython.boundscheck(False)
def monte_carlo_match(double p, double q, int best_of=3, int N=100000):
    '''
    Make monte carlo simulation that calculates expected result and number
    of points played (this can be used to estimate length of match).

    :param p: Probability of player 1 winning on serve.
    :param q: Probability of player 2 winning on serve.
    :param best_of: How many sets are played.
    :param N: How many runs of MC shall we do.
    :return: (result, serve), expected result and number of points played.
    '''

    r = [sim_match(p, q, best_of) for i in xrange(N)]
    result = 1.0 * sum(map(lambda x: x/1000, r)) / N
    serve = 1.0 * sum(map(lambda x: x%1000, r)) / N
    return result, serve


@cython.boundscheck(False)
def monte_carlo_points_list(double p, double q, int best_of=3, int N=10000):
    '''
    Make monte carlo simulation that calculates expected result and number
    of points played (this can be used to estimate length of match).

    :param p: Probability of player 1 winning on serve.
    :param q: Probability of player 2 winning on serve.
    :param best_of: How many sets are played.
    :param N: How many runs of MC shall we do.
    :return: (result, serve), list of results and list of poinst played
    '''

    r = [sim_match(p, q, best_of) for i in xrange(N)]
    serve = map(lambda x: x%1000, r)
    return serve


@cython.boundscheck(False)
def smooth_time_series_exp(np.ndarray[np.float64_t, ndim=1] input, float alpha):
    '''
    Smooths time series with an exponent smoothing.

    :param alpha: Smoothing value.
    :return: Smoothed time series.
    '''

    n_array = np.copy(input)
    n = input.size
    for i in xrange(1, n):
        n_array[i] = (1.0 - alpha) * n_array[i - 1] + alpha * n_array[i]
    return n_array


@cython.boundscheck(False)
def smooth_time_series_mov(np.ndarray[np.float64_t, ndim=1] input, int k):
    '''
    Smooths time series with a running average.

    :param k: How many elements do we average.
    :return: Smoothed time series.
    '''

    n_array = np.copy(input)
    n = input.size
    sum = 0.0
    for i in xrange(n):
        sum += input[i]
        if i>=k: sum -= input[i - k]
        n_array[i] = sum / (i+1 if i<k else k)
    return n_array