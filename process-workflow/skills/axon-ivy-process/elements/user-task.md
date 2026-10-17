# UserTask (Human Task + Dialog)

Prefer `UserTask` when a step combines a human task with an HTML dialog. It combines task assignment and dialog display. Use `TaskSwitchEvent` plus `DialogCall` only when the task and UI must be decoupled, such as a task without a UI or a dialog selected dynamically.

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

## Configuration

- `dialog` is the dialog signature; package separators use `.`. For dialog ID and folder naming rules, see `dialog-call.md`.
- `call.map` passes process data to dialog `param.*` inputs.
- `task` configures assignment, task metadata, expiry, and custom fields.
- `output.map` maps dialog `result.*` values back to process data.

The process and dialog have separate data classes. `call.map` and `output.map` are the boundary; data does not cross automatically. See `logic-process.md` -> "CRITICAL - Process Data vs Dialog Data Are Separate".

## Persistence

A `UserTask` is a save point: process data is persisted at task creation and restored when the task is worked. Mark data needed later as `PERSISTENT` (see `axon-ivy-data`) or re-materialize it in `call.code`. Otherwise, non-persistent data arrives as `null` in the dialog.

## Responsible

Supported responsible modes include:

- `ROLES` - assign the task to one or more fixed roles by name
- `ROLE_FROM_ATTRIBUTE` - role name from an expression
- `USER_FROM_ATTRIBUTE` - username from an expression

For fixed role assignment, specify `type: "ROLES"` and a `roles` array:

```json
"responsible": {
  "type": "ROLES",
  "roles": ["Employee", "Manager"]
}
```

## Expiry

Expiry is configured inside `task`:

```json
{
  "task": {
    "name": "Review Document",
    "expiry": {
      "timeout": "new Duration(\"3D\")"
    }
  }
}
```

Use `new Duration("XD")` for days or `new Duration("XH")` for hours, with uppercase units. Do not use lowercase shorthand such as `"3d"` or `"5d"`.

## Custom Fields

Define task custom fields in `config/custom-fields.yaml` before referencing them in `task.customFields`. Use `ivy-yaml-files` for YAML structure and validation.
