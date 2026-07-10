"""Functional evaluation — run each case with & without the skill, grade, record.

Orchestration only; provider details live behind the copilot adapter
(`copilot.run_task` / `copilot.run_judge`).
"""

import shutil

from . import copilot
from .common import (DEFAULT_EXCLUDES, copy_tree_filtered, slugify,
                     snapshot_hashes, write_json)
from .grading import grade
from .workspace import prepare_workspace


def _skill_prefix(skill_name):
    """Prefix that forces the skill to fire in the with-skill run."""
    return f"Use the /{skill_name} skill for this task.\n\n"


def run_configuration(case, config_dir, work_dir, *, with_skill, skill_dir, fixture_dir,
                      files, skill_repo_root, invoke_skill, timeout, dry_run, model=None):
    """Run one (case, config) pair end-to-end; return its record dict."""
    label = "with_skill" if with_skill else "without_skill"
    print(f"  [{label}] preparing workspace")
    config_dir.mkdir(parents=True, exist_ok=True)
    prepare_workspace(work_dir, fixture_dir, files, skill_repo_root)

    # Baseline = the fixture state BEFORE the agent runs (the runner may add an
    # injected skill under a "skills" dir, which the excludes drop from the diff).
    baseline = snapshot_hashes(work_dir, DEFAULT_EXCLUDES | {"skills"})
    write_json(config_dir / "baseline.json", baseline)

    prompt = case.get("prompt", "")
    if with_skill and invoke_skill:
        prompt = _skill_prefix(skill_dir.name) + prompt
    # {PROJECT_DIR} resolves to this run's workspace root so prompts can name the
    # project location explicitly and portably.
    prompt = prompt.replace("{PROJECT_DIR}", str(work_dir))

    print(f"  [{label}] running task")
    text, stderr, rc, duration_ms, usage, invocation = copilot.run_task(
        prompt, work_dir, skill_dir=(skill_dir if with_skill else None),
        model=model, timeout=timeout, dry_run=dry_run)

    (config_dir / "transcript.txt").write_text(
        f"$ {invocation}\n\n===STDOUT===\n{text}\n\n===STDERR===\n{stderr}")
    timing = {"total_tokens": usage.total_tokens if usage else None,
              "duration_ms": duration_ms, "exit_code": rc}
    if usage:
        timing["copilot_usage"] = usage.to_dict()  # token breakdown + skills fired
    write_json(config_dir / "timing.json", timing)

    # An SDK failure is an infrastructure problem, not a skill result — grading
    # the unchanged workspace would score it as a skill failure and skew the
    # benchmark. Stop here; the error is in transcript.txt.
    if rc != 0:
        raise SystemExit(
            f"[{label}] agent run failed — see {config_dir / 'transcript.txt'}")

    outputs = config_dir / "outputs"
    if outputs.exists():
        shutil.rmtree(outputs)
    if not dry_run:
        copy_tree_filtered(work_dir, outputs, DEFAULT_EXCLUDES | {"skills"})

    print(f"  [{label}] grading")
    grading = grade(case, config_dir, model=model, timeout=timeout, dry_run=dry_run)
    return {"duration_ms": duration_ms,
            "total_tokens": usage.total_tokens if usage else None,
            "models": usage.models if usage else None,
            "invoked_skills": usage.invoked_skills if usage else None,
            "exit_code": rc,
            "pass_rate": grading.get("summary", {}).get("pass_rate")}


def evaluate(*, skill_dir, cases, fixtures_dir, repo_root, workspace, iteration_dir,
             model, timeout, invoke_skill, skip_baseline, keep_workspaces, dry_run):
    """Run every case (with/without) and return the list of per-eval records."""
    per_eval = []
    for case in cases:
        eid = case.get("id", "?")
        slug = slugify(case.get("name") or case.get("prompt", str(eid)))
        eval_dir = iteration_dir / f"eval-{slug}"
        print(f"== eval {eid}: {slug} ==")

        fixture_dir = None
        fixture_name = case.get("fixture")
        if fixture_name:
            fixture_dir = fixtures_dir / fixture_name
            if not fixture_dir.exists():
                print(f"  !! fixture '{fixture_name}' not found at {fixture_dir} — skipping")
                continue
        files = case.get("files", [])

        record = {"id": eid, "slug": slug}
        configs = [("with_skill", True)]
        if not skip_baseline:
            configs.append(("without_skill", False))

        for label, with_skill in configs:
            work_dir = workspace / ".runs" / f"{eid}-{label}"
            record[label] = run_configuration(
                case, eval_dir / label, work_dir,
                with_skill=with_skill, skill_dir=skill_dir, fixture_dir=fixture_dir,
                files=files, skill_repo_root=repo_root, invoke_skill=invoke_skill,
                timeout=timeout, dry_run=dry_run, model=model)
            if not keep_workspaces and work_dir.exists():
                shutil.rmtree(work_dir, ignore_errors=True)
        per_eval.append(record)
        print()
    return per_eval
