import circle
from circle.apis.tags.management_api import ManagementApi

import unittest


class TestPing(unittest.TestCase):

    def setUp(self):
        circle.base_url = circle.Environment.SANDBOX_BASE_URL
        self.api = ManagementApi()

    def test_ping(self):
        with self.assertRaises(circle.ApiException):
            # Should error with ApiException because no API key provided
            self.api.get_account_config()

if __name__ == '__main__':
    unittest.main()
