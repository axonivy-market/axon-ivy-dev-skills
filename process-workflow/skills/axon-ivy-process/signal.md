# Signal Start Event

Process entry triggered by a signal code, typically used for side-step processes and event-driven workflows.

## SignalStartEvent

```json
{
  "id": "f0",
  "type": "SignalStartEvent",
  "name": "Signal side step",
  "config": {
    "signalCode": "com:axonivy:portal:sideStep:askMoreDetails",
    "output": {
      "code": "import ch.ivyteam.ivy.security.ISecurityMember;\nISecurityMember member = ivy.security.members().findById(data.getSecurityMemberId());"
    }
  },
  "visual": { "at": { "x": 96, "y": 64 } },
  "connect": [{ "id": "f10", "to": "f1" }]
}
```

- `signalCode` — unique signal identifier using colon-separated namespace
- `output.code` — script executed when signal is received

## Signal Code Convention

Use reverse-domain colon-separated naming:

```text
com:company:module:feature:action
```

Examples:

- `com:axonivy:portal:sideStep:askMoreDetails`
- `com:example:hr:employee:onboarded`
- `com:example:order:payment:received`
