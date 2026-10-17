---
name: axon-ivy-process
description: Rules and patterns for creating, editing, reviewing, and fixing Axon Ivy workflow processes (.p.json files). Use this when working with any .p.json file — including checking existing processes for errors, reviewing script code, or fixing IvyScript issues.
---

## Schema Loading

For every `.p.json` task, use the `ivy-json-files` skill for schema loading and validation. Do not bundle process schemas here.

## After Using This Skill

**MANDATORY**: After creating or modifying any `.p.json` file, use `axon-ivy-process-verify` skill to validate the output against common errors.

## Use Together With

- `axon-ivy-process-verify` - **MUST use after** generating/editing `.p.json` files
- `axon-ivy-workflow-guide` - Step-by-step workflow creation
- `axon-ivy-data` - For process data classes (`.d.json`), field types, and persistence modifiers
- `axon-ivy-java-data` - For Java models and enums
- `axon-ivy-html` - For dialog UIs
- `ivy-yaml-files` - For task/case/start custom fields configuration in `custom-fields.yaml`

## ID Conventions

**CRITICAL**: Element IDs and connection IDs share the same namespace and MUST NOT conflict.

### ID Rules

1. **Element IDs**: Use sequential IDs starting from `f0` (e.g., f0, f1, f2, ... f15)
2. **Connection IDs**: Use IDs that DO NOT conflict with element IDs
3. **Recommended pattern**: If elements are f0-f15, use f16+ for connections

### Connection Patterns

#### Sequential

```json
"connect": [{ "id": "f16", "to": "f1" }]
```

#### With Labels

```json
"connect": [
  { "id": "f22", "to": "f7", "label": { "name": "Yes" } },
  { "id": "f23", "to": "f3", "label": { "name": "No", "segment": 0.51, "offset": { "x": 0, "y": -8 } } }
]
```

- `segment` is the position on the connection line (0=start, 1=end).
- `offset` is the pixel displacement for the label.

#### With Via Points

```json
"connect": [
  { "id": "f23", "to": "f3", "via": [{ "x": 520, "y": 200 }] }
]
```

## Process Diagram Layout

When adding or inserting an element, reposition downstream elements so the new node and its labels do not overlap existing nodes. Straight connector length is derived from the connected elements' `visual.at` positions; there is no separate length property. Leave roughly 160-200 coordinate units between ordinary sequential elements, and use a connector's `via` points only when its route needs to avoid other nodes or labels. Verify the resulting layout in the process editor.

## Element References

These files provide usage patterns and semantic guidance. Use `ivy-json-files` for schema details.

- `RequestStart` -> `elements/request-start.md` — Start a workflow and define its request signature or case/start metadata.
- `UserTask` -> `elements/user-task.md` — Assign a human task that uses a fixed HTML dialog; prefer this for the common task-plus-UI pattern.
- `TaskSwitchEvent` -> `elements/task-switch-event.md` — Create a human task without a UI, or keep task assignment separate from a dynamic or independently selected UI.
- `DialogCall` -> `elements/dialog-call.md` — Open an HTML dialog separately, typically after a `TaskSwitchEvent` or without task assignment.
- `Script` -> `elements/script.md` — Execute IvyScript in the process. Load `code.md` when Script elements or other IvyScript expressions are present.
- `Alternative` -> `elements/alternative.md` — Branch the process according to conditions.
- `TaskEnd` -> `elements/task-end.md` — End a process flow.

Load these additional references only when applicable:

- SubProcessCall, CallSubStart/End, or TriggerCall -> `subprocess.md` — Call another process, define a callable subprocess, or start a process asynchronously.
- SignalStartEvent -> `signal.md` — Start a process in response to a signal.
- Dialog process elements in `dialog/` (HtmlDialogStart/End, HtmlDialogMethodStart, HtmlDialogExit) -> `logic-process.md` — Implement a dialog's start, methods, events, or close/exit flow.
- EmbeddedProcess -> `embedded.md` — Group process elements into an embedded subprocess.
- ErrorBoundaryEvent or ErrorStartEvent -> `error-handling.md` — Catch an error at an element boundary or start handling a process error.

## Final Checklist

- [ ] Every element ID is unique within its process.

