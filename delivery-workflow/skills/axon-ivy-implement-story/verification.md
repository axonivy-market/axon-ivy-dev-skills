# Story Verification

Use this guidance after implementation is complete.

## 1. Verify Changed Artifacts

Run the focused verifier for each changed artifact type:

| Artifact      | Verification                      |
| ------------- | --------------------------------- |
| `.p.json`     | `axon-ivy-process-verify`         |
| `.xhtml`      | `axon-ivy-primefaces-verify`      |
| CMS entries   | `axon-ivy-cms-verify`             |
| `.java`       | build/tests + story specification |
| `.d.json`     | build + story specification       |
| configuration | corresponding verifier            |

Verify related artifacts together when practical.

Prefer focused verification over repeatedly running the full project build.

## 2. Build and Test

Run `verify-build.py` from the `scripts/` folder of this skill and pass the project directory as argument.

The script runs the project build and summarizes validation findings.

Then:

* run relevant automated tests when available
* fix failures caused by the story
* report unrelated pre-existing failures separately

## 3. Verify the Story

Run:

```text
axon-ivy-verify-story
```

Verify each acceptance criterion individually.

Mark `[x]` only when there is implementation or verification evidence that the criterion is satisfied.

Do not consider a criterion satisfied only because the project builds or an artifact verifier passes.

If a criterion cannot be verified, leave it unchecked and report why.

The story is complete only when all required acceptance criteria are satisfied.
