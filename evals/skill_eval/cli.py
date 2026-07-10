"""Command-line entry points: `run` (functional eval) and `report`.

The top-level evals/evaluate.py and evals/report.py call the corresponding
*_main here; `python3 -m skill_eval <sub>` works too.
"""

import argparse
import re
import sys
import webbrowser
from pathlib import Path

from . import benchmark, common, functional, html_report


# ---------------------------------------------------------------------------
# run — functional evaluation
# ---------------------------------------------------------------------------

def run_main(argv=None):
    ap = argparse.ArgumentParser(prog="skill_eval run",
                                 description="Copilot skill evaluation harness")
    ap.add_argument("--skill", required=True,
                    help="skill directory name or path (must contain evals/evals.json)")
    ap.add_argument("--repo-root", default=None)
    ap.add_argument("--fixtures-dir", default=None,
                    help="fixture snapshots dir (default: <repo>/evals/fixtures)")
    ap.add_argument("--workspace", default=None,
                    help="workspace output dir (default: <skill>-workspace)")
    ap.add_argument("--iteration", type=int, default=1)
    ap.add_argument("--eval-id", default=None, help="run only this eval id")
    ap.add_argument("--model", default="claude-sonnet-5",
                    help="model to pin for reproducibility (default claude-sonnet-5; "
                         "'auto' or '' for the SDK default)")
    ap.add_argument("--timeout", type=int, default=common.DEFAULT_TIMEOUT)
    ap.add_argument("--no-invoke-skill", dest="invoke_skill", action="store_false",
                    help="don't force the skill to fire; test natural triggering")
    ap.add_argument("--skip-baseline", action="store_true",
                    help="run only with_skill (skip the baseline)")
    ap.add_argument("--keep-workspaces", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the plan without calling the model")
    args = ap.parse_args(argv)

    repo_root = common.resolve_repo_root(args.repo_root)
    skill_dir = common.resolve_skill_dir(repo_root, args.skill)
    if not skill_dir.exists():
        sys.exit(f"skill dir not found: {skill_dir}")

    evals_file = skill_dir / "evals" / "evals.json"
    if not evals_file.exists():
        sys.exit(f"no evals.json at {evals_file}\n"
                 f"Create it first (see evals/README.md for the schema).")
    cases = common.read_json(evals_file).get("evals", [])
    if args.eval_id is not None:
        cases = [c for c in cases if str(c.get("id")) == str(args.eval_id)]
        if not cases:
            sys.exit(f"no eval with id={args.eval_id}")

    fixtures_dir = (Path(args.fixtures_dir).resolve() if args.fixtures_dir
                    else common.default_fixtures_dir(repo_root))
    workspace = common.resolve_workspace(skill_dir, args.workspace)
    iteration_dir = workspace / f"iteration-{args.iteration}"
    iteration_dir.mkdir(parents=True, exist_ok=True)

    print(f"Skill:      {skill_dir.name}")
    print(f"Evals:      {len(cases)} case(s) from {evals_file}")
    print(f"Fixtures:   {fixtures_dir}")
    print(f"Workspace:  {iteration_dir}")
    print(f"Model:      {args.model or '(SDK default)'}")
    print(f"Invoke skill in with_skill run: {args.invoke_skill}")
    print()

    per_eval = functional.evaluate(
        skill_dir=skill_dir, cases=cases, fixtures_dir=fixtures_dir, repo_root=repo_root,
        workspace=workspace, iteration_dir=iteration_dir, model=(args.model or None),
        timeout=args.timeout, invoke_skill=args.invoke_skill,
        skip_baseline=args.skip_baseline, keep_workspaces=args.keep_workspaces,
        dry_run=args.dry_run)

    if not args.dry_run:
        bm = benchmark.aggregate(per_eval, iteration_dir, model_pinned=(args.model or None))
        benchmark.write_feedback_stub(per_eval, iteration_dir)
        rs = bm["run_summary"]
        d = rs["delta"]
        print("== benchmark ==")
        print(f"  pass_rate    with={rs['with_skill']['pass_rate']['mean']} "
              f"without={rs['without_skill']['pass_rate']['mean']} delta={d['pass_rate']}")
        print(f"  time_seconds delta={d['time_seconds']}")
        print(f"  tokens       with={rs['with_skill']['tokens']['mean']} "
              f"without={rs['without_skill']['tokens']['mean']} delta={d['tokens']}")
        print(f"\nWrote {iteration_dir / 'benchmark.json'}")
        print(f"Human review: fill in {iteration_dir / 'feedback.json'}")


# ---------------------------------------------------------------------------
# report — HTML dashboard
# ---------------------------------------------------------------------------

def report_main(argv=None):
    ap = argparse.ArgumentParser(prog="skill_eval report",
                                 description="Render eval results to an HTML dashboard")
    ap.add_argument("--skill", required=True, help="skill dir name or path")
    ap.add_argument("--repo-root", default=None)
    ap.add_argument("--workspace", default=None)
    ap.add_argument("--iteration", type=int, default=None,
                    help="iteration number (default: latest present)")
    ap.add_argument("--output", default=None, help="output HTML path")
    ap.add_argument("--open", action="store_true", help="open the report in a browser")
    args = ap.parse_args(argv)

    repo_root = common.resolve_repo_root(args.repo_root)
    skill_dir = common.resolve_skill_dir(repo_root, args.skill)
    workspace = common.resolve_workspace(skill_dir, args.workspace)
    if not workspace.exists():
        sys.exit(f"no workspace at {workspace} — run the eval first")

    if args.iteration is not None:
        iteration_dir = workspace / f"iteration-{args.iteration}"
    else:
        iters = sorted(workspace.glob("iteration-*"),
                       key=lambda p: int(re.sub(r"\D", "", p.name) or 0))
        if not iters:
            sys.exit(f"no iteration-N dirs under {workspace}")
        iteration_dir = iters[-1]

    bench_file = iteration_dir / "benchmark.json"
    if not bench_file.exists():
        sys.exit(f"no benchmark.json in {iteration_dir}")
    bench = common.read_json(bench_file)
    iteration = re.sub(r"\D", "", iteration_dir.name) or "?"

    out = Path(args.output).resolve() if args.output else iteration_dir / "report.html"
    out.write_text(html_report.render(skill_dir.name, iteration, bench, iteration_dir))
    print(f"Wrote {out}")
    if args.open:
        webbrowser.open(out.as_uri())


# ---------------------------------------------------------------------------
# unified dispatcher
# ---------------------------------------------------------------------------

def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    subs = {"run": run_main, "report": report_main}
    if not argv or argv[0] not in subs:
        sys.exit(f"usage: skill_eval {{{'|'.join(subs)}}} [options]")
    subs[argv[0]](argv[1:])


if __name__ == "__main__":
    main()
