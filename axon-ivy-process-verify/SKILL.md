---
name: axon-ivy-process-verify
description: Verification checklist for Axon Ivy process files (.p.json). Use this whenever a .p.json file is created, modified, or reviewed — either after axon-ivy-process skill, or when a user asks to check, verify, or fix a process file for errors.
---

**MANDATORY**: Run this checklist on EVERY `.p.json` file after creating or modifying it with the `axon-ivy-process` skill. Read the generated file, then verify each applicable check below. Fix any violations before considering the task done.

## Checklist

### 1. SubProcessCall — Path uses `/` (slash), NOT `.` (dot)

Scan every `SubProcessCall` element. The `processCall` value must use `/` as path separator.

```
WRONG: "processCall": "hr.onboarding.agent.ExtractEmployeeData:extractEmployeeData(String)"
RIGHT: "processCall": "hr/onboarding/agent/ExtractEmployeeData:extractEmployeeData(String)"
```

Note: `DialogCall.dialog` uses `.` (dot) — the opposite convention. Do not mix them up.

### 2. DialogCall / UserTask — Dialog path uses `.` (dot), NOT `/` (slash)

Scan every `DialogCall` and `UserTask` element. The `dialog` value must use `.` as package separator.

```
WRONG: "dialog": "package/DialogName:start()"
RIGHT: "dialog": "package.DialogName:start()"
```

### 3. Expiry timeout — Must use `new Duration(...)` constructor

Scan every `TaskSwitchEvent` and `UserTask` that has an `expiry.timeout`. The value must be a `Duration` constructor, not a shorthand string.

```
WRONG: "timeout": "3d"
WRONG: "timeout": "3D"
WRONG: "timeout": "5h"
RIGHT: "timeout": "new Duration(\"3D\")"
RIGHT: "timeout": "new Duration(\"5H\")"
```

Rule: Capital `D` for days, capital `H` for hours, wrapped in `new Duration("...")`.

### 4. HtmlDialogStart — Must have `result` section if returning data

Scan every `HtmlDialogStart` element. If the calling process reads `result.*` in its output mapping, the dialog's `HtmlDialogStart` MUST declare a `result` section.

```json
// REQUIRED when dialog returns data:
"result": {
  "params": [
    { "name": "project", "type": "package.model.Project", "desc": "" }
  ],
  "map": {
    "result.project": "in.project"
  }
}
```

Missing `result` causes: `Output 'out.field': Field fieldName not found for class <>`.

### 5. Alternative — Every connection must have a matching condition entry

Scan every `Alternative` element. Count the entries in `connect` and the keys in `conditions`. They MUST match.

```
WRONG (3 connections, 2 conditions):
  "conditions": { "c1": "expr1", "c2": "expr2" }
  "connect": [{ "id": "c1" }, { "id": "c2" }, { "id": "c3" }]

RIGHT (3 connections, 3 conditions — default uses ""):
  "conditions": { "c1": "expr1", "c2": "expr2", "c3": "" }
  "connect": [{ "id": "c1" }, { "id": "c2" }, { "id": "c3" }]
```

Rule: Default/fallback branch condition value is `""` (empty string).

### 6. Script elements — No `param.*` usage

Scan every `Script` element's `output.code`. The variable `param` is NOT available in scripts — use `in` instead.

```
WRONG: String name = param.employeeName;
RIGHT: String name = in.employeeName;
```

`param.*` is only available in start element signatures (`RequestStart`, `CallSubStart`, `HtmlDialogStart`).

### 7. Element ID / Connection ID — No duplicates across both

Collect ALL element `id` values and ALL connection `id` values in the file. They share one namespace and MUST NOT collide.

```
WRONG: element id "f5" AND connection id "f5"
RIGHT: elements f0–f5, connections f6–f10
```

### 8. Script imports — Do NOT import types already available in IvyScript

Scan every `Script` element's `output.code` for `import` statements. Several `java.*` types are **pre-imported** in IvyScript and importing them again causes:
> `The import java.io.File collides with File`

Common pre-imported types that MUST NOT be imported:
- `java.io.File` — Ivy shadows this with its own `File` class. Use fully-qualified `java.io.File` instead.
- `java.util.List`, `java.util.Map`, `java.util.Set` — use directly
- `java.lang.*` — always available

```
WRONG: "import java.io.File;",
       "File tempFile = File.createTempFile(...);"

WRONG: "File tempFile = File.createTempFile(...);"
       (Ivy resolves bare "File" to its own class, not java.io.File)

RIGHT: "java.io.File tempFile = java.io.File.createTempFile(...);"
```

Imports that ARE typically needed: `java.nio.file.Files`, `java.nio.file.Path`, `org.primefaces.*`, project-specific classes.

### 9. Script code — Use `as` for casting, NOT Java-style `(Type)` cast

IvyScript uses the `as` keyword for type casting. Java-style parenthesized casts do NOT work.

```
WRONG: "UploadedFile uploaded = (UploadedFile) in.uploadedFile;"
RIGHT: "UploadedFile uploaded = in.uploadedFile as UploadedFile;"
```

### 10. UserTask — Use `in` not `in1` in task expressions

`UserTask` elements do NOT support `in1`. The variable `in1` is specific to `TaskSwitchEvent` output branches. In `UserTask`, always use `in` to access process data in `task.name`, `task.description`, and other expressions.

```
WRONG: "name": "Review - <%= in1.request.getEmployeeFullName() %>"
RIGHT: "name": "Review - <%= in.request.getEmployeeFullName() %>"
```

Error if violated: `Variable 'in1' cannot be resolved`

### 11. Visual layout — Elements must be well aligned

Verify that all elements in the process have consistent visual alignment:

- **Same-lane elements** must share the same `y` coordinate (e.g., all main flow elements at `y: 64`).
- **Horizontal spacing** between sequential elements should be consistent (~128–160px apart on the x-axis). Wide elements (`"size": { "width": 128 }`) need more spacing to avoid overlap.
- **Branch lanes** must use distinct, consistent `y` values (e.g., main flow `y: 64`, first branch `y: 192`, second branch `y: 320`).
- **Via points** on connections to branches must align with the branching element's `x` and the target lane's `y`.

```
WRONG (misaligned y in same lane):
  f1: { "x": 200, "y": 64 }
  f2: { "x": 400, "y": 80 }   ← y differs

WRONG (overlapping elements):
  f1: { "x": 200, "y": 64 }, "size": { "width": 128 }
  f2: { "x": 280, "y": 64 }   ← overlaps with f1 (200+128 > 280)

RIGHT (consistent alignment and spacing):
  f1: { "x": 200, "y": 64 }, "size": { "width": 128 }
  f2: { "x": 400, "y": 64 }
  f3: { "x": 560, "y": 64 }
```

### 12. TriggerCall — `processCall` must include full parameter type signature

Scan every `TriggerCall` element. If the target `RequestStart` has parameters, the `processCall` value MUST include the exact parameter types. Omitting them or using empty `()` causes the trigger to fail silently.

```
WRONG: "processCall": "hr/workflow/BusinessProcess:createLeaveRequest"
WRONG: "processCall": "hr/workflow/BusinessProcess:createLeaveRequest()"
RIGHT: "processCall": "hr/workflow/BusinessProcess:createLeaveRequest(String,java.time.LocalDate,java.time.LocalDate,String)"
```

Also verify that the target `RequestStart` has `"triggerable": true` set in its config, and that its first task's `responsible` uses `SYSTEM`:

```json
// WRONG — no user context when triggered programmatically
"responsible": { "type": "ROLE_FROM_ATTRIBUTE", "script": "" }

// RIGHT
"responsible": { "roles": ["SYSTEM"] }
```

### 13. Alternative — Every outgoing connection must have a label

Scan every `Alternative` element. Each connection in `connect` MUST have a `label` with a `name` describing the decision branch, so users can understand the flow.

```
WRONG (no labels):
  "connect": [
    { "id": "c1", "to": "f2" },
    { "id": "c2", "to": "f3" },
    { "id": "c3", "to": "f4" }
  ]

RIGHT (all connections labeled):
  "connect": [
    { "id": "c1", "to": "f2", "label": { "name": "Approved" } },
    { "id": "c2", "to": "f3", "label": { "name": "Returned" } },
    { "id": "c3", "to": "f4", "label": { "name": "Rejected" } }
  ]
```

### 14. Script code — Do NOT use `var` for local variables

IvyScript does NOT support the `var` keyword for type inference. Always declare explicit types.

```
WRONG: "var caseUuid = ivy.case().uuid().toString();"
RIGHT: "String caseUuid = ivy.case().uuid().toString();"

WRONG: "var results = someService.findAll();"
RIGHT: "List results = someService.findAll();"
```

Error if violated: `Class var not found`
