import json

from . import container
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


def grade(case, config_dir, *, model, timeout, extra_results=None,
          provider=container):
    extra_results = extra_results or []
    assertions = case.get("assertions", [])

    def finalize(results, *, note=None, extra_fields=None):
        combined = extra_results + results
        passed = sum(1 for r in combined if r.get("passed"))
        total = len(combined)
        grading = {"assertion_results": combined,
                   "summary": {"passed": passed, "failed": total - passed, "total": total,
                               "pass_rate": round(passed / total, 4) if total else None}}
        if note:
            grading["note"] = note
        if extra_fields:
            grading.update(extra_fields)
        write_json(config_dir / "grading.json", grading)
        return grading

    if not assertions:
        return finalize([], note=None if extra_results else "no assertions defined")

    baseline = read_json(config_dir / "baseline.json")
    changed = collect_changed_files(config_dir / "outputs", baseline, DEFAULT_EXCLUDES)
    prompt, truncated = build_grading_prompt(case, changed)

    judge_result = provider.run_judge(prompt, config_dir, model=model, timeout=timeout)

    def errored(reason):
        (config_dir / "grading_raw.txt").write_text(judge_result.text or "")
        grading = {"assertion_results": extra_results,
                   "summary": {"passed": None, "failed": None,
                               "total": None, "pass_rate": None},
                   "error": reason}
        write_json(config_dir / "grading.json", grading)
        print(f"    !! grading errored — recorded, run continues: {reason}")
        return grading

    if judge_result.returncode != 0:
        return errored(f"judge run failed: {judge_result.text}")

    parsed = extract_json(judge_result.text)
    if not parsed or "assertion_results" not in parsed:
        return errored("judge did not return parseable JSON "
                       f"(raw output saved to {config_dir / 'grading_raw.txt'})")

    return finalize(parsed["assertion_results"],
                    extra_fields={"files_truncated": truncated} if truncated else None)
