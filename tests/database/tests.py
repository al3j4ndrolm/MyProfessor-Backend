import os
import sys

import pytest

if __name__ == "__main__":
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    sys.exit(pytest.main([tests_dir, "-v"]))
