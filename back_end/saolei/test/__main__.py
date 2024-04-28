import sys
import os

# Get the parent directory of the current directory (my_script)
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the parent directory to the Python path
sys.path.append(parent_dir)

from config.flags import *

def main():
    print(EMAIL_SKIP)
    assert EMAIL_SKIP == False
    assert BAIDU_VERIFY_SKIP == False
    assert DESIGNATOR_SKIP == False

if __name__ == "__main__":
    main()