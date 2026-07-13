## Error Handling in Processes

### ErrorBoundaryEvent

Attached to elements that may fail (EMail, WebServiceCall). Catches errors and routes to a graceful continuation.

**Location**: Inside the element's `"boundaries"` array.

```json
{
  "id" : "f6",
  "type" : "EMail",
  "name" : "Send notification",
  "config" : { ... },
  "boundaries" : [ {
      "id" : "f7",
      "type" : "ErrorBoundaryEvent",
      "name" : "ivy:error:email",
      "config" : {
        "errorCode" : "ivy:error:email",
        "output" : {
          "code" : "ivy.log.error(\"Can not send email\", error);"
        }
      },
      "visual" : {
        "at" : { "x" : 600, "y" : 96 },
        "labelOffset" : { "x" : -38, "y" : 17 }
      },
      "connect" : [
        { "id" : "f4", "to" : "f1", "via" : [ { "x" : 784, "y" : 96 } ] }
      ]
    } ],
  "connect" : [
    { "id" : "f2", "to" : "f1" }
  ]
}
```

### Common Error Codes

| Error Code | Used On | Description |
|-----------|---------|-------------|
| `ivy:error:email` | `EMail` elements | Email sending failure |
| `ivy:error:webservice:exception` | `WebServiceCall` elements | SOAP web service call failure |

### ErrorBoundaryEvent with Output Mapping

For WebServiceCall errors, you can capture the error message:

```json
{
  "id" : "f4",
  "type" : "ErrorBoundaryEvent",
  "config" : {
    "errorCode" : "ivy:error:webservice:exception",
    "output" : {
      "map" : {
        "out" : "in",
        "out.errorMessage" : "error.getLocalizedMessage()"
      }
    }
  },
  "visual" : {
    "at" : { "x" : 360, "y" : 144 }
  },
  "connect" : [
    { "id" : "f8", "to" : "f1", "via" : [ { "x" : 360, "y" : 192 }, { "x" : 536, "y" : 192 } ] }
  ]
}
```

### ErrorBoundaryEvent Output Types

| Type | Syntax | Use Case |
|------|--------|----------|
| Code (script) | `"output": { "code": "ivy.log.error(...);" }` | Log error and continue |
| Mapping | `"output": { "map": { "out.field": "error.getMessage()" } }` | Capture error details |

### ErrorStartEvent

Used in **callable sub-processes** to handle errors raised during execution. Placed as an alternative start element in the process.

```json
{
  "id" : "f10",
  "type" : "ErrorStartEvent",
  "visual" : {
    "at" : { "x" : 96, "y" : 256 }
  },
  "connect" : [
    { "id" : "f11", "to" : "f1" }
  ]
}
```

This catches any unhandled error in the callable sub-process and routes it to an end element, preventing the parent process from crashing.

### Best Practices

1. **ALWAYS wrap EMail elements** with `ErrorBoundaryEvent` using `ivy:error:email`
2. **ALWAYS wrap WebServiceCall elements** with `ErrorBoundaryEvent` using `ivy:error:webservice:exception`
3. Error boundary connections should lead to:
   - The normal end (`CallSubEnd` or `TaskEnd`) — to continue gracefully
   - A logging script — to capture the error before continuing
4. The `error` variable is automatically available in the error boundary's output code/map
5. Use `error.getLocalizedMessage()` or `error.getMessage()` to capture error details
6. ErrorBoundaryEvent IDs must follow the same uniqueness rules as other element/connection IDs
