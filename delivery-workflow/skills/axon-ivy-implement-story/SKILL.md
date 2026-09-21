---
name: axon-ivy-implement-story
description: Implement any formal story: data models, entities, processes, UI, forms, roles, etc.
---

# Conditional Sections

After reading the story, evaluate these triggers before continuing:

- Story has dependencies → follow "Dependency Handling" below
- Story has 2+ implementation units → follow "Parallel Work" below before implementation
- User requests multiple stories → follow "Multiple Stories" below before planning
- Implementation is complete → follow "Story Verification" below before marking completion

Do not skip a required section because the task appears simple or the behavior seems obvious.

Never run `mvn` or build commands directly. Use `scripts/verify-build.py <project_dir>` instead.

# Workflow

## 1. Read Story

Read the selected story and identify:

- story type
- dependencies
- implementation parts
- acceptance criteria

## 2. Inspect Existing Implementation

Before creating artifacts, inspect 1–3 similar implementations in the project.

Follow this priority:

1. Story requirements
2. Mandatory specialist skill rules
3. Existing project conventions
4. Simplest conventional implementation

Do not introduce a new pattern when an equivalent project pattern already exists.

## 3. Load Specialist Skills

| Story Type | Skills |
|---|---|
| Data Model | `axon-ivy-java-data`, `axon-ivy-data` |
| Entity + Repository | `axon-ivy-java-data` |
| Smart Workflow | `axon-ivy-process`, `axon-ivy-data`, `axon-ivy-smart-workflow` |
| UI Component | `axon-ivy-html`, `axon-ivy-cms` |
| Tag Library | `axon-ivy-html` |
| Form | `axon-ivy-html`, `axon-ivy-process`, `axon-ivy-cms` |
| Main Process | `axon-ivy-process`, `axon-ivy-workflow-guide` |
| Roles + Config | `axon-ivy-user-role-config` |

Let specialist skills load their own feature-specific references.

### Specialist Skill Execution

When invoking a specialist skill, follow its implementation rules but defer build, test, regeneration, and verification to "Story Verification" below.
Only run a specialist skill's intermediate build command when its generated output is required to continue implementation.

## 4. Plan Implementation

Plan implementation parts according to their dependencies.

Determine:

- which parts must run sequentially
- which parts can run independently
- which shared files require coordination

Follow "Parallel Work" and "Multiple Stories" below when they apply.

## 5. Implement

For each part:

- Follow the story specification.
- Follow the specialist skill.
- Follow existing project conventions where unspecified.
- Create or modify only required artifacts.

Do not invent requirements or unrelated abstractions.

## Complete

Follow "Story Verification" below.

# Dependency Handling

Verify dependency outputs exist and are usable before implementing the story.

Expected artifacts by story type:

- Data Model: .d.json, model/enum .java
- Entity + Repository: entity/repository .java
- Smart Workflow: .p.json, data classes
- UI Component: .xhtml
- Tag Library: .taglib.xml
- Form: .xhtml, .p.json, dialog data
- Main Process: .p.json
- Roles + Config: config files

Do not treat an empty/stub file as a satisfied dependency.

If missing:

- dependency is included in requested stories: implement it first
- otherwise: report the current story as blocked

Do not create temporary substitutes for missing dependencies.

# Parallel Work

Parallelize independent implementation units when useful.

Safe when:

- neither unit depends on the other's output
- they modify different files
- coordination overhead is low

Keep sequential when outputs depend on each other:

```text
Entity → Repository
Process → Dialog
Component → Tag Library → Form
```

# Multiple Stories

Use this guidance when the user asks to implement more than one story.

## Build a Dependency Plan

Read all requested stories and identify dependencies before implementation. Do not use story number as execution order.

Example:

Data Model: none
Entity + Repository: Data Model
Smart Workflow: Data Model
UI Components: Data Model
Tag Library: UI Components
Forms: Tag Library
Main Process: Forms

## Execution Rules

- Start stories whose dependencies are satisfied.
- Run independent stories in parallel when useful.
- After each completed batch, unblock and start newly ready stories.
- Do not parallelize work that modifies the same shared file (e.g. CMS, taglib, config, registry, central process).

## Missing Dependencies

- If the missing dependency is also requested, implement it first.
- Otherwise, if its expected artifacts are missing, mark the story blocked.
- Do not create temporary substitutes for missing dependencies.

## Verification

Verify each story individually after implementation.

After all related stories are complete, run integration/build verification to detect problems between their artifacts.

# Story Verification

Use this guidance after implementation is complete.

## 1. Verify Changed Artifacts

Run only the focused verifiers that apply:

```text
.p.json: axon-ivy-process-verify
.xhtml: axon-ivy-primefaces-verify
CMS: axon-ivy-cms-verify
configuration: corresponding verifier
```

Verify related artifacts together when practical.

## 2. Build

Run `verify-build.py` from this skill's `scripts` folder with the project directory.
Run it once after integration, or after the final dependent batch for multiple stories.
Run earlier only if generated output is needed to continue.

## 3. Verify Story

Run `axon-ivy-verify-story`.
Mark complete only when artifact verification, build, and story verification pass. Report unrelated pre-existing failures separately.
