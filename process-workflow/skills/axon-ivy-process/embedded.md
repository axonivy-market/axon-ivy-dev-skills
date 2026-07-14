# Embedded Process

Container element that groups related elements into a visual block.

## EmbeddedProcess

```json
{
  "id": "S10",
  "type": "EmbeddedProcess",
  "name": "Validate and upload document",
  "elements": [
    {
      "id": "S10-f0",
      "type": "EmbeddedStart",
      "name": "",
      "visual": { "at": { "x": 96, "y": 64 } },
      "connect": [{ "id": "S10-f10", "to": "S10-f1" }]
    },
    {
      "id": "S10-f1",
      "type": "Script",
      "name": "Validate",
      "config": {
        "output": {
          "code": ["in.isValid = in.document != null;"]
        }
      },
      "visual": { "at": { "x": 256, "y": 64 } },
      "connect": [{ "id": "S10-f11", "to": "S10-f2" }]
    },
    {
      "id": "S10-f2",
      "type": "EmbeddedEnd",
      "name": "",
      "visual": { "at": { "x": 416, "y": 64 } }
    }
  ],
  "visual": { "at": { "x": 400, "y": 128 } },
  "connect": [{ "id": "f20", "to": "f5" }]
}
```

## ID Convention

Elements inside an EmbeddedProcess use the parent ID as prefix:

- Parent: `S10`
- Children: `S10-f0`, `S10-f1`, `S10-f2`
- Child connections: `S10-f10`, `S10-f11`

## Structure

- `EmbeddedStart` — entry point inside the container
- `EmbeddedEnd` — exit point inside the container
- Any element types can be placed between them
- The parent `EmbeddedProcess` has its own `connect` for the outgoing flow
