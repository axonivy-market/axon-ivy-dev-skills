import argparse
import sys

from . import baseline as baseline_git
from . import benchmark, common, functional, gate, html_report


def _resolve_latest_iteration_dir(workspace):
    iters = sorted(
        workspace.glob("iteration-*"),
        key=lambda p: int(p.name.split("-")[-1]) if p.name.split("-")[-1].isdigit() else 0,
    )
    if not iters:
        sys.exit(f"no iteration-N dirs under {workspace}")
    return iters[-1]


def _build_comparison(*, baseline_dir, baseline_desc):
    return {"mode": "previous-version",
            "baseline_desc": baseline_desc,
            "baseline_path": str(baseline_dir)}


def run_main(argv=None):
    ap = argparse.ArgumentParser(prog="skill_eval run",
                                 description="Copilot skill evaluation harness")
    ap.add_argument("--skill", required=True,
                    help="skill directory name or path (must contain evals/evals.json)")
    ap.add_argument("--model", default="mai-code-1-flash-picker",
                    help="model to use for task and judge runs "
                         "(default: mai-code-1-flash-picker)")
    ap.add_argument("--baseline", choices=("without-skill", "previous-version"),
                    default="without-skill")
    args = ap.parse_args(argv)

    model = args.model
    timeout = common.DEFAULT_TIMEOUT

    repo_root = common.resolve_repo_root(None)
    skill_dir = common.resolve_skill_dir(repo_root, args.skill)
    if not skill_dir.exists():
        sys.exit(f"skill dir not found: {skill_dir}")

    baseline_dir = None
    baseline_desc = None
    baseline_config = "without_skill"
    comparison = None
    cleanup_baseline = None
    if args.baseline == "previous-version":
        try:
            skill_rel = skill_dir.relative_to(repo_root)
        except ValueError:
            skill_rel = None
        resolved = (baseline_git.resolve_previous_version(repo_root, skill_rel)
                   if skill_rel else None)
        if resolved:
            baseline_dir, baseline_desc, cleanup_baseline = resolved
            baseline_config = "with_previous_version"
            comparison = _build_comparison(
                baseline_dir=baseline_dir, baseline_desc=baseline_desc)
        else:
            print("warning: no previous version of this skill on the default "
                  "branch (brand-new skill) — falling back to the "
                  "without-skill baseline.", file=sys.stderr)

    try:
        evals_file = skill_dir / "evals" / "evals.json"
        if not evals_file.exists():
            sys.exit(f"no evals.json at {evals_file}\n"
                     f"Create it first (see evals/EVALUATION.md for the schema).")
        evals_data = common.read_json(evals_file)
        cases = evals_data.get("evals", [])

        dep_skill_dirs = []
        for dep in evals_data.get("depends_on", []):
            dep_dir = common.resolve_skill_dir(repo_root, dep)
            if not dep_dir.exists():
                sys.exit(f"depends_on skill not found: '{dep}' (resolved to {dep_dir})")
            dep_skill_dirs.append(dep_dir)

        fixtures_dir = common.default_fixtures_dir(repo_root)
        workspace = common.resolve_workspace(skill_dir, None)
        iteration_dir = workspace / "iteration-1"
        iteration_dir.mkdir(parents=True, exist_ok=True)

        if baseline_config == "with_previous_version":
            baseline_line = f"previous version at {baseline_dir} ({baseline_desc})"
        else:
            baseline_line = "no skill loaded (classic baseline)"

        dep_note = ("co-loaded on both sides" if baseline_config == "with_previous_version"
                    else "co-loaded in the with-skill run")
        print(f"Skill:      {skill_dir.name}")
        print(f"Depends on: {', '.join(d.name for d in dep_skill_dirs) or '(none)'} — {dep_note}")
        print(f"Evals:      {len(cases)} case(s) from {evals_file}")
        print(f"Fixtures:   {fixtures_dir}")
        print(f"Workspace:  {iteration_dir}")
        print(f"Model:      {model}")
        print(f"Baseline:   {baseline_config} — {baseline_line}")
        print("Invoke skill in with_skill run: True")
        from . import container as provider
        provider.preflight()
        print(f"Isolation:  docker container ({provider.IMAGE}) — the official runner")
        print()

        per_eval = functional.evaluate(
            skill_dir=skill_dir, cases=cases, fixtures_dir=fixtures_dir, repo_root=repo_root,
            iteration_dir=iteration_dir, model=model,
            timeout=timeout, invoke_skill=True,
            provider=provider, dep_skill_dirs=dep_skill_dirs,
            baseline_dir=baseline_dir)

        bm = benchmark.aggregate(per_eval, iteration_dir, model_pinned=model,
                                 baseline_config=baseline_config, comparison=comparison)
        benchmark.write_feedback_stub(per_eval, iteration_dir)
        rs = bm["run_summary"]
        d = rs["delta"]
        base = rs[baseline_config]
        print("== benchmark ==")
        print(f"  baseline     {baseline_config}")
        print(f"  pass_rate    with={rs['with_skill']['pass_rate']['mean']} "
              f"baseline={base['pass_rate']['mean']} delta={d['pass_rate']}")
        print(f"  time_seconds delta={d['time_seconds']}")
        print(f"  tokens       with={rs['with_skill']['tokens']['mean']} "
              f"baseline={base['tokens']['mean']} delta={d['tokens']}")
        print(f"\nWrote {iteration_dir / 'benchmark.json'}")
        print(f"Human review: fill in {iteration_dir / 'feedback.json'}")
    finally:
        if cleanup_baseline:
            cleanup_baseline()


def report_main(argv=None):
    ap = argparse.ArgumentParser(prog="skill_eval report",
                                 description="Render eval results to an HTML dashboard")
    ap.add_argument("--skill", required=True, help="skill dir name or path")
    args = ap.parse_args(argv)

    repo_root = common.resolve_repo_root(None)
    skill_dir = common.resolve_skill_dir(repo_root, args.skill)
    workspace = common.resolve_workspace(skill_dir, None)
    if not workspace.exists():
        sys.exit(f"no workspace at {workspace} — run the eval first")

    iteration_dir = _resolve_latest_iteration_dir(workspace)

    bench_file = iteration_dir / "benchmark.json"
    if not bench_file.exists():
        sys.exit(f"no benchmark.json in {iteration_dir}")
    bench = common.read_json(bench_file)

    out = iteration_dir / "report.html"
    out.write_text(html_report.render(skill_dir.name, bench, iteration_dir))
    print(f"Wrote {out}")


def summary_main(argv=None):
    ap = argparse.ArgumentParser(prog="skill_eval summary",
                                 description="Print the run-summary markdown "
                                             "(for a CI step summary or a terminal)")
    ap.add_argument("--skill", required=True, help="skill dir name or path")
    args = ap.parse_args(argv)

    repo_root = common.resolve_repo_root(None)
    skill_dir = common.resolve_skill_dir(repo_root, args.skill)
    workspace = common.resolve_workspace(skill_dir, None)
    if not workspace.exists():
        sys.exit(f"no workspace at {workspace} — run the eval first")

    iteration_dir = _resolve_latest_iteration_dir(workspace)
    bench_file = iteration_dir / "benchmark.json"
    if not bench_file.exists():
        sys.exit(f"no benchmark.json in {iteration_dir}")
    bench = common.read_json(bench_file)

    print(html_report.render_summary_markdown(skill_dir.name, bench))


def gate_main(argv=None):
    ap = argparse.ArgumentParser(prog="skill_eval gate",
                                 description="Publish quality gate — exits non-zero if the "
                                             "skill's latest benchmark isn't good enough to ship")
    ap.add_argument("--skill", required=True, help="skill dir name or path")
    args = ap.parse_args(argv)

    min_efficiency = 0.10

    repo_root = common.resolve_repo_root(None)
    skill_dir = common.resolve_skill_dir(repo_root, args.skill)
    workspace = common.resolve_workspace(skill_dir, None)
    if not workspace.exists():
        sys.exit(f"no workspace at {workspace} — run the eval first")
    iteration_dir = _resolve_latest_iteration_dir(workspace)
    bench_file = iteration_dir / "benchmark.json"
    if not bench_file.exists():
        sys.exit(f"no benchmark.json in {iteration_dir} — run the eval first")

    bench = common.read_json(bench_file)
    results, passed = gate.check(bench, min_efficiency=min_efficiency)

    print(f"Quality gate: {skill_dir.name}\n")
    for r in results:
        if r.get("advisory"):
            marker = "ℹ️"
            suffix = "  (advisory)"
        else:
            marker = "✅" if r["passed"] else "❌"
            suffix = ""
        print(f"  {marker} {r['gate']:12} {r['value']}{suffix}")
    print(f"\n{'✅ PASS — publishable' if passed else '❌ FAIL — not publishable'}")
    sys.exit(0 if passed else 1)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    subs = {"run": run_main, "report": report_main, "gate": gate_main,
            "summary": summary_main}
    if not argv or argv[0] not in subs:
        sys.exit(f"usage: skill_eval {{{'|'.join(subs)}}} [options]")
    subs[argv[0]](argv[1:])


if __name__ == "__main__":
    main()
