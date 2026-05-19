---
name: axon-ivy-process
description: Rules and patterns for creating, editing, reviewing, and fixing Axon Ivy workflow processes (.p.json files). Use this when working with any .p.json file — including checking existing processes for errors, reviewing script code, or fixing IvyScript issues.
---

## Schema Reference

See `axon-ivy-process-schema-14.0-dev/` folder for JSON schemas:

- `process.json` - Main process schema (self-contained with all `$defs` inline)

## After Using This Skill

**MANDATORY**: After creating or modifying any `.p.json` file, use `axon-ivy-process-verify` skill to validate the output against common errors.

## Use Together With

- `axon-ivy-process-verify` - **MUST use after** generating/editing `.p.json` files
- `axon-ivy-workflow-guide` - Step-by-step workflow creation
- `axon-ivy-data` - For master data class and models
- `axon-ivy-html` - For dialog UIs
- `axon-ivy-custom-fields` - For task/case/start custom fields configuration

## Always Load on Invocation

**MANDATORY** — load these every time the skill is invoked, regardless of task:

- **`code.md`** — IvyScript rules for Script elements: variable types (`var` not supported), `ivy.case`/`ivy.task` property access, casting, logging. Nearly every process has Script elements, so these rules always apply.

## Load References When Needed

Load these only when the process contains the relevant element type:

- Calling subprocesses (SubProcessCall, CallSubStart/End) → Load `subprocess.md`
- Signal-based start (SignalStartEvent) → Load `signal.md`
- Dialog processes in `src_hd/` (HtmlDialogStart/End, MethodStart, Exit vs End) → Load `logic-process.md`
- Embedded grouping (EmbeddedProcess) → Load `embedded.md`
- Error handling (ErrorBoundaryEvent, ErrorStartEvent) → Load `error-handling.md`

## Process JSON Structure

```json
{
  "$schema": "https://json-schema.axonivy.com/14.0-dev/project/process.json",
  "id": "UNIQUE_HEX_ID",
  "kind": "NORMAL",
  "config": {
    "data": "package.name.MasterDataClass"
  },
  "elements": [ ... ],
  "layout": {
    "lanes": [
      { "name": "Lane Name", "size": 480 }
    ]
  }
}
```

### Process Kind

- `NORMAL` — Main process, entry point for workflow (default)
- `CALLABLE_SUB` — Callable sub-process, invoked via `SubProcessCall`
- `WEB_SERVICE` — Web service process
- `HTML_DIALOG` — HTML dialog process

## Element Types

### RequestStart (Entry Point)

```json
{
  "id": "f0",
  "type": "RequestStart",
  "name": "start",
  "config": {
    "signature": "start",
    "request": {
      "name": "Process Name",
      "description": "Process description"
    },
    "case": {
      "name": "Case: <%= param.name %>",
      "customFields": [
        { "name": "caseType", "value": "\"HR Request\"" },
        { "name": "businessUnit", "value": "param.department" }
      ]
    },
    "start": {
      "customFields": [
        { "name": "processCategory", "value": "\"HR Onboarding\"" },
        { "name": "requiredRole", "value": "\"HRManager\"" }
      ]
    }
  },
  "visual": { "at": { "x": 40, "y": 64 } },
  "connect": [{ "id": "f0_1", "to": "f1" }]
}
```

**IMPORTANT**: Before adding `customFields` to RequestStart, use `axon-ivy-custom-fields` skill to define fields in `config/custom-fields.yaml` (load `case.md` for Cases, `start.md` for Starts).

### UserTask (Human Task + Dialog) — DEFAULT for "task + UI" steps

**ALWAYS prefer `UserTask` when a step combines a human task with an HTML dialog.** It bundles task assignment and dialog display into one element, keeps the process compact, and matches the standard pattern used in `axon-ivy-workflow-guide`. Use the separate `TaskSwitchEvent` + `DialogCall` pair only for advanced cases where the task and the UI must be decoupled (e.g., the same task can be completed by different dialogs, the dialog is launched conditionally after the task starts, or the task has no UI at all).

```json
{
  "id": "f1",
  "type": "UserTask",
  "name": "Task Name",
  "config": {
    "dialog": "package.DialogName:start(hr.model.Employee,hr.model.JobInfo)",
    "call": {
      "map": {
        "param.employee": "in.employee",
        "param.jobInfo": "in.jobInfo"
      }
    },
    "task": {
      "name": "Task for <%= in.employee.name %>",
      "description": "Task description",
      "skipTasklist": true,
      "responsible": {
        "type": "ROLE_FROM_ATTRIBUTE",
        "script": "in.roleName"
      },
      "customFields": [
        { "name": "employeeName", "value": "in.employee.name" },
        { "name": "department", "value": "in.employee.department" }
      ]
    },
    "output": {
      "map": {
        "out": "in",
        "out.result": "result.data"
      }
    }
  },
  "visual": { "at": { "x": 128, "y": 64 }, "size": { "width": 128 } },
  "connect": [{ "id": "f1_2", "to": "f2" }]
}
```

**UserTask config properties:**

- `dialog` — dialog signature using `.` (dot) package separators: `"package.DialogName:start(ParamTypes)"`
- `call.map` — maps process data to dialog `param.*` inputs
- `task` — task assignment configuration (name, description, responsible, expiry, customFields)
- `output.map` — maps dialog `result.*` back to process data

**Task responsible types:**

- `ROLE_FROM_ATTRIBUTE` — role name from expression: `"script": "in.roleName"`
- `USER_FROM_ATTRIBUTE` — username from expression: `"script": "in.username"`

**Task expiry (optional)**: Add `expiry` inside `task` to set a deadline.

```json
"task": {
  "name": "Review Document",
  "expiry": {
    "timeout": "new Duration(\"3D\")"
  }
}
```

**CRITICAL — Duration format**: Use `new Duration("XD")` for days or `new Duration("XH")` for hours (capital letter). Do NOT use shorthand like `"3d"` or `"5d"`.

**IMPORTANT**: Before adding `customFields` to UserTask, use `axon-ivy-custom-fields` skill (load `task.md`) to define fields in `config/custom-fields.yaml` under `Tasks:`.

**Note on `dialog`**: Uses `.` (dot) package separators. This is different from `SubProcessCall.processCall` which uses `/` (slash) path separators.

### TaskSwitchEvent (Human Task) — only when `UserTask` does not fit

Use `TaskSwitchEvent` only when you cannot use `UserTask` (see the UserTask section above for when that applies — e.g. a task without UI, or a task whose UI is selected dynamically). For the common "human task with a fixed dialog" case, use `UserTask` instead.

**CRITICAL — Variable is `in1`, NOT `in`**: Inside a `TaskSwitchEvent`, all expressions that reference process data (`task.name`, `task.description`, `responsible.script`, `output.code`, `case.name`, etc.) MUST use `in1` — it is the first output branch of the event. Using `in` here produces `Variable 'in' cannot be resolved`. This is the exact opposite of `UserTask`, which uses `in`.

```json
{
  "id": "f1",
  "type": "TaskSwitchEvent",
  "name": "Task Name",
  "config": {
    "task": {
      "name": "Task for <%= in1.project.name %>",
      "description": "Task description",
      "responsible": {
        "type": "ROLE_FROM_ATTRIBUTE",
        "script": "in1.roleName"
      }
    },
    "case": {
      "name": "Case Name",
      "description": "Case description"
    },
    "output": {
      "code": "ivy.case.attachToBusinessCase(in1.parentCaseId);"
    }
  },
  "visual": { "at": { "x": 128, "y": 64 } },
  "connect": [{ "id": "f1_2", "to": "f2" }]
}
```

### DialogCall (Dialog Display)

Use `DialogCall` to display an HTML dialog. Typically connected after a `TaskSwitchEvent` for human task workflows, or used standalone for dialogs without task assignment.

```json
{
  "id": "f2",
  "type": "DialogCall",
  "name": "Dialog Name",
  "config": {
    "dialog": "package.DialogName:start()",
    "output": {
      "map": {
        "out": "in",
        "out.result": "result.data"
      }
    }
  },
  "visual": { "at": { "x": 248, "y": 64 } },
  "connect": [{ "id": "f2_3", "to": "f3" }]
}
```

**Note**: `dialog` uses `.` (dot) package separators. This is different from `SubProcessCall.processCall` which uses `/` (slash) path separators.

**CRITICAL — Dialog ID is the folder path, NOT folder + class name.** The dialog ID is composed of the package (parent folders under `src_hd/`) plus the dialog folder name. The dialog folder name appears **once** at the end — do NOT append it again. Same rule applies to `UserTask.dialog`.

```
Folder layout:        src_hd/com/example/orders/OrderForm/
                                                ├── OrderForm.xhtml
                                                ├── OrderFormData.d.json
                                                └── OrderFormProcess.p.json

Dialog ID:            com.example.orders.OrderForm        ← folder path, OrderForm appears ONCE
Data class FQN:       com.example.orders.OrderForm.OrderFormData
DialogCall.dialog:    "com.example.orders.OrderForm:start()"

WRONG:                "com.example.orders.OrderForm.OrderForm:start()"     ← duplicated name
                      → runtime error: "User Dialog '...OrderForm.OrderForm' not found"
```

### Script (Code Execution)

```json
{
  "id": "f3",
  "type": "Script",
  "name": "Script Name",
  "config": {
    "output": {
      "code": [
        "import package.ClassName;",
        "in.field = value;",
        "ivy.case.name = \"Case: \" + in.name;"
      ]
    },
    "sudo": true
  },
  "visual": { "at": { "x": 416, "y": 64 } },
  "connect": [{ "id": "f3_4", "to": "f4" }]
}
```

`sudo: true` — execute with elevated permissions (optional).

For detailed script code patterns, load `code.md`.

### Alternative (Conditional Branch)

```json
{
  "id": "f4",
  "type": "Alternative",
  "name": "Condition?",
  "config": {
    "conditions": {
      "f4_5": "in.value != null",
      "f4_6": ""
    }
  },
  "visual": { "at": { "x": 520, "y": 64 } },
  "connect": [
    { "id": "f4_5", "to": "f5" },
    { "id": "f4_6", "to": "f6" }
  ]
}
```

**CRITICAL — Condition rules**:
1. Every outgoing connection ID MUST have a matching key in `conditions`. Missing entries cause runtime errors.
2. The default/fallback branch uses an empty string `""` as its condition value.
3. If there are N connections, there must be exactly N entries in `conditions`.

### TaskEnd (Process End)

```json
{
  "id": "f5",
  "type": "TaskEnd",
  "name": "Success",
  "visual": { "at": { "x": 700, "y": 64 } }
}
```

### ProgramInterface (AI/External Call)

```json
{
  "id": "f6",
  "type": "ProgramInterface",
  "name": "AI Task",
  "config": {
    "javaClass": "com.axonivy.utils.smart.workflow.AgenticProcessCall",
    "userConfig": {
      "system": "You are an AI assistant...",
      "query": "Process this: <%= dev.langchain4j.internal.Json.toJson(in.data) %>",
      "resultType": "package.ResultClass.class",
      "resultMapping": "in.result"
    }
  },
  "visual": { "at": { "x": 600, "y": 64 }, "size": { "width": 128 } },
  "boundaries": [{
    "id": "f6_error",
    "type": "ErrorBoundaryEvent",
    "config": {
      "errorCode": "ivy:error:program:exception",
      "output": {
        "map": {
          "out": "in",
          "out.errorMessage": "\"AI call failed\""
        }
      }
    },
    "connect": [{ "id": "f6e_7", "to": "f7" }]
  }],
  "connect": [{ "id": "f6_8", "to": "f8" }]
}
```

## ID Conventions

**CRITICAL**: Element IDs and Connection IDs share the same namespace and MUST NOT conflict.

### ID Rules

1. **Element IDs**: Use sequential IDs starting from `f0` (e.g., f0, f1, f2, ... f15)
2. **Connection IDs**: Use IDs that DO NOT conflict with element IDs
3. **Recommended pattern**: If elements are f0-f15, use f16+ for connections

### Example ID Assignment

```text
Elements:     f0, f1, f2, f3, f4, f5 (6 elements)
Connections:  f6, f7, f8, f9, f10    (5 connections)
```

## Connection Patterns

### Sequential

```json
"connect": [{ "id": "f16", "to": "f1" }]
```

### With Labels

```json
"connect": [
  { "id": "f22", "to": "f7", "label": { "name": "Yes" } },
  { "id": "f23", "to": "f3", "label": { "name": "No", "segment": 0.51, "offset": { "x": 0, "y": -8 } } }
]
```

- `segment` — position on connection line (0=start, 1=end)
- `offset` — pixel displacement for label

### With Via Points (routing around elements)

```json
"connect": [
  { "id": "f23", "to": "f3", "via": [{ "x": 520, "y": 200 }] }
]
```

