---
name: axon-ivy-implement-story
description: Implement any formal story: data models, entities, processes, UI, forms, roles, etc.
---

# Conditional References

After reading the story, evaluate these triggers before continuing:

- Story has dependencies → MUST load `dependencies.md`
- Story has 2+ implementation units → MUST load `parallel-work.md` before implementation
- User requests multiple stories → MUST load `multi-story.md` before planning
- Implementation is complete → MUST load `verification.md` before marking completion

Do not skip a required reference because the task appears simple or the behavior seems obvious.

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

## 4. Plan Implementation

Plan implementation parts according to their dependencies.

Determine:

- which parts must run sequentially
- which parts can run independently
- which shared files require coordination

Follow any loaded planning references.

## 5. Implement

For each part:

- Follow the story specification.
- Follow the specialist skill.
- Follow existing project conventions where unspecified.
- Create or modify only required artifacts.

Do not invent requirements or unrelated abstractions.

## Complete

Follow `verification.md`.