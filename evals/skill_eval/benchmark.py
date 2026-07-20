import json
import statistics

from .common import eval_dir_name, write_json


def _delta(a, b):
    if a is None or b is None:
        return None
    return round(a - b, 4)


def aggregate(per_eval, iteration_dir, model_pinned=None,
              baseline_config="without_skill", comparison=None):
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

    configs = ("with_skill", baseline_config)
    summary = {}
    for config in configs:
        summary[config] = {
            "pass_rate": summ(values(config, lambda c: c.get("pass_rate"))),
            "time_seconds": summ(values(config, lambda c: (c["duration_ms"] / 1000)
                                        if c.get("duration_ms") is not None else None)),
            "tokens": summ(values(config, lambda c: c.get("total_tokens"))),
        }
    ws, base = summary["with_skill"], summary[baseline_config]
    summary["delta"] = {
        "pass_rate": _delta(ws["pass_rate"]["mean"], base["pass_rate"]["mean"]),
        "time_seconds": _delta(ws["time_seconds"]["mean"], base["time_seconds"]["mean"]),
        "tokens": _delta(ws["tokens"]["mean"], base["tokens"]["mean"]),
    }
    # Record the model for reproducibility: what we pinned + what actually ran.
    observed = sorted({m for e in per_eval for cfg in configs
                       if e.get(cfg) and e[cfg].get("models") for m in e[cfg]["models"]})
    benchmark = {"model_pinned": model_pinned, "models_observed": observed,
                 "baseline_config": baseline_config,
                 "run_summary": summary, "evals": per_eval}
    if comparison is not None:
        benchmark["comparison"] = comparison
    write_json(iteration_dir / "benchmark.json", benchmark)
    return benchmark


def write_feedback_stub(per_eval, iteration_dir):
    path = iteration_dir / "feedback.json"
    existing = {}
    if path.exists():
        try:
            existing = json.loads(path.read_text())
        except json.JSONDecodeError:
            existing = {}
    feedback = {eval_dir_name(e["id"], e["slug"]): existing.get(eval_dir_name(e["id"], e["slug"]), "")
                for e in per_eval}
    write_json(path, feedback)
