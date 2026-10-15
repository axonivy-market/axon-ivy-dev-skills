# Script (Code Execution)

Use a `Script` element to execute IvyScript in a process.

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
        "ivy.case.name = \\\"Case: \\\" + in.name;"
      ]
    },
    "sudo": true
  },
  "visual": { "at": { "x": 416, "y": 64 } },
  "connect": [{ "id": "f3_4", "to": "f4" }]
}
```

`sudo: true` is optional and runs the script with elevated permissions.

For IvyScript rules and code patterns, load `code.md` when this element or another IvyScript expression is present.
