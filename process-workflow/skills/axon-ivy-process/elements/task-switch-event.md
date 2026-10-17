# TaskSwitchEvent (Human Task)

Use `TaskSwitchEvent` when `UserTask` does not fit, such as a task without a UI or one whose UI is selected dynamically. For a human task with a fixed dialog, prefer `UserTask` instead.

**Critical: use `in1`, not `in`.** Expressions inside `TaskSwitchEvent` that reference process data, including `task.name`, `task.description`, `responsible.script`, `output.code`, and `case.name`, must use `in1`, the first output branch. Using `in` causes `Variable 'in' cannot be resolved`. `UserTask` uses `in` instead.

## Process Data

**Use `in1`, not `in`, when referencing process data.**
This applies to expressions in task and case metadata, `responsible.script`, and `output.code`. Using `in` causes `Variable 'in' cannot be resolved`.

## Example

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

## Configuration

- `task` configures task assignment and metadata.
- `case` configures case metadata when needed.
- `output.code` contains output logic; process data references use `in1`.

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
