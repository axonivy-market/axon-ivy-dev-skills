"""LLM-as-judge grading — score a run's changed files against the case assertions.

Uses Copilot itself as the judge — a separate SDK session with no skills loaded.
"""

import json

from . import copilot
from .common import (DEFAULT_EXCLUDES, MAX_BUNDLE_BYTES, MAX_FILE_BYTES,
                     collect_changed_files, read_json, write_json)


def build_grading_prompt(case, changed_files):
    bundle_parts, used = [], 0
    truncated_files = 0
    for rel, text in changed_files:
        blob = text
        if len(blob.encode("utf-8", "ignore")) > MAX_FILE_BYTES:
            blob = blob.encode("utf-8", "ignore")[:MAX_FILE_BYTES].decode("utf-8", "ignore")
            blob += "\n…[truncated]…"
            truncated_files += 1
        section = f"\n----- FILE: {rel} -----\n{blob}\n"
        if used + len(section.encode("utf-8", "ignore")) > MAX_BUNDLE_BYTES:
            bundle_parts.append("\n…[additional changed files omitted for size]…\n")
            break
        bundle_parts.append(section)
        used += len(section.encode("utf-8", "ignore"))

    bundle = "".join(bundle_parts) if bundle_parts else "(no files were created or modified)"
    assertions = case.get("assertions", [])
    numbered = "\n".join(f"{i+1}. {a}" for i, a in enumerate(assertions))

    prompt = f"""You are grading the output of an AI coding agent that worked on an Axon Ivy project task. Judge ONLY from the files below — do not assume anything you cannot see.

TASK GIVEN TO THE AGENT:
{case.get('prompt', '')}

WHAT SUCCESS LOOKS LIKE (human description):
{case.get('expected_output', '')}

FILES THE AGENT CREATED OR MODIFIED:
{bundle}

ASSERTIONS — evaluate each as PASS or FAIL. Require concrete evidence for a PASS (quote or reference the files); do NOT give the benefit of the doubt. A label without substance is a FAIL.
{numbered}

Respond with ONLY a JSON object, no markdown fences, no prose, exactly this shape:
{{"assertion_results":[{{"text":"<the assertion>","passed":true,"evidence":"<quote or file reference>"}}]}}
"""
    return prompt, truncated_files


def extract_json(text):
    """Pull the grading JSON object out of an LLM response.

    The judge often prefixes prose (which may contain stray braces like
    `{PROJECT_DIR}`) and its `evidence` strings can contain `{...}` dict reprs, so
    we can't just balance-count braces. Instead we try `raw_decode` (string-aware)
    from every `{` and return the first object that parses — preferring one that
    has `assertion_results`.
    """
    dec = json.JSONDecoder()
    fallback = None
    for i, ch in enumerate(text):
        if ch != "{":
            continue
        try:
            obj, _ = dec.raw_decode(text, i)
        except ValueError:  # JSONDecodeError subclasses ValueError
            continue
        if isinstance(obj, dict):
            if "assertion_results" in obj:
                return obj
            if fallback is None:
                fallback = obj
    return fallback


def grade(case, config_dir, *, model, timeout, dry_run):
    """Grade config_dir/outputs against the case assertions; write grading.json."""
    assertions = case.get("assertions", [])
    if not assertions:
        grading = {"assertion_results": [], "summary": {"passed": 0, "failed": 0,
                   "total": 0, "pass_rate": None}, "note": "no assertions defined"}
        write_json(config_dir / "grading.json", grading)
        return grading

    baseline = read_json(config_dir / "baseline.json")
    changed = collect_changed_files(config_dir / "outputs", baseline, DEFAULT_EXCLUDES)
    prompt, truncated = build_grading_prompt(case, changed)

    if dry_run:
        print(f"    DRY-RUN grade: {len(assertions)} assertions over {len(changed)} changed files")
        return {"assertion_results": [], "summary": {}}

    stdout, rc = copilot.run_judge(prompt, config_dir, model=model, timeout=timeout,
                                   dry_run=False)
    if rc != 0:
        raise SystemExit(f"judge run failed for {config_dir}: {stdout}")
    parsed = extract_json(stdout)

    # An unparseable judge response is an infrastructure problem, not a skill
    # result — scoring it as 0.0 would skew the benchmark. Keep the raw output
    # for inspection and stop.
    if not parsed or "assertion_results" not in parsed:
        raw = config_dir / "grading_raw.txt"
        raw.write_text(stdout)
        raise SystemExit(
            f"judge did not return parseable JSON — raw output saved to {raw}")

    results = parsed["assertion_results"]
    passed = sum(1 for r in results if r.get("passed"))
    total = len(results)
    grading = {
        "assertion_results": results,
        "summary": {"passed": passed, "failed": total - passed, "total": total,
                    "pass_rate": round(passed / total, 4) if total else None},
    }
    if truncated:
        grading["files_truncated"] = truncated
    write_json(config_dir / "grading.json", grading)
    return grading
