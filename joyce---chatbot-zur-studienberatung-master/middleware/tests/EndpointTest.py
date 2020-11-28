import json
import os
import signal
import time
import unittest
import subprocess

import redis

import main
import requests

from definitions import CONFIG_PATH, REDIS_HOST, REDIS_DB, REDIS_PORT
from webapp_middleware.cost_cap_middleware import QUERIES

class EndpointTest(unittest.TestCase):

    def testQueryEndpoint(self):
        """
        Test if the Query Endpoints responds properly to a request.
        Server is started via shell script. Make Sure to install curl and have the Environment set up.
        """
        try:
            subprocess.call(['./EndpointTest.sh'])
            request = self.send_text_query()
            self.assertTrue(len(request.content) > 2)
        except Exception as e:
            print('[-] exception occurred: {!r}'.format(e))
            assert 2 + 2 == 5, 'An error occurred'
        finally:
            self.kill_server()

    def kill_server(self):
        p = subprocess.Popen(['lsof', '-i', ':5000'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        for line in str(out).split('\\n'):
            if 'python3.6' in line:
                split_line = line.split()
                pid = int(split_line[1])
                os.kill(pid, signal.SIGKILL)

    def send_text_query(self):
        time.sleep(2)
        url = 'http://localhost:5000/query'
        payload = {'session_id': '12345', 'text': 'I have an issue'}
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        request = requests.post(url, data=payload, headers=headers)
        return request

    def testQueryEndpointBlocks(self):
        """
        Test if the query is blocked if the accumulated cost is too high
        """
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        queries = r.get(QUERIES)
        r.set(QUERIES, 5000)

        with open(CONFIG_PATH) as f:
            data = json.load(f)
            cap_reached_message = data['cap_reached_message']

        try:
            subprocess.call(['./EndpointTest.sh'])
            response = str(self.send_text_query().content)
            print(response)
            self.assertTrue(response == "b'" + cap_reached_message +"'")
        except Exception as e:
            print('[-] exception occurred: {!r}'.format(e))
            assert 2 + 2 == 5, 'An error occurred'
        finally:
            self.kill_server()
            r.set(QUERIES, queries)



