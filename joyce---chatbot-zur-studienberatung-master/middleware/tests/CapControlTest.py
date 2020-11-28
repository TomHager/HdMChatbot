import unittest
from unittest.mock import Mock, MagicMock
import redis
import time

from webapp_middleware.cost_cap_middleware import PATH_INFO, ACCUMULATED_COST, START_TIME
from webapp_middleware import cost_cap_middleware
from webapp_middleware.cost_cap_middleware import CostCapMiddleware
from datetime import date, timedelta
from flask import Flask

environ_dict = {PATH_INFO: '/query'}


def getitem(name):
    return environ_dict[name]


class CapControlTest(unittest.TestCase):

    def setUp(self):
        self.logger_middleware = CostCapMiddleware(Flask(__name__), Flask(__name__))
        self.logger_middleware.redis = redis.Redis(host='localhost', port=6379, db=1)
        self.logger_middleware.load_config_options()
        self.logger_middleware.initialize_time_field()

    def tearDown(self):
        self.logger_middleware.redis.flushdb()
        pass

    def testMonthHasEnded(self):
        a_month_ago_millis = self.get_time_from_a_month_ago()
        self.logger_middleware.redis.set(cost_cap_middleware.START_TIME, a_month_ago_millis)

        self.assertTrue(self.logger_middleware.month_has_ended())

    def get_time_from_a_month_ago(self):
        a_month_ago = date.today() - timedelta(days=31)
        a_month_ago_millis = int(time.mktime(a_month_ago.timetuple()))
        return a_month_ago_millis

    def testValuesAreResetted(self):
        environ = MagicMock()
        environ.__getitem__.side_effect = getitem
        self.logger_middleware.call(environ)

        self.logger_middleware.redis.set(START_TIME, self.get_time_from_a_month_ago())

        self.logger_middleware.call(environ)

        accumulated_cost = float(self.logger_middleware.redis.get(ACCUMULATED_COST))
        self.assertEqual(accumulated_cost, 0)