#!/usr/bin/env python3
"""Render a skill's eval results to an HTML dashboard (thin entry point).

Implementation in skill_eval/html_report.py.

    python3 evals/report.py --skill axon-ivy-cms
    python3 evals/report.py --skill axon-ivy-cms --iteration 2 --open
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skill_eval.cli import report_main  # noqa: E402

if __name__ == "__main__":
    report_main()
