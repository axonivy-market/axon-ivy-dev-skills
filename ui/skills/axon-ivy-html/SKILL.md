---
name: axon-ivy-html
description: Rules and best practices for Axon Ivy HTML Dialog implementations including PrimeFaces, PrimeFlex, CSS, JS, and Ivy components.
---

## HTML Dialog Structure — MANDATORY

Every HTML Dialog must contain these 3 files in the same named folder under `dialog/`:

```text
dialog/<namespace-path>/<DialogName>/
├── <DialogName>.xhtml
├── <DialogName>Data.d.json
└── <DialogName>Process.p.json
```

Never:

* place dialog XHTML in `webContent/`
* place the dialog data class in `dataclass/`

Naming:

```text
Data class namespace:
<package>.<DialogName>

Process config.data:
<package>.<DialogName>.<DialogName>Data
```

Example:

```text
invoice.parser.upload.UploadInvoice
invoice.parser.upload.UploadInvoice.UploadInvoiceData
```

## Required References

UI framework: PrimeFaces 15.0.18 (`jakarta` classifier)

For every HTML Dialog, load:

* `dialogs.md` — dialog types, templates, components, and Ivy `<ic:*>` components
* `primefaces.md` — JSF and PrimeFaces rules
* `css-js.md` — layout, styling, icons, CSS, and JavaScript

## Load by Feature

* Input forms → `form-design.md`
* `p:datePicker` → `date-picker.md`
* `p:fileUpload` → `file-upload.md`
* Managed beans → `managed-bean.md`
* `#{logic.*}`, `#{data.*}`, dialog events, or process methods →
  `logic-process.md` and `code.md` from `axon-ivy-process`

## Related Skills

* Validate finished PrimeFaces markup → `axon-ivy-primefaces-verify`
* Add or update UI labels/translations → `axon-ivy-cms`
* Look up icon names → `icons.txt`
