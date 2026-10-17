# Subprocess Calls and Triggers

Use `ivy-json-files` for JSON structure and schema validation.

- `SubProcessCall` calls a subprocess and receives its results.
- `TriggerCall` starts another process asynchronously without waiting for completion or receiving results.

Examples below omit IDs, layout, and connections.

## Shared Call Rules

For both `SubProcessCall` and `TriggerCall`:

- Use `config.processCall` to identify the target entry.
- Use `config.call.map` when the target declares input parameters, mapping current process data (`in.*`) to target parameters (`param.*`). Omit the entire `call` block when the target has no input parameters.

### Target Path and Signature

Use `Folder/ProcessName:methodName(ParamTypes)`:

- Separate process folders with `/`, not `.`.
- Include the exact parameter types in their declared order.
- Use `()` only when the target has no parameters.

Example:

`hr/onboarding/ExtractEmployeeData:extractEmployeeData(String)`

**Do not confuse path conventions:** `processCall` uses slash-separated process paths; `DialogCall.dialog` uses dot-separated package names.

**For `TriggerCall`, an incomplete signature can fail silently.** Do not omit parameter types or use `()` when the target expects parameters.

## Synchronous Subprocess

A callable subprocess declares `"kind": "CALLABLE_SUB"`, starts with `CallSubStart`, and finishes with `CallSubEnd`.

### Entry and Return Values

Define the subprocess contract on `CallSubStart`:

- `signature` — entry method name.
- `input.params` — input parameter definitions.
- `input.map` — maps incoming `param.*` to subprocess data `out.*`.
- `result.params` — return value definitions.
- `result.map` — maps subprocess data `in.*` to returned `result.*`.

Parameter definitions include `name`, `type`, and `desc`.

Example entry in `documents/CheckDocument`:

```json
{
  "type": "CallSubStart",
  "name": "check(String)",
  "config": {
    "signature": "check",
    "input": {
      "params": [
        { "name": "documentName", "type": "String", "desc": "" }
      ],
      "map": {
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
  }
}
```

The subprocess performs its logic, populates `message`, and reaches `CallSubEnd`. Return mappings belong to `CallSubStart`, not `CallSubEnd`.

### Calling the Subprocess

Use `call.map` to pass inputs and `output.map` to copy returned `result.*` into caller data `out.*`.

```json
{
  "type": "SubProcessCall",
  "name": "Check Document",
  "config": {
    "processCall": "documents/CheckDocument:check(String)",
    "call": {
      "map": {
        "param.documentName": "in.documentName"
      }
    },
    "output": {
      "map": {
        "out.message": "result.message"
      }
    }
  }
}
```

## Asynchronous Trigger

`TriggerCall` starts a process through a triggerable `RequestStart`. It is fire-and-forget: it does not wait for completion and has no output mapping.

### Target Entry

The target `RequestStart` must declare `"triggerable": true`. Its input parameters must match the caller's full signature.

Example entry in `hr/workflow/BusinessProcess`:

```json
{
  "type": "RequestStart",
  "config": {
    "signature": "createLeaveRequest",
    "triggerable": true,
    "input": {
      "params": [
        { "name": "leaveType", "type": "String", "desc": "" },
        { "name": "startDate", "type": "java.time.LocalDate", "desc": "" }
      ],
      "map": {
        "out.leaveType": "param.leaveType",
        "out.startDate": "param.startDate"
      }
    }
  }
}
```

### Triggering the Process

```json
{
  "type": "TriggerCall",
  "name": "Trigger Leave Request",
  "config": {
    "processCall": "hr/workflow/BusinessProcess:createLeaveRequest(String,java.time.LocalDate)",
    "call": {
      "map": {
        "param.leaveType": "in.leaveType",
        "param.startDate": "in.startDate"
      }
    }
  }
}
```

### Task Responsibility

For programmatically triggered starts, use the `SYSTEM` role for the first task. Default to `SYSTEM` when the user has not specified a responsible party:

```json
"responsible": {
  "roles": ["SYSTEM"]
}
```

Do not use `ROLE_FROM_ATTRIBUTE` with an empty script: a programmatic trigger has no initiating user context.
