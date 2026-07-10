"""Aggregation & analysis artifacts — benchmark.json and the feedback.json stub."""

import json
import statistics

from .common import write_json


def _delta(a, b):
    if a is None or b is None:
        return None
    return round(a - b, 4)


def aggregate(per_eval, iteration_dir, model_pinned=None):
    """Write benchmark.json in the agentskills.io shape: per-config
    pass_rate / time_seconds / tokens (mean+stddev) plus a with−without delta."""
    def summ(vals):
        if not vals:
            return {"mean": None, "stddev": None}
        return {"mean": round(statistics.mean(vals), 4),
                "stddev": round(statistics.pstdev(vals), 4) if len(vals) > 1 else 0.0}

    def values(config, extract):
        out = []
        for e in per_eval:
            c = e.get(config)
            if not c:
                continue
            v = extract(c)
            if v is not None:
                out.append(v)
        return out

    summary = {}
    for config in ("with_skill", "without_skill"):
        summary[config] = {
            "pass_rate": summ(values(config, lambda c: c.get("pass_rate"))),
            "time_seconds": summ(values(config, lambda c: (c["duration_ms"] / 1000)
                                        if c.get("duration_ms") is not None else None)),
            "tokens": summ(values(config, lambda c: c.get("total_tokens"))),
        }
    ws, wo = summary["with_skill"], summary["without_skill"]
    summary["delta"] = {
        "pass_rate": _delta(ws["pass_rate"]["mean"], wo["pass_rate"]["mean"]),
        "time_seconds": _delta(ws["time_seconds"]["mean"], wo["time_seconds"]["mean"]),
        "tokens": _delta(ws["tokens"]["mean"], wo["tokens"]["mean"]),
    }
    # Record the model for reproducibility: what we pinned + what actually ran.
    observed = sorted({m for e in per_eval for cfg in ("with_skill", "without_skill")
                       if e.get(cfg) and e[cfg].get("models") for m in e[cfg]["models"]})
    benchmark = {"model_pinned": model_pinned, "models_observed": observed,
                 "run_summary": summary, "evals": per_eval}
    write_json(iteration_dir / "benchmark.json", benchmark)
    return benchmark


def write_feedback_stub(per_eval, iteration_dir):
    """Emit the guideline's feedback.json for the human-review step, keyed by eval
    dir name. Never overwrite existing human-entered feedback."""
    path = iteration_dir / "feedback.json"
    existing = {}
    if path.exists():
        try:
            existing = json.loads(path.read_text())
        except json.JSONDecodeError:
            existing = {}
    feedback = {f"eval-{e['slug']}": existing.get(f"eval-{e['slug']}", "")
                for e in per_eval}
    write_json(path, feedback)
