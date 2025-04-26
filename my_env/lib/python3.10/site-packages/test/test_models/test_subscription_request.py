import circle
from circle.model.subscription_request import SubscriptionRequest

import unittest


class TestPing(unittest.TestCase):

    def test_create(self):
        model = SubscriptionRequest(
            endpoint='https://example.org/test-create-sub-req'
        )
        self.assertEquals(model['endpoint'], 'https://example.org/test-create-sub-req')

    def test_empty(self):
        with self.assertRaises(TypeError):
            # Shoudl error with TypeError because required constructor params not provided
            SubscriptionRequest()

if __name__ == '__main__':
    unittest.main()
