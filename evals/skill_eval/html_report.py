"""HTML report rendering — a plain JUnit-style test report, self-contained.

Layout: a status banner + summary, a with/without comparison table, then one
section per eval (a "suite") listing its assertions as pass/fail rows. No design
system — just a clean, familiar test-report look.
"""

import html
import json
from datetime import datetime

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
table { width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 22px; }
th, td { text-align: left; padding: 7px 10px; border: 1px solid #d0d7de; }
th { background: #f6f8fa; font-weight: 600; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
.delta-good { color: #1a7f37; } .delta-bad { color: #cf222e; }
h2 { font-size: 15px; margin: 22px 0 6px; }
.suite { border: 1px solid #d0d7de; border-radius: 6px; margin-bottom: 12px; overflow: hidden; }
.suite > summary { cursor: pointer; list-style: none; padding: 10px 14px; background: #f6f8fa;
  display: flex; align-items: center; gap: 10px; }
.suite > summary::-webkit-details-marker { display: none; }
.suite .name { font-weight: 600; flex: 1; font-family: ui-monospace, Menlo, Consolas, monospace; }
.suite .sub { color: #656d76; font-size: 12px; font-weight: 400; }
.badge { font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 4px; white-space: nowrap; }
.badge.pass  { background: #dafbe1; color: #1a7f37; }
.badge.fail  { background: #ffebe9; color: #cf222e; }
.asserts { width: 100%; border-collapse: collapse; margin: 0; }
.asserts td { border: none; border-top: 1px solid #eaeef2; vertical-align: top; padding: 8px 14px; }
.asserts tr.fail { background: #fff5f5; }
.asserts .st { width: 62px; font-weight: 700; }
.asserts .st.pass { color: #1a7f37; } .asserts .st.fail { color: #cf222e; }
.asserts .ev { color: #656d76; font-size: 12px; margin-top: 3px; }
.empty { color: #656d76; font-style: italic; }
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


def _grading(iteration_dir, slug, cfg):
    """Return (passed, total, results) for one config's grading.json."""
    f = iteration_dir / f"eval-{slug}" / cfg / "grading.json"
    if not f.exists():
        return None, None, []
    try:
        g = json.loads(f.read_text())
    except (OSError, json.JSONDecodeError):
        return None, None, []
    s = g.get("summary", {})
    return s.get("passed"), s.get("total"), g.get("assertion_results", [])


def _delta_cell(delta, fmt, higher_is_better):
    if delta is None:
        return '<td class="num">—</td>'
    if delta == 0:
        return '<td class="num">0</td>'
    good = (delta > 0) == higher_is_better
    sign = "+" if delta > 0 else ""
    return f'<td class="num {"delta-good" if good else "delta-bad"}">{sign}{fmt(delta)}</td>'


def render(skill, iteration, bench, iteration_dir):
    rs = bench.get("run_summary", {})
    ws, wo, delta = rs.get("with_skill", {}), rs.get("without_skill", {}), rs.get("delta", {})

    def mean(cfg, key):
        return (cfg.get(key) or {}).get("mean")

    # --- gather per-eval results (the with-skill run is the "test") ---
    total_pass = total_all = 0
    suites = ""
    for e in bench.get("evals", []):
        w, o = e.get("with_skill") or {}, e.get("without_skill") or {}
        slug = e.get("slug", str(e.get("id", "")))
        wp, wt, results = _grading(iteration_dir, slug, "with_skill")
        if wp is not None and wt is not None:
            total_pass += wp
            total_all += wt

        status = "pass" if (wt and wp == wt) else "fail"
        badge = "PASS" if status == "pass" else "FAIL"
        count = f"{wp}/{wt}" if wp is not None and wt is not None else "—"
        dur = (w.get("duration_ms") or 0) / 1000 if w.get("duration_ms") else None
        fired = ", ".join(w.get("invoked_skills") or []) or "—"
        sub = f"tokens {fmt_num(w.get('total_tokens'))} · {fmt_sec(dur)} · skill fired: {fired}"

        if results:
            rows = ""
            for r in results:
                p = r.get("passed")
                rows += (f'<tr class="{"pass" if p else "fail"}">'
                         f'<td class="st {"pass" if p else "fail"}">{"✓ PASS" if p else "✗ FAIL"}</td>'
                         f'<td>{esc(r.get("text", ""))}'
                         f'<div class="ev">{esc(r.get("evidence", ""))}</div></td></tr>')
            body = f'<table class="asserts">{rows}</table>'
        else:
            body = '<div class="empty" style="padding:10px 14px">no graded assertions</div>'

        suites += (
            f'<details class="suite" open>'
            f'<summary><span class="badge {status}">{badge}</span>'
            f'<span class="name">{esc(slug)} <span class="sub">({count})</span></span>'
            f'<span class="sub">{sub}</span></summary>{body}</details>')

    if not suites:
        suites = '<p class="empty">no evals in this benchmark.</p>'

    # --- overall status banner ---
    overall = "pass" if (total_all and total_pass == total_all) else "fail"
    verdict = "PASSED" if overall == "pass" else "FAILED"
    rate = f"{total_pass/total_all*100:.0f}%" if total_all else "—"
    banner = (f'<div class="banner {overall}"><span class="big">{verdict}</span>'
              f'<div class="counts">{total_pass}/{total_all} assertions passed '
              f'({rate}) across {len(bench.get("evals", []))} eval(s), with skill</div></div>')

    # --- with vs without comparison ---
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
  <div class="meta">iteration {esc(iteration)} · model <code>{esc(model)}</code> · {esc(generated)}</div>
  {banner}
  <h2>With skill vs. without</h2>
  <table>
    <thead><tr><th>Metric</th><th class="num">With skill</th>
      <th class="num">Without</th><th class="num">Δ</th></tr></thead>
    <tbody>{cmp_rows}</tbody>
  </table>
  <h2>Evals</h2>
  {suites}
</div></body></html>"""
