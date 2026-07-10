#!/usr/bin/env python3
"""Functional skill evaluation on GitHub Copilot (thin entry point).

Runs each case in a skill's evals/evals.json with & without the skill (via the
github-copilot-sdk), grades the outputs with an LLM judge, and aggregates a
benchmark. Implementation lives in the skill_eval package.

Needs github-copilot-sdk (Python 3.11+) in this interpreter — see evals/README.md.

    python3 evals/evaluate.py --skill axon-ivy-cms
    python3 evals/evaluate.py --skill axon-ivy-cms --eval-id 0 --dry-run
"""

import importlib.util
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

# Convenience: if this interpreter lacks the SDK but a repo-local .venv has it,
# transparently re-exec with that interpreter (so plain `python3 evals/evaluate.py`
# works). The env sentinel prevents an infinite loop if the .venv also lacks the SDK
# — a realpath check fails here because a venv python is a symlink to the base one.
if importlib.util.find_spec("copilot") is None and not os.environ.get("_SKILL_EVAL_REEXEC"):
    _repo = os.path.dirname(_HERE)
    for _cand in (os.path.join(_repo, ".venv", "bin", "python"),
                  os.path.join(_HERE, ".venv", "bin", "python")):
        if os.path.exists(_cand):
            os.environ["_SKILL_EVAL_REEXEC"] = "1"
            os.execv(_cand, [_cand, os.path.abspath(__file__), *sys.argv[1:]])

from skill_eval.cli import run_main  # noqa: E402

if __name__ == "__main__":
    run_main()
