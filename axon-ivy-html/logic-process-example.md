# Dialog Process: File Upload — Complete Example

Load this file when **implementing a new file upload dialog process from scratch**.

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
