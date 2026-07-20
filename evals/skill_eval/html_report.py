import html
import json
from datetime import datetime

from .common import eval_dir_name

CSS = """
* { box-sizing: border-box; }
body { margin: 0; background: #fff; color: #1f2328;
  font-family: system-ui, -apple-system, "Segoe UI", Arial, sans-serif;
  font-size: 14px; line-height: 1.5; }
.wrap { max-width: 900px; margin: 0 auto; padding: 24px 20px 64px; }
h1 { font-size: 20px; margin: 0 0 2px; }
.meta { color: #656d76; font-size: 13px; margin-bottom: 18px; }
.meta code { background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 4px; padding: 0 5px; }
.banner { border-radius: 6px; padding: 12px 16px; margin-bottom: 18px; font-weight: 600;
  border: 1px solid; }
.banner .big { font-size: 16px; }
.banner.pass  { background: #dafbe1; border-color: #97e3ad; color: #1a7f37; }
.banner.fail  { background: #ffebe9; border-color: #ffcecb; color: #cf222e; }
.banner .counts { font-weight: 400; color: #1f2328; font-size: 13px; margin-top: 4px; }
h2 { font-size: 15px; margin: 22px 0 6px; }
h2 .caption { font-weight: 400; color: #656d76; font-size: 12px; margin-left: 6px; }
table { width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 22px; }
th, td { text-align: left; padding: 7px 10px; border: 1px solid #d0d7de; }
th { background: #f6f8fa; font-weight: 600; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
.delta-good { color: #1a7f37; } .delta-bad { color: #cf222e; }
.bench { border: 2px solid #d0d7de; border-radius: 6px; overflow: hidden; margin-bottom: 4px; }
.bench table { margin: 0; }
.suite { border: 1px solid #d0d7de; border-radius: 6px; margin-bottom: 12px; overflow: hidden; }
.suite > summary { cursor: pointer; list-style: none; padding: 10px 14px; background: #f6f8fa;
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.suite > summary::-webkit-details-marker { display: none; }
.suite .name { font-weight: 600; font-family: ui-monospace, Menlo, Consolas, monospace; }
.suite .spacer { flex: 1; }
.suite .sub { color: #656d76; font-size: 12px; font-weight: 400; }
.badge { font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 4px; white-space: nowrap; }
.badge.pass  { background: #dafbe1; color: #1a7f37; }
.badge.fail  { background: #ffebe9; color: #cf222e; }
.badge.na    { background: #eaeef2; color: #656d76; }
.config { border-top: 1px solid #d0d7de; }
.config-head { display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
  padding: 9px 14px; background: #fbfcfd; border-bottom: 1px solid #eaeef2; }
.config-head .label { font-weight: 600; }
.config-head .sub { color: #656d76; font-size: 12px; font-weight: 400; }
.asserts { width: 100%; border-collapse: collapse; margin: 0; font-size: 13px; }
.asserts td { border: none; border-top: 1px solid #eaeef2; vertical-align: top; padding: 8px 14px; }
.asserts tr:first-child td { border-top: none; }
.asserts tr.fail { background: #fff5f5; }
.asserts .st { width: 62px; font-weight: 700; }
.asserts .st.pass { color: #1a7f37; } .asserts .st.fail { color: #cf222e; }
.asserts .ev { color: #656d76; font-size: 12px; margin-top: 3px; white-space: pre-wrap; }
.empty { color: #656d76; font-style: italic; }
.tx { border-top: 1px solid #eaeef2; }
.tx > summary { cursor: pointer; list-style: none; padding: 8px 14px; color: #656d76;
  font-size: 12px; font-weight: 600; }
.tx > summary::-webkit-details-marker { display: none; }
.tx > summary::before { content: "▸ "; }
.tx[open] > summary::before { content: "▾ "; }
pre.transcript { margin: 0; padding: 12px 14px; background: #0d1117; color: #d1d9e0;
  font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 12px; line-height: 1.5;
  max-height: 460px; overflow: auto; white-space: pre-wrap; word-break: break-word; }
"""


def esc(x):
    return html.escape(str(x))


def fmt_pct(v):
    return "—" if v is None else f"{v * 100:.0f}%"


def fmt_num(v):
    if v is None:
        return "—"
    return f"{v/1000:.0f}K" if v >= 1000 else str(int(v))


def fmt_sec(v):
    return "—" if v is None else f"{v:,.0f}s"


def _grading(iteration_dir, eid, slug, cfg):
    """Return (passed, total, results) for one config's grading.json."""
    f = iteration_dir / eval_dir_name(eid, slug) / cfg / "grading.json"
    if not f.exists():
        return None, None, []
    try:
        g = json.loads(f.read_text())
    except (OSError, json.JSONDecodeError):
        return None, None, []
    s = g.get("summary", {})
    return s.get("passed"), s.get("total"), g.get("assertion_results", [])


def _transcript(iteration_dir, eid, slug, cfg):
    """Return the raw transcript text for one config, or None if absent."""
    f = iteration_dir / eval_dir_name(eid, slug) / cfg / "transcript.txt"
    if not f.exists():
        return None
    try:
        return f.read_text()
    except OSError:
        return None


def _delta_cell(delta, fmt, higher_is_better):
    if delta is None:
        return '<td class="num">—</td>'
    if delta == 0:
        return '<td class="num">0</td>'
    good = (delta > 0) == higher_is_better
    sign = "+" if delta > 0 else ""
    return f'<td class="num {"delta-good" if good else "delta-bad"}">{sign}{fmt(delta)}</td>'


def _assert_table(results):
    """Render one config's graded assertions as a pass/fail table."""
    if not results:
        return '<div class="empty" style="padding:10px 14px">no graded assertions</div>'
    rows = ""
    for r in results:
        p = r.get("passed")
        rows += (f'<tr class="{"pass" if p else "fail"}">'
                 f'<td class="st {"pass" if p else "fail"}">{"✓ PASS" if p else "✗ FAIL"}</td>'
                 f'<td>{esc(r.get("text", ""))}'
                 f'<div class="ev">{esc(r.get("evidence", ""))}</div></td></tr>')
    return f'<table class="asserts">{rows}</table>'


def _config_panel(label, rec, passed, total, results, transcript):
    """Render one run (with_skill or without_skill) inside a suite."""
    if total is None:
        status, badge = "na", "N/A"
    elif total and passed == total:
        status, badge = "pass", "PASS"
    else:
        status, badge = "fail", "FAIL"
    count = f"{passed}/{total}" if passed is not None and total is not None else "—"

    dur = (rec.get("duration_ms") or 0) / 1000 if rec.get("duration_ms") else None
    fired = ", ".join(rec.get("invoked_skills") or []) or "—"
    sub = (f"{count} passed · tokens {fmt_num(rec.get('total_tokens'))} · "
           f"{fmt_sec(dur)} · skill fired: {esc(fired)}")

    tx = ""
    if transcript is not None:
        tx = (f'<details class="tx"><summary>Transcript</summary>'
              f'<pre class="transcript">{esc(transcript)}</pre></details>')

    return (
        f'<div class="config">'
        f'<div class="config-head"><span class="badge {status}">{badge}</span>'
        f'<span class="label">{esc(label)}</span>'
        f'<span class="sub">{sub}</span></div>'
        f'{_assert_table(results)}{tx}</div>')


def _baseline_labels(bench):
    baseline_config = bench.get("baseline_config", "without_skill")
    if baseline_config == "without_skill":
        return baseline_config, "Without", "Without skill", "without"
    desc = (bench.get("comparison") or {}).get("baseline_desc")
    label = f"Old version ({esc(desc)})" if desc else "Old version"
    return baseline_config, label, label, "old"


def render(skill, bench, iteration_dir):
    rs = bench.get("run_summary", {})
    baseline_config, base_col, base_panel, base_sub = _baseline_labels(bench)
    ws, wo, delta = rs.get("with_skill", {}), rs.get(baseline_config, {}), rs.get("delta", {})

    def mean(cfg, key):
        return (cfg.get(key) or {}).get("mean")

    # --- gather per-eval results (both configs) ---
    total_pass = total_all = 0
    suites = ""
    for e in bench.get("evals", []):
        eid = e.get("id", "?")
        slug = e.get("slug", str(eid))
        w, o = e.get("with_skill") or {}, e.get(baseline_config) or {}

        wp, wt, wresults = _grading(iteration_dir, eid, slug, "with_skill")
        op, ot, oresults = _grading(iteration_dir, eid, slug, baseline_config)
        if wp is not None and wt is not None:
            total_pass += wp
            total_all += wt

        def _status(passed, total):
            if total is None:
                return "na", "N/A", "—"
            label = "PASS" if (total and passed == total) else "FAIL"
            return label.lower(), label, f"{passed}/{total}"

        wcls, wbadge, wcount = _status(wp, wt)
        ocls, obadge, ocount = _status(op, ot)

        panels = _config_panel("With skill", w, wp, wt, wresults,
                               _transcript(iteration_dir, eid, slug, "with_skill"))
        # Only render the baseline panel if it was actually run.
        if o or ot is not None:
            panels += _config_panel(base_panel, o, op, ot, oresults,
                                    _transcript(iteration_dir, eid, slug, baseline_config))

        suites += (
            f'<details class="suite" open>'
            f'<summary>'
            f'<span class="name">{esc(eid)}: {esc(slug)}</span>'
            f'<span class="spacer"></span>'
            f'<span class="sub">with</span><span class="badge {wcls}">{wbadge} {wcount}</span>'
            f'<span class="sub">{base_sub}</span><span class="badge {ocls}">{obadge} {ocount}</span>'
            f'</summary>{panels}</details>')

    if not suites:
        suites = '<p class="empty">no evals in this benchmark.</p>'

    # --- overall status banner (with-skill run is the graded "test") ---
    overall = "pass" if (total_all and total_pass == total_all) else "fail"
    verdict = "PASSED" if overall == "pass" else "FAILED"
    rate = f"{total_pass/total_all*100:.0f}%" if total_all else "—"
    n_evals = len(bench.get("evals", []))
    banner = (f'<div class="banner {overall}"><span class="big">{verdict}</span>'
              f'<div class="counts">{total_pass}/{total_all} assertions passed '
              f'({rate}) across {n_evals} eval(s), with skill</div></div>')

    # --- final benchmark: aggregate with vs. without ---
    cmp_rows = "".join([
        f'<tr><td>Pass rate</td><td class="num">{fmt_pct(mean(ws,"pass_rate"))}</td>'
        f'<td class="num">{fmt_pct(mean(wo,"pass_rate"))}</td>'
        f'{_delta_cell(delta.get("pass_rate"), fmt_pct, True)}</tr>',
        f'<tr><td>Tokens / run</td><td class="num">{fmt_num(mean(ws,"tokens"))}</td>'
        f'<td class="num">{fmt_num(mean(wo,"tokens"))}</td>'
        f'{_delta_cell(delta.get("tokens"), fmt_num, False)}</tr>',
        f'<tr><td>Time / run</td><td class="num">{fmt_sec(mean(ws,"time_seconds"))}</td>'
        f'<td class="num">{fmt_sec(mean(wo,"time_seconds"))}</td>'
        f'{_delta_cell(delta.get("time_seconds"), fmt_sec, False)}</tr>',
    ])

    model = bench.get("model_pinned") or "(unpinned)"
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(skill)} · eval report</title><style>{CSS}</style></head><body>
<div class="wrap">
  <h1>{esc(skill)} — evaluation report</h1>
  <div class="meta">model <code>{esc(model)}</code> · {esc(generated)}</div>
  {banner}
  <h2>Final benchmark result<span class="caption">aggregate across all {n_evals} eval(s) — with skill vs. {base_panel.lower()}</span></h2>
  <div class="bench">
  <table>
    <thead><tr><th>Metric</th><th class="num">With skill</th>
      <th class="num">{base_col}</th><th class="num">Δ</th></tr></thead>
    <tbody>{cmp_rows}</tbody>
  </table>
  </div>
  <h2>Detailed results<span class="caption">every eval — with-skill and without-skill runs, assertions &amp; transcripts</span></h2>
  {suites}
</div></body></html>"""


def _delta_md(delta, fmt):
    if delta is None:
        return "—"
    if delta == 0:
        return "0"
    sign = "+" if delta > 0 else ""
    return f"{sign}{fmt(delta)}"


def render_summary_markdown(skill, bench):
    rs = bench.get("run_summary", {})
    baseline_config, base_col, _, _ = _baseline_labels(bench)
    ws, base, delta = rs.get("with_skill", {}), rs.get(baseline_config, {}), rs.get("delta", {})

    def mean(cfg, key):
        return (cfg.get(key) or {}).get("mean")

    rows = (("Pass rate", "pass_rate", fmt_pct),
            ("Tokens / run", "tokens", fmt_num),
            ("Time / run", "time_seconds", fmt_sec))

    lines = [
        f"# Skill eval: `{skill}`",
        "",
        f"With skill vs **{base_col}** · model `{bench.get('model_pinned') or '(unpinned)'}`",
        "",
        f"| Metric | With skill | {base_col} | Δ |",
        "|---|---:|---:|---:|",
    ]
    for label, key, fmt in rows:
        lines.append(f"| {label} | {fmt(mean(ws, key))} | {fmt(mean(base, key))} "
                     f"| {_delta_md(delta.get(key), fmt)} |")
    lines += ["", "Per-eval detail, transcripts and gradings are in the run artifact "
                  "(report.html); the efficiency advisory is in the Quality gate section below."]
    return "\n".join(lines)
