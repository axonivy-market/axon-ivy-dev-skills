# Subprocess Elements

## SubProcessCall (Call a Subprocess)

```json
{
  "id": "f3",
  "type": "SubProcessCall",
  "name": "Upload Document Checker",
  "config": {
    "processCall": "Functional Processes/UploadDocumentItemChecker:call(IvyDocument)",
    "call": {
      "map": {
        "param.uploadFile": "in.uploadedFile"
      }
    },
    "output": {
      "map": {
        "out.message": "result.message"
      }
    }
  },
  "visual": { "at": { "x": 400, "y": 64 } },
  "connect": [{ "id": "f10", "to": "f4" }]
}
```

- `processCall` — path to subprocess signature: `"Folder/ProcessName:methodName(ParamTypes)"`
- `call.map` — maps current data to subprocess `param.*`
- `output.map` — maps subprocess `result.*` back to current data

**CRITICAL — Path separator rule**: `processCall` uses `/` (slash) separators for process paths, NOT `.` (dot).

```text
WRONG: "hr.onboarding.agent.ExtractEmployeeData:extractEmployeeData(String)"
RIGHT: "hr/onboarding/agent/ExtractEmployeeData:extractEmployeeData(String)"
```

Note: `DialogCall.dialog` uses `.` (dot) package separators — do NOT confuse the two conventions.

## CallSubStart (Callable Subprocess Entry)

Used in processes with `"kind": "CALLABLE_SUB"`. Defines the entry point that other processes call.

```json
{
  "id": "f0",
  "type": "CallSubStart",
  "name": "call(ICase,String)",
  "config": {
    "signature": "call",
    "input": {
      "params": [
        { "name": "businessCase", "type": "ch.ivyteam.ivy.workflow.ICase", "desc": "" },
        { "name": "documentName", "type": "String", "desc": "" }
      ],
      "map": {
        "out.businessCase": "param.businessCase",
        "out.documentName": "param.documentName"
      }
    },
    "result": {
      "params": [
        { "name": "message", "type": "String", "desc": "" }
      ],
      "map": {
        "result.message": "in.message"
      }
    }
  },
  "visual": { "at": { "x": 96, "y": 64 } },
  "connect": [{ "id": "f10", "to": "f1" }]
}
```

- `input.params` — parameter definitions (name, type, desc)
- `input.map` — maps `param.*` to process data `out.*`
- `result.params` — return value definitions
- `result.map` — maps process data `in.*` back to `result.*`

## CallSubEnd (Callable Subprocess Exit)

```json
{
  "id": "f5",
  "type": "CallSubEnd",
  "name": "",
  "visual": { "at": { "x": 700, "y": 64 } }
}
```

## TriggerCall (Start Another Process Asynchronously)

Used to trigger a `RequestStart` process programmatically. The target `RequestStart` MUST have `"triggerable": true`.

```json
{
  "id": "f8",
  "type": "TriggerCall",
  "name": "Trigger Leave Request",
  "config": {
    "processCall": "hr/workflow/BusinessProcess:createLeaveRequest(String,java.time.LocalDate,java.time.LocalDate,String)",
    "call": {
      "map": {
        "param.leaveType": "in.leaveType",
        "param.startDate": "in.startDate",
        "param.endDate": "in.endDate",
        "param.reason": "in.reason"
      }
    }
  },
  "visual": { "at": { "x": 288, "y": 408 } },
  "connect": [{ "id": "f19", "to": "f9" }]
}
```

**CRITICAL — Full parameter type signature required**: `processCall` MUST include the exact parameter types in the signature, matching the `RequestStart` params. Omitting them or using `()` causes the trigger to fail silently.

```text
WRONG: "processCall": "hr/workflow/BusinessProcess:createLeaveRequest"
WRONG: "processCall": "hr/workflow/BusinessProcess:createLeaveRequest()"
RIGHT: "processCall": "hr/workflow/BusinessProcess:createLeaveRequest(String,java.time.LocalDate,java.time.LocalDate,String)"
```

**Target `RequestStart` must declare `"triggerable": true`**:

```json
{
  "type": "RequestStart",
  "config": {
    "signature": "createLeaveRequest",
    "triggerable": true,
    "input": {
      "params": [
        { "name": "leaveType", "type": "String", "desc": "..." },
        { "name": "startDate", "type": "java.time.LocalDate", "desc": "..." }
      ],
      "map": {
        "out.leaveType": "param.leaveType",
        "out.startDate": "param.startDate"
      }
    }
  }
}
```

- `processCall` — path uses `/` (slash) separators, same as `SubProcessCall`
- `call.map` — maps current process data to the target process `param.*` inputs
- TriggerCall is **fire-and-forget** (async): it does not wait for the triggered process to complete and returns no output

**CRITICAL — Target `RequestStart` task responsible must be `SYSTEM`**: When a `RequestStart` is triggered programmatically via `TriggerCall` (not started by a user from the portal), its first task's `responsible` must use the `SYSTEM` role. If no responsible is specified by the user, default to `SYSTEM`.

```json
// WRONG — no user context when triggered programmatically
"responsible": {
  "type": "ROLE_FROM_ATTRIBUTE",
  "script": ""
}

// RIGHT — system-initiated trigger
"responsible": {
  "roles": ["SYSTEM"]
}
```

## SUB Process Structure

A callable subprocess uses `"kind": "CALLABLE_SUB"`:

```json
{
  "$schema": "https://json-schema.axonivy.com/14.0-dev/project/process.json",
  "id": "UNIQUE_HEX_ID",
  "kind": "CALLABLE_SUB",
  "config": {
    "data": "package.name.DataClass"
  },
  "elements": [
    { "type": "CallSubStart", ... },
    { "type": "Script", ... },
    { "type": "CallSubEnd", ... }
  ]
}
```
