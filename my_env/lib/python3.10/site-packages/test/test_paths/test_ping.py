import circle
from circle.apis.tags.health_api import HealthApi

import unittest


class TestPing(unittest.TestCase):

    def setUp(self):
        circle.base_url = circle.Environment.SANDBOX_BASE_URL
        self.api = HealthApi()

    def test_ping(self):
        resp = self.api.ping()
        self.assertEquals(resp.body['message'], 'pong')


if __name__ == '__main__':
    unittest.main()
