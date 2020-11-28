import logging
import time
import redis
import json
import datetime
from definitions import CONFIG_PATH, REDIS_HOST, REDIS_PORT, REDIS_DB
from datetime import date

ACCUMULATED_COST = 'accumulated_cost'

QUERIES = 'queries'

PATH_INFO = 'PATH_INFO'

PER_TEXT_REQUEST = 'cost_per_text_request'

START_TIME = 'start_time'


class CostCapMiddleware(object):
    """
    Monthly Cost Cap
    """
    def __init__(self, app, wsgi_app):
        self.wsgi_app = wsgi_app
        self.app = app
        logger = logging.getLogger('cost_cap_middleware')
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler('middleware.log')
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)
        self.redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        self.load_config_options()
        self.initialize_time_field()
        self.reset_values_if_month_has_ended()

        if self.redis.get('%s' % QUERIES) is None:
            self.redis.set(QUERIES, 0)

    def reset_values_if_month_has_ended(self):
        if self.month_has_ended():
            self.redis.set(ACCUMULATED_COST, 0)
            self.redis.set(START_TIME, int(time.mktime(date.today().timetuple())))
            self.redis.set(QUERIES, 0)
            self.app.logger.info(" [-] Month has ended, accumulated cost resetted")

    def initialize_time_field(self):
        if self.redis.get('%s' % START_TIME) is None:
            self.redis.set(START_TIME, int(round(time.time())))
            self.app.logger.info(" [-] time field initialized")

    def load_config_options(self):
        with open(CONFIG_PATH) as f:
            data = json.load(f)
            self.cost_per_text_request = float(data[('%s' % PER_TEXT_REQUEST)])

    def month_has_ended(self):
        """
        Calculates the difference between
        :return:
        """
        start_time_millis = int(self.redis.get(START_TIME))
        start = datetime.datetime.fromtimestamp(start_time_millis)
        now = datetime.datetime.now()
        diff = now - start
        logging.info(" * Days passed since last reset: {}".format(diff.days))
        return diff.days > 30

    def __call__(self, environ, start_response):
        self.call(environ)
        return self.wsgi_app(environ, start_response)

    def call(self, environ):
        """
            Listens to the /query Endpoint and increments the request count with each request.
            Calculates the accumulated cost with every request that is made to that specific endpoint.
            """
        self.app.logger.info("[-] Request to {}".format(environ[('%s' % PATH_INFO)]))
        if environ[PATH_INFO] == '/query':
            self.redis.incr('%s' % QUERIES)
            self.redis.set(ACCUMULATED_COST, int(self.redis.get(QUERIES)) * self.cost_per_text_request)

        self.reset_values_if_month_has_ended()
        self.app.logger.info("[-] Accumulated Cost: ${}".format(self.redis.get('%s' % ACCUMULATED_COST)))
