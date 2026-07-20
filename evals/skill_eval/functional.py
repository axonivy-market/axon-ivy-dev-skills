import shutil
import tempfile
from pathlib import Path

from . import container
from .common import (DEFAULT_EXCLUDES, copy_tree_filtered, eval_dir_name,
                     slugify, snapshot_hashes, write_json)
from .grading import grade
from .workspace import prepare_workspace


def _skill_prefix(skill_name):
    return f"Use the /{skill_name} skill for this task.\n\n"


def _build_prompt(case, work_dir, *, force_prefix, skill_name):
    prompt = case.get("prompt", "")

    if force_prefix and case.get("should_trigger") is None:
        prompt = _skill_prefix(skill_name) + prompt
    return prompt.replace("{PROJECT_DIR}", str(work_dir))


def _write_run_artifacts(config_dir, task_result):
    (config_dir / "transcript.txt").write_text(
        f"$ {task_result.invocation}\n\n===STDOUT===\n{task_result.text}\n\n===STDERR===\n{task_result.stderr}")
    timing = {
        "total_tokens": task_result.usage.total_tokens if task_result.usage else None,
        "duration_ms": task_result.duration_ms,
        "exit_code": task_result.returncode,
    }
    if task_result.usage:
        timing["copilot_usage"] = task_result.usage.to_dict()  # token breakdown + skills fired
    write_json(config_dir / "timing.json", timing)


def _trigger_assertions(case, *, usage, skill_name):
    if case.get("should_trigger") is None:
        return []
    expected = bool(case["should_trigger"])
    fired = bool(usage and skill_name in (usage.invoked_skills or []))
    return [{
        "text": (f"Skill '{skill_name}' triggers naturally for this prompt"
                 if expected else
                 f"Skill '{skill_name}' stays quiet for this prompt (negative control)"),
        "passed": fired == expected,
        "evidence": f"invoked_skills={usage.invoked_skills if usage else []}; expected_fire={expected}",
    }]


def run_configuration(case, config_dir, work_dir, *, label, load_dirs, skill_dir,
                      invoke_skill, fixture_dir, files, skill_repo_root, timeout,
                      model=None, provider=container):

    skill_loaded = bool(load_dirs)

    print(f"  [{label}] preparing workspace")
    config_dir.mkdir(parents=True, exist_ok=True)
    prepare_workspace(work_dir, fixture_dir, files, skill_repo_root)

    baseline = snapshot_hashes(work_dir, DEFAULT_EXCLUDES | {"skills"})
    write_json(config_dir / "baseline.json", baseline)

    prompt = _build_prompt(
        case, work_dir, force_prefix=skill_loaded and invoke_skill,
        skill_name=skill_dir.name)

    print(f"  [{label}] running task")
    task_result = provider.run_task(
        prompt, work_dir, skill_dirs=load_dirs, model=model, timeout=timeout)
    _write_run_artifacts(config_dir, task_result)

    if task_result.returncode != 0:
        raise SystemExit(
            f"[{label}] agent run failed — see {config_dir / 'transcript.txt'}")

    outputs = config_dir / "outputs"
    if outputs.exists():
        shutil.rmtree(outputs)
    copy_tree_filtered(work_dir, outputs, DEFAULT_EXCLUDES | {"skills"})

    extra_results = _trigger_assertions(
        case, usage=task_result.usage, skill_name=skill_dir.name)

    print(f"  [{label}] grading")
    grading = grade(case, config_dir, model=model, timeout=timeout,
                    extra_results=extra_results, provider=provider)
    return {"duration_ms": task_result.duration_ms,
            "total_tokens": task_result.usage.total_tokens if task_result.usage else None,
            "models": task_result.usage.models if task_result.usage else None,
            "invoked_skills": task_result.usage.invoked_skills if task_result.usage else None,
            "exit_code": task_result.returncode,
            "pass_rate": grading.get("summary", {}).get("pass_rate")}


def _configs(skill_dir, dep_skill_dirs, baseline_dir):
    with_run = ("with_skill", [skill_dir, *dep_skill_dirs])
    if baseline_dir:
        baseline_run = ("with_previous_version", [baseline_dir, *dep_skill_dirs])
    else:
        baseline_run = ("without_skill", [])
    return with_run, baseline_run


def evaluate(*, skill_dir, cases, fixtures_dir, repo_root, iteration_dir,
             model, timeout, invoke_skill,
             provider=container, dep_skill_dirs=(),
             baseline_dir=None):

    configs = _configs(skill_dir, dep_skill_dirs, baseline_dir)

    runs_root = Path(tempfile.mkdtemp(prefix=f"skill-eval-{skill_dir.name}-"))
    print(f"Run dirs:   {runs_root} (outside the repo, so runs can't read the skills)")
    try:
        return _evaluate_cases(
            runs_root, skill_dir=skill_dir, cases=cases, fixtures_dir=fixtures_dir,
            repo_root=repo_root, iteration_dir=iteration_dir, model=model,
            timeout=timeout, invoke_skill=invoke_skill, provider=provider,
            configs=configs)
    finally:
        shutil.rmtree(runs_root, ignore_errors=True)


def _evaluate_cases(runs_root, *, skill_dir, cases, fixtures_dir, repo_root,
                    iteration_dir, model, timeout, invoke_skill, provider, configs):
    with_run, baseline_run = configs
    per_eval = []
    for case in cases:
        eid = case.get("id", "?")
        slug = slugify(case.get("name") or case.get("prompt", str(eid)))
        eval_dir = iteration_dir / eval_dir_name(eid, slug)
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

        for label, load_dirs in [with_run, baseline_run]:
            work_dir = runs_root / f"{eid}-{label}"
            record[label] = run_configuration(
                case, eval_dir / label, work_dir,
                label=label, load_dirs=load_dirs, skill_dir=skill_dir,
                invoke_skill=invoke_skill, fixture_dir=fixture_dir,
                files=files, skill_repo_root=repo_root,
                timeout=timeout, model=model, provider=provider)
            if work_dir.exists():
                shutil.rmtree(work_dir, ignore_errors=True)
        per_eval.append(record)
        print()
    return per_eval
