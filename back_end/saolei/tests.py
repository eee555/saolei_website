import unittest
import sys
import os
from django.conf import settings

# Get the parent directory of the current directory (my_script)
parent_dir = os.path.abspath(os.path.dirname(__file__))

# Add the parent directory to the Python path
sys.path.append(parent_dir)


class TestFlags(unittest.TestCase):
    def test_skip(self):
        self.assertFalse(settings.EMAIL_SKIP)
        self.assertFalse(settings.BAIDU_VERIFY_SKIP)
        self.assertFalse(settings.E2E_TEST)


if __name__ == "__main__":
    unittest.main()
