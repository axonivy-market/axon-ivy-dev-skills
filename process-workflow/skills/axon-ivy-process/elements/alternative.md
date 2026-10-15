# Alternative (Conditional Branch)

Use `Alternative` to branch the process based on conditions.

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

- Every outgoing connection ID must have a matching key in `conditions`; missing entries cause runtime errors.
- Use an empty string `""` as the default/fallback branch condition.
- The number of entries in `conditions` must equal the number of outgoing connections.
