"""skill_eval — evaluation toolkit for agent skills on GitHub Copilot (official SDK).

Modules, by concern (mirrors the layered layout of a typical eval framework):

  infrastructure : common (paths/IO/fs), schemas (Usage dataclass)
  execution      : copilot (the provider adapter — build/run/token-capture)
  measurement    : workspace, grading, functional
  presentation   : benchmark (aggregate), html_report (dashboard)
  entry point    : cli (run / report subcommands)

The top-level evals/evaluate.py and evals/report.py are thin shims into cli so
existing commands keep working.
"""

__version__ = "0.1.0"
