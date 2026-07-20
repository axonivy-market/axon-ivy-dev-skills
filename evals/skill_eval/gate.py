PASS_RATE_FLOOR = 0.9999  # == 100%, modulo the 4-decimal rounding in benchmark.json


def _reduction(with_mean, baseline_mean):
    if with_mean is None or not baseline_mean:
        return None
    return (baseline_mean - with_mean) / baseline_mean


def check(benchmark, *, min_efficiency, token_axis="tokens"):
    rs = benchmark.get("run_summary", {})
    baseline_config = benchmark.get("baseline_config", "without_skill")
    ws, base = rs.get("with_skill", {}), rs.get(baseline_config, {})
    results = []

    pr = (ws.get("pass_rate") or {}).get("mean")
    failing = [e.get("slug", e.get("id"))
               for e in benchmark.get("evals", [])
               if ((e.get("with_skill") or {}).get("pass_rate")) is not None
               and (e["with_skill"]["pass_rate"]) < PASS_RATE_FLOOR]
    g1 = pr is not None and pr >= PASS_RATE_FLOOR and not failing
    if pr is None:
        value = "no assertions"
    elif g1:
        value = f"{pr:.0%} passed"
    else:
        value = f"{pr:.0%} passed ({', '.join(map(str, failing))})" if failing else f"{pr:.0%} passed"
    results.append({"gate": "correctness", "passed": g1, "advisory": False, "value": value})

    ws_tok = (ws.get(token_axis) or {}).get("mean")
    base_tok = (base.get(token_axis) or {}).get("mean")
    reduction = _reduction(ws_tok, base_tok)
    against = "previous version" if baseline_config == "with_previous_version" else "no-skill baseline"
    if reduction is None:
        value = "no baseline tokens to compare"
    else:
        warn = "  ⚠ skill uses more tokens" if reduction < 0 else ""
        met = "" if reduction >= min_efficiency else f" (below {min_efficiency:.0%} target)"
        value = f"tokens {-reduction:+.0%} vs {against}{met}{warn}"
    results.append({"gate": "efficiency", "passed": True, "advisory": True, "value": value})

    passed = all(r["passed"] for r in results if not r.get("advisory"))
    return results, passed
