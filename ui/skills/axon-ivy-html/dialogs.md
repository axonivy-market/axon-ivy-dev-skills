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

**Template dialog**

- The data class `namespace` = `<package>.<DialogName>` (e.g. `invoice.parser.upload.UploadInvoice`)
- The process `config.data` = `<namespace>.<DialogName>Data` (e.g. `invoice.parser.upload.UploadInvoice.UploadInvoiceData`)

**Component dialog** — goes under a `components` subpackage in the namespace path:

```
dialog/<namespace-path>/components/<ComponentName>/
├── <ComponentName>.xhtml               ← composite component
├── <ComponentName>Data.d.json          ← component data class
└── <ComponentName>Process.p.json       ← HTML_DIALOG logic process
```

- The data class `namespace` = `<package>.components.<ComponentName>` (e.g. `invoice.parser.components.InvoiceReview`)
- The process `config.data` = `<namespace>.components.<ComponentName>.<ComponentName>Data`

---

## Template Dialog

Load this section when **creating a new Template Dialog** (a full-page dialog tied to a user task).

**Reference files:** `template/TemplateDialogName/` — all 3.

**Layout file:** `template/layouts/frame-10-full-width.xhtml` — this is the layout referenced by
`template="/layouts/frame-10-full-width.xhtml"`. Copy it to `webContent/layouts/` in the target
project if it doesn't already exist.

### XHTML Structure

Copy `template/TemplateDialogName/TemplateDialogName.xhtml` and edit it in place — it is the single
source for the namespace declarations and the `<h:body>` / `<ui:composition>` / `<h:form>` skeleton.

Always use full `<html><h:body>` wrapping a `<ui:composition>` on the frame layout. Put form content
inside `<h:form id="form">` after `<p:messages />`. For field layout inside the form, load
`form-design.md`.

---

## Component Dialog

Load this section when **creating a new Component Dialog** (a reusable UI fragment embedded in other
pages).

**Reference files:** `template/components/TemplateComponentName/` — all 3.

### XHTML Structure

Copy `template/components/TemplateComponentName/TemplateComponentName.xhtml` and edit it in place —
it is the single source for the namespace declarations and the composite skeleton.

Uses `<cc:interface componentType="IvyComponent">` + `<cc:implementation>` with **NO own form,
layout, or `<h:body>`** — the embedding page provides the `<h:form>`.

Rules for component dialogs:

- Only generate `<h:form>` if the parent dialog didn't define one, or there is no parent dialog
- Do NOT generate a messages block
- Only generate form content rows
- Assume the parent dialog already manages form and actions

---

## Embedding a Component — the `<ic:>` tag

To use Axon Ivy HTML components, you must declare the Ivy component namespace in the `<html>` tag:

```xml
xmlns:ic="http://ivyteam.ch/jsf/component"
```

For example, if you have an HTML component named ProjectDetails located in
`dialog/hr/talent/acquisition/component`, you can use it in your HTML dialog as follows:

```xml
<ic:hr.talent.acquisition.component.ProjectDetails />
```
