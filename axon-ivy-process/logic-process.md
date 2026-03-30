# Dialog Logic Process Elements

Element types used in HTML Dialog process files (`src_hd/**/*Process.p.json`). These processes handle the logic behind dialog UIs — upload handling, validation, data manipulation, and navigation.

## CRITICAL — End Element Rules

**Choose the correct end element based on whether the flow should exit the dialog:**

| End Element | Behavior | Use For |
|---|---|---|
| `HtmlDialogEnd` | Flow ends, **dialog stays open** | Method flows (upload, removeFile, validate, refresh), start initialization |
| `HtmlDialogExit` | Flow ends, **dialog closes** and returns to calling process | Navigation events (submit, close, cancel) that leave the dialog |

**Rule**: Only use `HtmlDialogExit` when the event is intended to **leave the dialog and continue the calling process**. For all other flows (methods, UI actions), use `HtmlDialogEnd`.

### Correct Examples

```
start()        → Script → HtmlDialogEnd      (dialog opens and stays open)
upload()       → Script → HtmlDialogEnd      (file uploaded, dialog stays open)
removeFile()   → Script → HtmlDialogEnd      (file removed, dialog stays open)
submit         → Script → HtmlDialogExit     (dialog closes, result returned)
close          →          HtmlDialogEnd       (dialog closes without result)
```

### Common Mistake

```
WRONG:  HtmlDialogMethodStart (upload) → Script → HtmlDialogExit
        (dialog would close after upload — user loses their work!)

RIGHT:  HtmlDialogMethodStart (upload) → Script → HtmlDialogEnd
        (upload completes, dialog stays open for user to continue)
```

## HtmlDialogStart (Dialog Entry)

```json
{
  "id": "f0",
  "type": "HtmlDialogStart",
  "name": "start(String)",
  "config": {
    "signature": "start",
    "input": {
      "params": [
        { "name": "callbackUrl", "type": "String" }
      ],
      "map": {
        "out.callbackUrl": "param.callbackUrl"
      },
      "code": "out.dataModel.search();"
    },
    "result": {
      "params": [
        { "name": "project", "type": "package.model.Project", "desc": "" }
      ],
      "map": {
        "result.project": "in.project"
      }
    },
    "guid": "17501D6F0923F1F3"
  },
  "visual": { "at": { "x": 96, "y": 64 } },
  "connect": [{ "id": "f10", "to": "f1" }]
}
```

- `input.params` — parameter definitions
- `input.map` — maps `param.*` to process data
- `input.code` — initialization script
- `result.params` — return value definitions (name, type, desc)
- `result.map` — maps process data `in.*` back to `result.*` for the calling process
- `guid` — unique identifier linking to the dialog component

**CRITICAL — Result section**: Every `HtmlDialogStart` that returns data to a calling process MUST have a `result` section. Without it, the calling process cannot resolve `result.fieldName` in its output mapping, causing `Output 'out.field': Field not found` errors.

## HtmlDialogEnd (Flow End — Dialog Stays Open)

End element for flows that should **not** close the dialog. Used after `HtmlDialogStart` (initialization), `HtmlDialogMethodStart` (UI actions), and `HtmlDialogEventStart` when the event should not navigate away (e.g., close/cancel without result).

```json
{
  "id": "f5",
  "type": "HtmlDialogEnd",
  "name": "",
  "visual": { "at": { "x": 700, "y": 64 } }
}
```

## HtmlDialogExit (Flow End — Dialog Closes)

End element for flows that should **close the dialog** and return control to the calling process. Only use when the event is intended to leave the dialog.

```json
{
  "id": "f4",
  "type": "HtmlDialogExit",
  "name": "",
  "visual": { "at": { "x": 400, "y": 200 } }
}
```

## HtmlDialogMethodStart (Dialog Method)

Entry point for a method callable from the dialog UI via `#{logic.methodName}`. Used for actions like file upload, data loading, validation, and any UI interaction that should keep the dialog open.

### Simple method (no parameters)

```json
{
  "id": "f3",
  "type": "HtmlDialogMethodStart",
  "name": "removeFile()",
  "config": {
    "signature": "removeFile",
    "guid": "15C67E8753E2C68C"
  },
  "visual": { "at": { "x": 96, "y": 200 } },
  "connect": [{ "id": "f12", "to": "f4" }]
}
```

### Method with parameters (e.g., file upload listener)

```json
{
  "id": "f6",
  "type": "HtmlDialogMethodStart",
  "name": "upload(FileUploadEvent)",
  "config": {
    "signature": "upload",
    "input": {
      "params": [
        { "name": "event", "type": "org.primefaces.event.FileUploadEvent", "desc": "" }
      ],
      "map": {
        "out.uploadedFile": "param.event"
      }
    },
    "guid": "1A4E9F78C2F18AB4"
  },
  "visual": { "at": { "x": 96, "y": 352 } },
  "connect": [{ "id": "f18", "to": "f7" }]
}
```

- `input.params` — method parameter definitions
- `input.map` — maps `param.*` to process data fields so subsequent Script elements can access them via `in.*`
- In XHTML, call via `listener="#{logic.upload}"` (PrimeFaces passes the event automatically)

## HtmlDialogEventStart (Dialog Event)

Entry point triggered by a UI event (e.g., submit, close, row selection). Events that navigate away from the dialog end with `HtmlDialogExit`. Events that stay in the dialog end with `HtmlDialogEnd`.

```json
{
  "id": "f6",
  "type": "HtmlDialogEventStart",
  "name": "submit",
  "config": {
    "guid": "1A2B3C4D5E6F7890"
  },
  "visual": { "at": { "x": 96, "y": 336 } },
  "connect": [{ "id": "f14", "to": "f7" }]
}
```

- In XHTML, trigger via `actionListener="#{logic.submit}"`

## Dialog Process Structure

A dialog process file lives in `src_hd/` and typically contains multiple flows:

```json
{
  "$schema": "https://json-schema.axonivy.com/14.0-dev/project/process.json",
  "id": "UNIQUE_HEX_ID",
  "kind": "HTML_DIALOG",
  "config": {
    "data": "package.name.DialogData"
  },
  "elements": [
    // Initialization flow (dialog stays open)
    { "type": "HtmlDialogStart", "name": "start()", ... },
    { "type": "HtmlDialogEnd", ... },

    // Navigation events (dialog closes)
    { "type": "HtmlDialogEventStart", "name": "submit", ... },
    { "type": "HtmlDialogExit", ... },

    // Cancel/close (dialog closes without result)
    { "type": "HtmlDialogEventStart", "name": "close", ... },
    { "type": "HtmlDialogEnd", ... },

    // UI methods (dialog stays open)
    { "type": "HtmlDialogMethodStart", "name": "upload(FileUploadEvent)", ... },
    { "type": "Script", "name": "Save uploaded file", ... },
    { "type": "HtmlDialogEnd", ... },

    { "type": "HtmlDialogMethodStart", "name": "removeFile()", ... },
    { "type": "Script", "name": "Clear uploaded file", ... },
    { "type": "HtmlDialogEnd", ... }
  ]
}
```

## Complete Example: File Upload Dialog Process

A working example of a dialog process that handles file upload, removal, submit, and close:

```json
{
  "$schema": "https://json-schema.axonivy.com/14.0-dev/project/process.json",
  "id": "1A4E9F78C2BDC1A1",
  "kind": "HTML_DIALOG",
  "config": {
    "data": "hr.onboarding.InputUploadForm.InputUploadFormData"
  },
  "elements": [
    {
      "id": "f0",
      "type": "HtmlDialogStart",
      "name": "start()",
      "config": {
        "signature": "start",
        "result": {
          "params": [
            { "name": "inputFile", "type": "java.io.File", "desc": "Uploaded PDF file" }
          ],
          "map": { "result.inputFile": "in.inputFile" }
        },
        "guid": "GUID_START"
      },
      "visual": { "at": { "x": 96, "y": 64 } },
      "connect": [{ "id": "f15", "to": "f1" }]
    },
    {
      "id": "f1",
      "type": "HtmlDialogEnd",
      "visual": { "at": { "x": 224, "y": 64 } }
    },
    {
      "id": "f2",
      "type": "HtmlDialogEventStart",
      "name": "submit",
      "config": { "guid": "GUID_SUBMIT" },
      "visual": { "at": { "x": 96, "y": 160 } },
      "connect": [{ "id": "f16", "to": "f3" }]
    },
    {
      "id": "f3",
      "type": "HtmlDialogExit",
      "visual": { "at": { "x": 224, "y": 160 } }
    },
    {
      "id": "f4",
      "type": "HtmlDialogEventStart",
      "name": "close",
      "config": { "guid": "GUID_CLOSE" },
      "visual": { "at": { "x": 96, "y": 256 } },
      "connect": [{ "id": "f17", "to": "f5" }]
    },
    {
      "id": "f5",
      "type": "HtmlDialogEnd",
      "visual": { "at": { "x": 224, "y": 256 } }
    },
    {
      "id": "f6",
      "type": "HtmlDialogMethodStart",
      "name": "upload(FileUploadEvent)",
      "config": {
        "signature": "upload",
        "input": {
          "params": [
            { "name": "event", "type": "org.primefaces.event.FileUploadEvent", "desc": "" }
          ],
          "map": { "out.uploadedFile": "param.event" }
        },
        "guid": "GUID_UPLOAD"
      },
      "visual": { "at": { "x": 96, "y": 352 } },
      "connect": [{ "id": "f18", "to": "f7" }]
    },
    {
      "id": "f7",
      "type": "Script",
      "name": "Save uploaded file",
      "config": {
        "output": {
          "code": [
            "import org.primefaces.event.FileUploadEvent;",
            "",
            "FileUploadEvent event = in.uploadedFile as FileUploadEvent;",
            "if (event != null && event.getFile() != null) {",
            "  java.io.File tempFile = java.io.File.createTempFile(\"upload_\", \".pdf\");",
            "  java.io.FileOutputStream fos = new java.io.FileOutputStream(tempFile);",
            "  fos.write(event.getFile().getContent());",
            "  fos.close();",
            "  in.inputFile = tempFile;",
            "}",
            "in.uploadedFile = null;"
          ]
        }
      },
      "visual": { "at": { "x": 288, "y": 352 } },
      "connect": [{ "id": "f19", "to": "f8" }]
    },
    {
      "id": "f8",
      "type": "HtmlDialogEnd",
      "visual": { "at": { "x": 480, "y": 352 } }
    },
    {
      "id": "f9",
      "type": "HtmlDialogMethodStart",
      "name": "removeFile()",
      "config": {
        "signature": "removeFile",
        "guid": "GUID_REMOVE"
      },
      "visual": { "at": { "x": 96, "y": 448 } },
      "connect": [{ "id": "f20", "to": "f13" }]
    },
    {
      "id": "f13",
      "type": "Script",
      "name": "Clear uploaded file",
      "config": {
        "output": {
          "code": [
            "if (in.inputFile != null && in.inputFile.exists()) {",
            "  in.inputFile.delete();",
            "}",
            "in.inputFile = null;"
          ]
        }
      },
      "visual": { "at": { "x": 288, "y": 448 } },
      "connect": [{ "id": "f21", "to": "f14" }]
    },
    {
      "id": "f14",
      "type": "HtmlDialogEnd",
      "visual": { "at": { "x": 480, "y": 448 } }
    }
  ]
}
```
