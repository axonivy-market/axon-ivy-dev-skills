# RequestStart (Entry Point)

`RequestStart` defines the process entry point, its signature, and optional request, case, and start metadata.

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

Before adding `customFields`, use `ivy-yaml-files` to define the fields in `config/custom-fields.yaml` under `Cases:` or `Starts:` as appropriate.

For mapping request parameters to process data, see `code.md` -> "RequestStart Input Mapping".
