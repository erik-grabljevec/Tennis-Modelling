__author__ = 'riko'


import unittest

import ranking_systems as rs


class TestRating(unittest.TestCase):
    '''
    Test cases for class Rating.
    '''

    def test_get_sigma(self):
        '''
        Tests get_sigma method. It indirectly tests methods __init__ and update.

        :return: void.
        '''

        # First test.
        sigma = 350
        rating = rs.Rating(1500, sigma, 50, 1)
        self.assertEqual(rating.sigma, sigma)

        # Second test.
        rating = rs.Rating(1500, 100, 0, 20)
        rating.update(1500)
        self.assertEqual(rating.sigma, 80)

    def test_update(self):
        '''
        Tests method update.

        :return: void.
        '''

        old_rating = 1500
        new_rating = 1700
        rating = rs.Rating(old_rating, 100, 10, 1)

        rating.update(new_rating)
        self.assertEqual(rating.t, 1)
        self.assertEqual(rating.rating, new_rating)


class TestModifiedGlicko(unittest.TestCase):
    '''
    Test cases for class ModifiedGlicko.
    '''

    def cmp(self, double1, double2, eps):
        '''
        Are these two number almost the same?

        :param double1: First number in double format.
        :param double2: Second number in double format.
        :return: True if difference is smaller than eps, otherwise False.
        '''

        return abs(double1 - double2) < eps

    def test_create_rating(self):
        '''
        Tests create_rating method.

        :return: void.
        '''

        mod_glicko = rs.ModifiedGlicko(1500, 350, 100, 100, 1.0/200)
        rating = mod_glicko.create_rating()
        self.assertEqual(rating.rating, 1500)
        self.assertEqual(rating.sigma, 350)
        self.assertEqual(rating.c, 100)

    def test_impact(self):
        '''
        Tests impact method.

        :return: void.
        '''

        mod_glicko = rs.ModifiedGlicko()
        rating = mod_glicko.create_rating(1500, 300, 100, 20)
        expected_result = 0.7242332
        actual_result = mod_glicko.impact(rating)
        dif = abs(expected_result - actual_result)
        self.assertTrue(dif < 0.001)

    def test_expect(self):
        '''
        Tests expect method.

        :return: void.
        '''

        mod_glicko = rs.ModifiedGlicko()
        rating1 = mod_glicko.create_rating(1700, 300, 100, 20)
        rating2 = mod_glicko.create_rating(1500, 300, 100, 20)
        expected_result = 0.697158
        actual_result = mod_glicko.expect(rating1, rating2)
        dif = abs(expected_result - actual_result)
        self.assertTrue(dif < 0.001)

    def test_rate(self):
        '''
        Tests rate method.

        :return: void.
        '''

        mod_glicko = rs.ModifiedGlicko()
        rating1 = mod_glicko.create_rating(1700, 300, 100, 20)
        rating2 = mod_glicko.create_rating(1500, 300, 100, 20)
        result = 0.4
        rating1 = mod_glicko.rate(rating1, rating2, result)

        expected_result = 1616
        actual_result = int(rating1.rating)

        self.assertEqual(expected_result, actual_result)


if __name__ == '__main__':
    unittest.main()