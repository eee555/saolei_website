import unittest

from django.conf import settings


class TestFlags(unittest.TestCase):
    def test_skip(self):
        self.assertFalse(settings.EMAIL_SKIP)
        self.assertFalse(settings.BAIDU_VERIFY_SKIP)
        self.assertFalse(settings.E2E_TEST)
