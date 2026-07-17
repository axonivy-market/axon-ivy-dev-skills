PASS_RATE_FLOOR = 0.9999  # == 100%, modulo the 4-decimal rounding in benchmark.json
BLOWUP_NOTE_FACTOR = 2.0  # note (don't fail) a waived gate if tokens double or more


def _reduction(with_mean, without_mean):
    if with_mean is None or not without_mean:
        return None
    return (without_mean - with_mean) / without_mean


def check(benchmark, *, min_efficiency, token_axis="tokens"):
    rs = benchmark.get("run_summary", {})
    ws, wo = rs.get("with_skill", {}), rs.get("without_skill", {})
    results = []

    # Gate 1 — correctness: 100% with-skill pass rate, no case left behind.
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
    results.append({"gate": "correctness", "passed": g1, "value": value})

    # Gate 2 — efficiency: tokens, waived if the baseline couldn't already do the
    # task (then the skill's value is the correctness gap it closed, not tokens).
    # If baseline stats are missing, we cannot evaluate efficiency.
    wo_pr = (wo.get("pass_rate") or {}).get("mean")
    ws_tok, wo_tok = (ws.get(token_axis) or {}).get("mean"), (wo.get(token_axis) or {}).get("mean")
    reduction = _reduction(ws_tok, wo_tok)

    if wo_pr is None or wo_tok is None:
        g2, value = False, "no baseline"
    elif wo_pr < PASS_RATE_FLOOR:
        g2 = True
        value = f"waived — baseline only {wo_pr:.0%} correct without the skill"
        if reduction is not None and ws_tok is not None and ws_tok >= wo_tok * BLOWUP_NOTE_FACTOR:
            value += f" (note: tokens {-reduction:+.0%} vs baseline — review before shipping)"
    else:
        g2 = reduction is not None and reduction >= min_efficiency
        value = f"tokens {-reduction:+.0%}" if reduction is not None else "no baseline"
    results.append({"gate": "efficiency", "passed": g2, "value": value})

    return results, all(r["passed"] for r in results)
