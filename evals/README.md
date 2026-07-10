# Skill evaluation (GitHub Copilot)

Eval-driven iteration for the skills in this repo, targeting **GitHub Copilot** via the
official Copilot SDK. Based on <https://agentskills.io/skill-creation/evaluating-skills>.

Each test case runs twice — **with** the skill and **without** it (baseline) — in isolated
workspaces. An LLM judge (Copilot itself) grades the produced files against the case's
assertions, and the harness reports the delta. That delta is the whole point: *does this
skill make Copilot measurably better at the task?*

## The loop

1. Author `evals.json` — prompts + a human description of success.
2. Run the harness, then read `transcript.txt` and `outputs/` to see what "good" looked like.
3. Add `assertions` (objective pass/fail statements); rerun.
4. Study failed assertions and the transcripts; improve `SKILL.md`.
5. Rerun into `iteration-<N+1>/`. Stop when results plateau.

## Prerequisites

The eval drives the **GitHub Copilot SDK**, so it needs the SDK in the running interpreter:

- GitHub Copilot signed in (`copilot --version` works) — the SDK reuses that login.
- **Python 3.11+ with `github-copilot-sdk`.** If the box has no `pip` / is PEP-668
  externally-managed, use a venv:
  ```bash
  python3 -m venv .venv
  .venv/bin/python -m pip install github-copilot-sdk
  ```
  `evaluate.py` auto-re-execs into a repo-local `.venv` if it finds the SDK there, so
  `python3 evals/evaluate.py …` works even from an interpreter that lacks it.

Why the SDK: **tokens** come from official `assistant.usage` events (the model's own
accounting, not a scraped estimate), skills load deterministically via `skill_directories`,
and `skill.invoked` confirms the skill actually fired. We emit the agentskills.io benchmark
metrics exactly — `pass_rate`, `time_seconds`, `tokens`.

## Run

```bash
# All cases for a skill, iteration 1
python3 evals/evaluate.py --skill axon-ivy-cms

# One case, into a new iteration dir
python3 evals/evaluate.py --skill axon-ivy-cms --eval-id 1 --iteration 2

# Inspect the exact plan without calling Copilot
python3 evals/evaluate.py --skill axon-ivy-cms --dry-run
```

Useful flags: `--skip-baseline` (with-skill only), `--no-invoke-skill` (test natural
triggering instead of forcing the skill), `--keep-workspaces`, `--timeout N`,
`--model <name>` (pins the model for reproducibility; default `claude-sonnet-5`).

> **Model matters.** The with/without delta is model-dependent, so the harness pins
> `--model` by default and records both `model_pinned` and the actually-observed model
> (`models_observed`) in `benchmark.json`. Pin to whatever your team actually uses.

## Run in CI (GitHub Actions)

[`evaluate-skill.yml`](../.github/workflows/evaluate-skill.yml) wraps the same commands as a
manually-triggered workflow: **Actions → Evaluate skill → Run workflow**, pick the skill
(and optionally `eval_id`, `iteration`, `model`, `skip_baseline`). It runs the eval,
generates `report.html`, posts the benchmark table to the run's summary page, and uploads
the whole `iteration-N/` directory as an artifact (kept 30 days). If the harness fails fast
on an infrastructure error, the artifact still contains the diagnostics
(`transcript.txt`, `grading_raw.txt`).

One-time setup: add a repo secret **`COPILOT_GH_TOKEN`** — a PAT of an account that has a
GitHub Copilot license (the default Actions `GITHUB_TOKEN` has none). The Copilot CLI reads
it from `GH_TOKEN`.

## Authoring `evals.json`

Lives at `<skill>/evals/evals.json`. Per-case fields:

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Stable identifier (used by `--eval-id`). |
| `prompt` | yes | Realistic user message — what someone would actually type. |
| `expected_output` | yes | Human description of success (guides the judge). |
| `assertions` | no\* | Objective PASS/FAIL statements. *\*Add after you've seen the first run — without them the run is recorded but not graded (`pass_rate: null`).* |
| `name` | no | Slug for the eval directory (`eval-<name>`). Falls back to a slug of the prompt. |
| `files` | no | Extra input files (repo-relative). Each is copied to the **workspace root under its basename** — subdirectories are not preserved, so reference the bare filename in the prompt. |
| `fixture` | no | Name of a project snapshot under `evals/fixtures/` to start from (currently: `ivy-project`). Omit for skills that start from an empty workspace. |

A real case from this repo — [`axon-ivy-cms/evals/evals.json`](../axon-ivy-cms/evals/evals.json)
(first of three; assertions trimmed here, see the file for the full set):

```json
{
  "skill_name": "axon-ivy-cms",
  "evals": [
    {
      "id": 0,
      "name": "create-yesno-labels",
      "prompt": "The Axon Ivy project at {PROJECT_DIR} has no CMS text content yet. Add reusable Yes/No confirmation labels (the displayed text should be 'Yes' and 'No') that several dialogs could share, plus a confirmation question label with the text 'Do you agree to the terms and conditions?'. Set things up so these are available via ivy.cms.co(...).",
      "expected_output": "A cms_en.yaml is created under the project's cms/ folder. Reusable Yes/No labels are added under the Labels: namespace with the option keys single-quoted ('Yes'/'No') so SnakeYAML does not coerce them to booleans. The confirmation question is added as a text entry under a sensible namespace. Keys use colon-separated nesting and the file is valid YAML.",
      "fixture": "ivy-project",
      "assertions": [
        "A cms_en.yaml file is created in the project's cms/ folder",
        "cms_en.yaml parses as valid YAML",
        "The Yes and No option keys are written as single-quoted strings ('Yes'/'No'), so SnakeYAML (YAML 1.1) does not coerce them to boolean true/false"
      ]
    }
  ]
}
```

`{PROJECT_DIR}` in a `prompt` is substituted at run time with the run's workspace root
(where the `fixture` was copied), so prompts can name the project location explicitly.

Tips: start with 2–3 cases; vary phrasing; include one edge case. **Don't write assertions
until you've seen the first run's output.** Reserve assertions for objectively checkable
things — leave subjective quality to human review (`feedback.json`).

## Fixtures

`evals/fixtures/<name>/` holds pre-initialized Axon Ivy project snapshots. Each run gets a
fresh copy, so runs never contaminate each other. Skills cluster onto a few starting states,
so you need a handful of fixtures — not one per skill.

One fixture is committed today: **`ivy-project`**, a minimal initialized Axon Ivy project
(`pom.xml`, `.ivyproject`, the `config/` YAMLs, and one `BusinessProcess` with its data
class). Build artifacts (`target/`, `src_generated/`) are git-ignored and excluded from the
copy, so runs always start from clean sources.

## Visualize results

`report.py` renders an iteration's `benchmark.json` (+ per-eval `grading.json`) into a
self-contained `report.html`: a plain JUnit-style test report — a pass/fail status banner, a
with-vs-without comparison table (pass rate, tokens, time + Δ), and one collapsible section
per eval listing its assertions as ✓/✗ rows with evidence. No dependencies; opens offline.

```bash
python3 evals/report.py --skill axon-ivy-cms                    # latest iteration
python3 evals/report.py --skill axon-ivy-cms --iteration 2 --open
```

Written to `<skill>-workspace/iteration-N/report.html`; re-run it after a fresh eval.

## Output layout

```
<skill>-workspace/
  iteration-N/
    eval-<slug>/
      with_skill/     outputs/  transcript.txt  timing.json  grading.json  baseline.json
      without_skill/  outputs/  transcript.txt  timing.json  grading.json  baseline.json
    benchmark.json    # per-config pass_rate / time_seconds / tokens + deltas
    feedback.json     # human-review notes, keyed by eval dir (fill in by hand)
    report.html       # from report.py
```

`timing.json` records `duration_ms` (wall-clock) and `total_tokens`, plus a `copilot_usage`
breakdown (input / output / cache tokens, `invoked_skills`) — all from the SDK's
`assistant.usage` events. `total_tokens` is full throughput incl. cache, so the delta
reflects the context cost the skill's text adds. `baseline.json` is the pre-run hash map of
the workspace; grading diffs `outputs/` against it to find what the agent changed.

**Failure handling.** Infrastructure failures fail fast — an SDK error in a task run, a
failed judge run, or an unparseable judge response aborts the harness immediately instead of
being scored as a skill failure (which would poison the benchmark deltas). Diagnostics stay
on disk: the task error in `transcript.txt`, the raw judge output in `grading_raw.txt`. Fix
the issue and rerun the iteration.

## Code layout

Logic lives in the `skill_eval/` package, organized by concern; `evaluate.py` and `report.py`
are thin entry points (so `python3 evals/evaluate.py …` and `python3 -m skill_eval {run|report}`
both work).

| Layer | Module | Responsibility |
|---|---|---|
| infrastructure | `common` | paths, JSON IO, filesystem helpers, tunables |
| | `schemas` | the `Usage` dataclass (token accounting) |
| execution | `copilot` | **the only provider-specific module** — drives the Copilot SDK; runs the task/judge, returns typed usage |
| measurement | `workspace` | build the run's initial project from a fixture |
| | `grading` | LLM-as-judge scoring of changed files |
| | `functional` | run each case with/without, record results |
| presentation | `benchmark` | aggregate → `benchmark.json`, feedback stub |
| | `html_report` | the report renderer |
| entry point | `cli` | `run` / `report` argument handling |

To retarget another agent host, write a sibling of `copilot.py` (same `run_task`/`run_judge`
contract) — nothing else is provider-aware.

## Alignment with the open standard

Implements the agentskills.io eval loop and emits its file formats verbatim:

- **Conformant:** `evals.json` fields (`skill_name`, `id`, `prompt`, `expected_output`,
  `files`, `assertions`), the `iteration-N/eval-<slug>/{with,without}_skill/` layout, and the
  `grading.json`, `timing.json`, `benchmark.json`, `feedback.json` shapes.
- **One documented extension:** the per-case `fixture` field. The standard's `files` lists
  individual input files; a whole initialized Axon Ivy project is impractical that way, so
  `fixture` names a committed project snapshot instead. Purely additive — standard tooling
  ignores unknown fields, and `files` still works per spec.
- **Copilot-specific substitutions:** a fresh Copilot SDK session per config (the guideline's
  clean-context isolation) instead of Claude subagents; `tokens` from the SDK's
  `assistant.usage` events. Neither changes the standard file formats.
