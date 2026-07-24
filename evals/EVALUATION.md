# Skill Evaluation Quick Guide

## Write Eval Cases

File: `<skill>/evals/evals.json`

Minimum recommended fields per case:
- `id`
- `name`
- `fixture`: optional, initial workspace to run the eval.
- `prompt`
- `expected_output`
- `assertions`: list of checks to verify correctness

Example:

```json
{
  "skill_name": "axon-ivy-custom-fields",
  "evals": [
    {
      "id": 0,
      "name": "add-approved-field",
      "fixture": "ivy-project",
      "prompt": "add a task custom field called `approved`, a Yes/No string, and translate it to German",
      "expected_output": "The field is defined in config/custom-fields.yaml, with German translations added in cms/cms_de.yaml.",
      "assertions": [
        "config/custom-fields.yaml defines the approved field with Type STRING",
        "cms/cms_de.yaml contains a German translation for it"
      ]
    }
  ]
}
```

Some skills only work correctly when another skill is also loaded. Declare these with a
top-level `depends_on`:

```json
{
  "skill_name": "axon-ivy-html",
  "depends_on": [
    "process-workflow/skills/axon-ivy-process",
    "ui/skills/axon-ivy-cms"
  ],
  "evals": [ ... ]
}
```

## Run Evals CI

Use workflow:
- `.github/workflows/evaluate-skill.yml`

It runs evaluate + report + gate and uploads results as artifact.

Gate checks:
- correctness: with-skill pass rate is 100%
- efficiency: if all assertions pass when running without skill, running with skill should save more tokens (10% default)

## What This Measures

Each eval case runs twice:
- with skill
- without skill (baseline)

The harness compares the two runs using:
- pass rate (correctness)
- tokens and time (efficiency)

## Result Structure

```text
<skill>-workspace/
  eval-<id>-<slug>/
    with_skill/
    without_skill/
  benchmark.json
  feedback.json
  report.html
```

Useful files:
- `benchmark.json`: aggregate metrics and deltas
- `grading.json`: per-assertion pass/fail with evidence
- `transcript.txt`: model run transcript
- `timing.json`: duration and token usage


## Local evaluation

1. Docker is installed and running.
2. Build the sandbox image once:

```bash
docker build -t skill-eval-agent evals/docker
```

3. Set a Copilot-licensed token:

```bash
export COPILOT_GH_TOKEN=<your_pat>
```

4. Run all eval cases for one skill:

```bash
python3 evals/evaluate.py --skill configuration/skills/custom-fields-l10n
```

5. Generate Report

```bash
python3 evals/report.py --skill configuration/skills/custom-fields-l10n
```
