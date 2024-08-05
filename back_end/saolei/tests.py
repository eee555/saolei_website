import unittest

import sys
import os

# Get the parent directory of the current directory (my_script)
parent_dir = os.path.abspath(os.path.dirname(__file__))

# Add the parent directory to the Python path
sys.path.append(parent_dir)

from config.flags import *

class TestFlags(unittest.TestCase):
    def test_skip(self):
        self.assertFalse(EMAIL_SKIP)
        self.assertFalse(BAIDU_VERIFY_SKIP)

if __name__ == "__main__":
    unittest.main()