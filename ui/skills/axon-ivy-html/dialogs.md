# Dialog Types

Two kinds of HTML dialog. Both use the same 3-file structure; they differ in the XHTML root.

| | Template Dialog | Component Dialog |
| --- | --- | --- |
| Purpose | Full page tied to a user task | Reusable fragment embedded in other pages |
| XHTML root | `<h:body><ui:composition template="/layouts/…">` | `<cc:interface componentType="IvyComponent">`, **no** `<h:body>` |
| Own `<h:form>` | Yes | No — the embedding page provides it |
| `<p:messages>` | Yes | No — the embedding page owns them |

## File Structure

```
dialog/<namespace-path>/<DialogName>/
├── <DialogName>.xhtml               ← the UI
├── <DialogName>Data.d.json          ← dialog data class
└── <DialogName>Process.p.json       ← HTML_DIALOG logic process
```

- Data class `namespace` = the full folder path, dot-separated, ending with the dialog name
  (e.g. `invoice.parser.upload.UploadInvoice`)
- Process `config.data` = `<namespace>.<DialogName>Data`
  (e.g. `invoice.parser.upload.UploadInvoice.UploadInvoiceData`) — the dialog name appears **once**
  in the namespace, then again only as the `…Data` suffix.

Component dialogs are grouped under a `components` subpackage by convention so they are easy to tell
apart from full-page dialogs — a convention, not a requirement.

---

## Template Dialog

**Reference files:** `template/TemplateDialogName/` (all 3).

**Layout:** `template/layouts/frame-10-full-width.xhtml` — the layout referenced by
`template="/layouts/frame-10-full-width.xhtml"`. Copy it to `webContent/layouts/` in the target
project if it isn't already there.

Copy `template/TemplateDialogName/TemplateDialogName.xhtml` and edit it in place — it is the single
source for the namespace declarations and the `<h:body>` / `<ui:composition>` / `<h:form>` skeleton.
Put form content inside `<h:form id="form">` after `<p:messages />`. For field layout and the action
row, load `form-design.md` — the template's button block is its *Standard Button Pattern* verbatim.

### Wiring rules

- **Event names must match.** `#{logic.submit}` only resolves if `<DialogName>Process.p.json` contains an `HtmlDialogEventStart` with `"name": "submit"` — same for `close` and any event you add.
- The reference process defines two events: `close` (Cancel) and `submit` (Submit), both ending in `HtmlDialogExit`.
- `#{data.*}` binds to fields of `<DialogName>Data`; `#{logic.*}` binds to the process events/methods.

---

## Component Dialog

**Reference files:** `template/components/TemplateComponentName/` (all 3).

Copy `template/components/TemplateComponentName/TemplateComponentName.xhtml` and edit it in place.
Uses `<cc:interface componentType="IvyComponent">` + `<cc:implementation>` with **no own form,
layout, or `<h:body>`**. Generate form content rows only — no messages block, no action buttons; the
embedding page owns those.

### Declaring attributes

Inputs the embedding page passes in are declared in `<cc:interface>` and read via `#{cc.attrs.*}`:

```xml
<cc:interface componentType="IvyComponent">
  <cc:attribute name="bean" required="true" />
  <cc:attribute name="readOnly" type="java.lang.Boolean" default="false" />
</cc:interface>
```

---

## Embedding a Component — the `<ic:>` tag

Declare the Ivy component namespace in the `<html>` tag:

```xml
xmlns:ic="http://ivyteam.ch/jsf/component"
```

The tag name is the component's folder path below `dialog/`, dot-separated, ending with the
component name. A component at
`dialog/hr/talent/acquisition/components/ProjectDetails/ProjectDetails.xhtml` is used as:

```xml
<ic:hr.talent.acquisition.components.ProjectDetails bean="#{projectBean}" readOnly="true" />
```

The `dialog` folder name itself is **not** part of the tag name, and the component name appears
exactly **once** — do not repeat it as a trailing class segment.
