---
name: axon-ivy-requirements-creation
description: Generate detailed requirements and implementation stories from simple user input. Use when a user provides vague requirements, needs a structured requirements document, or wants to create implementation stories.
---

## Step 0: Load Source Files

Run this step before Step 1 when the user references external source files or folders.

* For `.xlsx` or `.bpmn`, run `axon-ivy-external-loader` with the path and purpose: `requirements for <process>`.
* Read other supported files such as Markdown, PDF, or CSV directly.
* Never infer content from filenames or guess a missing path.
* Use a subagent when the sources are large.

From the loader manifest:

* **Digest** → use as input to Step 1.
* **Findings** → ask the user about unresolved contradictions; never choose a side.
* **Gaps** → tell the user what could not be read.
* **Sources** → preserve source references for traceability.

If the digest lacks needed detail, read the referenced dump.

**Output:** source content for Step 1.

---

## Core 4-Step Process

### Step 1: Detail the Crude Requirements

**Read:** `thinking-dimensions.md` in this skill's directory.

Take the user's input plus everything loaded in Step 0 and expand them into detailed, structured requirements. Use the thinking dimensions to:

- Extract the workflow skeleton from the description
- Decompose each step into inputs, outputs, rules, errors, actors
- Expand vague terms ("details", "info") into specific fields with types
- Define enumerations, roles, state machine, notifications, business rules

**Ask the user only what you cannot reasonably infer.** Keep questions short (max 5 per round). Skip topics already covered by the user's input. Use the expansion heuristics in the file to fill gaps yourself.

**Output:** A detailed internal understanding of the full requirements.

---

### Step 2: Verify Against Checklist

**Read:** `checklist.md` in this skill's directory.

Go through the checklist and verify every applicable question has been answered — either from the user's input, from your Step 1 expansion, or by reasonable inference.

- For each unanswered question: decide if you can infer the answer or need to ask the user
- Batch remaining questions to the user (max 5 per round)
- Mark questions as not-applicable if they don't fit the process scope

**Output:** All checklist items resolved. Requirements are complete.

---

### Step 3: Generate the Requirements Document

**Read:** `requirement-template.md` in this skill's directory.

Use the verified requirements from Steps 1-2 to fill in the template:

- Fill in every applicable section
- Remove sections that don't apply to the specific process
- For repeatable sections (Task Definition, UI Requirements), duplicate as needed
- Replace all placeholder examples with real content

**Output location:** `[project]/documents/requirements/` — create folder if it doesn't exist.

---

### Step 4: Create Implementation Stories

**Read:** `create-stories.md` in this skill's directory.

Decompose the requirements document from Step 3 into implementation stories:

- Follow the dependency order in `create-stories.md`
- For each story type you are about to generate, **read the corresponding file in `story-types/`** before writing the story (e.g., read `story-types/form-composition.md` before writing any form story)
- Each story is a separate file grouped by ticket: `<TICKET>/story_NN_type-name.md` (see filename convention in `create-stories.md`)
- Each story includes: user framing, description, dependencies, implementation details, acceptance criteria

**Output location:** `[project]/documents/stories/<TICKET>/` — create the ticket folder if it doesn't exist.

---

## Next Steps After This Skill

Once stories are generated, use these skills to implement and verify them:

- `axon-ivy-implement-story` — Pick a story and implement it (maps story types to the right skills)
- `axon-ivy-verify-story` — Verify the implementation (runs after each story implementation)

---

## Quality Gate

Before delivering the document, apply the Developer Test:

> "Could a developer build this with ZERO additional questions?"

If no — go back and fill the gaps.
