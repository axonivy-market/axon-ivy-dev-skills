---
name: axon-ivy-html
description: Rules and best practices for Axon Ivy HTML Dialog implementations including PrimeFaces, PrimeFlex, CSS, JS, and Ivy components.
---

## HTML Dialog File Structure — MANDATORY

Every HTML dialog consists of **3 files, all inside one named subfolder under `dialog/`**. Never put dialog XHTML in `webContent/` and never put the dialog data class in `dataclass/`.

```
dialog/<namespace-path>/<DialogName>/
├── <DialogName>.xhtml               ← the UI template
├── <DialogName>Data.d.json          ← dialog data class
└── <DialogName>Process.p.json       ← HTML_DIALOG logic process
```

- The data class `namespace` = `<package>.<DialogName>` (e.g. `invoice.parser.upload.UploadInvoice`)
- The process `config.data` = `<namespace>.<DialogName>Data` (e.g. `invoice.parser.upload.UploadInvoice.UploadInvoiceData`)

## Dialog Types

Creating or editing a dialog of either type (full-page Template Dialog, or reusable Component
Dialog) → Load `dialogs.md`.

## Always Load

These references are needed for every HTML dialog:

- Load `primefaces.md` — JSF & PrimeFaces component rules
- Load `css-js.md` — Styling, layout, icons, CSS & JS rules

## Load When Needed

- Building input forms → Load `form-design.md`
- Using date picker or calendar components (`p:datePicker`) → Load `date-picker.md`
- Using file upload components (`p:fileUpload`) → Load `file-upload.md`
- Working with dialog logic, events, or methods (`#{logic.*}`, `#{data.*}`) → Load `logic-process.md` and `code.md` from the `axon-ivy-process` skill
- Creating or updating managed beans for dialogs → Load `managed-bean.md`
- Using Ivy HTML components (`<ic:*>`) → Load `dialogs.md`
- Checking finished PrimeFaces markup → Use the `axon-ivy-primefaces-verify` skill
- Looking up icon names → Refer to `icons.txt`
- Adding/updating UI labels or translations → Use `axon-ivy-cms` skill to create CMS entries
