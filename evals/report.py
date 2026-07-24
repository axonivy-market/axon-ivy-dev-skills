#!/usr/bin/env python3

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skill_eval.cli import report_main  # noqa: E402

if __name__ == "__main__":
    report_main()
