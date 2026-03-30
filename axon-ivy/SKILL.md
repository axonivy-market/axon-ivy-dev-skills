---
name: axon-ivy
description: Master router skill for all requirement clarification, create story, development, review, and testing tasks. Detects user intent and orchestrates the correct path using specialized skills and parallel subagents.
---

## When to Use

Use this skill as the **single entry point** whenever the user wants to do anything in an Axon Ivy project. It routes to the right path automatically.

---

## Step 0: Check for Existing Ivy Project

**Before doing anything else**, search for `.ivyproject` files to locate existing Axon Ivy projects **within this codebase only**:

1. Use Glob with pattern `**/.ivyproject` scoped to the current working directory, skipping `.claude/`, `.github/`, and `.vscode/` folders
2. For each `.ivyproject` found, read it to extract the `name` field, then locate and read the sibling `pom.xml` for `groupId` and `artifactId`
3. Present findings to the user in a short summary, e.g.:
   ```
   Found project: invoice-parser
   Group ID:      com.example
   Artifact ID:   invoice-parser
   Location:      invoice-parser/
   ```

**If NO `.ivyproject` is found:** automatically run **Path A — Project Bootstrap** first (no prompt needed), then — once Path A is fully complete — continue to the path that matches the user's original intent (Step 1 below). Do NOT skip ahead to requirements or stories before the project is scaffolded.

**If one or more projects ARE found:** present the summary, then proceed to Step 1.

---

## Step 1: Detect Intent

Read the user's request and match it to one of the 4 paths:

| If user says... | Path |
|---|---|
| "new project", "create project", "init", "scaffold" | **A — Project Bootstrap** |
| "implement story N", "work on story", "continue story N" | **B — Story Pipeline** |
| "build feature", "new feature", "create workflow", "add functionality" | **C — Feature Builder** |
| "verify", "review", "check my changes", "run checks", "quality gate" | **D — Verify All** |

If intent is **ambiguous**, use your best judgment — freely decide which path fits the user's goal most naturally. State your choice in one line before starting, e.g.:
`→ Routing to Path B: Story Pipeline`

---

## Path A: Project Bootstrap

**Goal:** Scaffold a new project that is ready for development.

**Sequential steps in main context:**

1. Run skill `axon-ivy-init` — scaffold project from template, run Maven build
2. After scaffold completes, **spawn 2 parallel subagents:**
   - **`config-setup`** — follow `axon-ivy-variable-config` + `axon-ivy-user-role-config`: create `config/variables.yaml`, `config/roles.yaml`, `config/users.yaml`
   - **`data-scaffold`** — follow `axon-ivy-data`: create base data classes in `dataclasses/`
3. Wait for both subagents to finish
4. Run skill `axon-ivy-custom-fields` if the project needs task/case metadata fields

**Done when:** project builds cleanly and base config files exist. If Path A was triggered as a prerequisite (i.e., no `.ivyproject` existed when the user asked for a feature or story), immediately continue to the originally intended path — do not stop here.

---

## Path B: Story Pipeline

**Goal:** Implement a story end-to-end and verify it passes all checks.

**Steps:**

1. Read the story file `[project]/documents/stories/story_NN.md`
2. Run skill `axon-ivy-implement-story` — implement all parts sequentially
3. After all parts are done, **spawn 3 parallel verification subagents:**

   | Subagent | Follows | Scope |
   |---|---|---|
   | **`process-verify`** | `axon-ivy-process-verify` | All `.p.json` files modified in this story |
   | **`cms-verify`** | `axon-ivy-cms-verify` | All `cms_*.yaml` files modified in this story |
   | **`ui-verify`** | `axon-ivy-primefaces-verify` | All `.xhtml` files modified in this story |

4. Collect results from all 3 subagents
5. If **any subagent reports failures** → fix the issues, then re-spawn only the failing subagent(s)
6. Once all pass, run `axon-ivy-verify-story` in main context for final acceptance criteria check
7. Mark story checkboxes `[x]` on pass

---

## Path C: Feature Builder

**Goal:** Turn a plain feature description into a fully implemented and verified feature.

**Steps:**

1. Run skill `axon-ivy-requirements-creation` — produce structured requirements doc + ordered story files
2. Present the story list to the user; confirm the implementation order
3. Spawn a **`story-planner`** subagent to identify which stories can run in parallel (e.g., CMS stories alongside process stories)
4. For each story (or parallel batch), execute **Path B: Story Pipeline**
5. After all stories pass, run **Path D: Verify All** as a final gate

---

## Path D: Verify All

**Goal:** Run the full verification and review suite on recent changes and produce a consolidated report.

**Spawn 6 parallel subagents simultaneously:**

| Subagent | Follows | Scope |
|---|---|---|
| **`process-verify`** | `axon-ivy-process-verify` | All modified `.p.json` files |
| **`cms-verify`** | `axon-ivy-cms-verify` | All modified `cms_*.yaml` files |
| **`ui-verify`** | `axon-ivy-primefaces-verify` | All modified `.xhtml` files |
| **`story-verify`** | `axon-ivy-verify-story` | Current story acceptance criteria |
| **`java-review`** | `review-java` | All modified `.java` files |
| **`js-review`** | `review-javascript` | All modified `.js` / `.ts` files |

Skip subagents where no matching files exist in the current changeset.

Wait for all, then output a **consolidated report**:

```
✓ Process verify:     PASS  (N files checked)
✗ CMS verify:         FAIL  — cms_en.yaml line 42: key mismatch
✓ PrimeFaces verify:  PASS  (N files checked)
✓ Story verify:       PASS  (all acceptance criteria met)
✓ Java review:        PASS  (N files checked)
✗ JavaScript review:  FAIL  — formHelper.js: cookie manipulation detected

Action required: Fix 2 issues before proceeding.
```

Only mark the story done when all applicable subagents show PASS.

---

## Subagent Instructions Pattern

When spawning a subagent, provide:
1. The **skills folder path** so it can read `skill-overview.md` for the full list and then read any relevant `SKILL.md` itself
2. The **task and scope**

Use this prompt structure:

```
You are a specialized Axon Ivy agent.
Skills folder: .claude/skill/

Start by reading `.claude/skill/axon-ivy/skill-overview.md` to understand all available skills,
then read the SKILL.md file(s) relevant to your task before starting.

Project root: [absolute path]
Task: [what to do]
Scope: [specific files or areas]
Report all issues found or artifacts created.
```

---

## General Rules

- **State the detected path in one line** before starting — no confirmation needed unless the user explicitly asks
- Show a brief plan (which steps, which subagents) before executing
- On subagent failure, pause the chain — do not skip to the next step
- After any Maven-triggering change (`.d.json`, `pom.xml`), remind the user to run `mvn install`
