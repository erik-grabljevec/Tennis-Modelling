__author__ = 'riko'


import unittest

import ranking_systems as rs


class TestElo(unittest.TestCase):
    '''
    Test cases for class ModifiedGlicko.
    '''

    def test_all(self):
        '''
        This funtion implicitly tests whole ranking system.

        :return: void.
        '''

        elo = rs.Elo(2400, 32)
        r1 = elo.create_rating()
        r2 = elo.create_rating(2000)

        r1, r2 = elo.match(r1, r2, 1.0)

        self.assertTrue(abs(r1.rating - 2402.9090) < 0.001)
        self.assertTrue(abs(r2.rating - 1997.0909) < 0.001)


if __name__ == '__main__':
    unittest.main()


