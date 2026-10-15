# DialogCall (Dialog Display)

Use `DialogCall` to display an HTML dialog without configuring task assignment. It can follow `TaskSwitchEvent` when the human task and UI are separate. For a human task with a fixed dialog, prefer `UserTask`.

## Example

```json
{
  "id": "f2",
  "type": "DialogCall",
  "name": "Edit Employee",
  "config": {
    "dialog": "hr.EmployeeDialog:start(hr.model.Employee)",
    "call": {
      "map": {
        "param.employee": "in.employee"
      }
    },
    "output": {
      "map": {
        "out": "in",
        "out.employee": "result.employee"
      }
    }
  },
  "visual": { "at": { "x": 248, "y": 64 } },
  "connect": [{ "id": "f2_3", "to": "f3" }]
}
```

This example assumes the dialog declares an `employee` start parameter and an `employee` result.

## Configuration and Data Mapping

- `dialog` identifies the dialog and its start signature. Use `.` package separators. See the above example.
- `call.map` maps calling-process data to the dialog's `param.*` start parameters.
- Inside the dialog, `HtmlDialogStart.input.map` maps those parameters into the dialog's own data.
- `output.map` maps the dialog's declared `result.*` values back to calling-process data.

**The calling process and dialog have separate data classes.** Configure both sides of the mapping; passing a parameter does not automatically populate the dialog's data fields.

See `logic-process.md` → "CRITICAL - Process Data vs Dialog Data Are Separate".

## Dialog ID and Project Structure

An HTML dialog uses a process of kind `HTML_DIALOG`. Its XHTML, data class, and process file live together under its directory in `dialog/`.

For example, `dialog/com/example/CmsExample/` contains:

- `CmsExample.xhtml`
- `CmsExampleData.d.json`
- `CmsExampleProcess.p.json`

The process file specifies:

- Kind: `HTML_DIALOG`
- Data class: `com.example.CmsExample.CmsExampleData`

The dialog ID is its directory path relative to `dialog/`, with `/` replaced by `.`:

```json
"dialog": "com.example.CmsExample:start()"
```

Do not append the XHTML, process, or data-class name. For example, `com.example.CmsExample.CmsExample:start()` incorrectly duplicates the final path segment.
