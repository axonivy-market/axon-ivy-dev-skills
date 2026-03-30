---
name: axon-ivy-html
description: Rules and best practices for Axon Ivy HTML Dialog implementations including PrimeFaces, PrimeFlex, CSS, JS, and Ivy components.
---

## HTML Dialog File Structure — MANDATORY

Every HTML dialog consists of **3 files, all inside one named subfolder under `src_hd/`**. Never put XHTML in `webContent/` and never put the dialog data class in `dataclasses/`.

```
src_hd/<namespace-path>/<DialogName>/
├── <DialogName>.xhtml               ← the UI template
├── <DialogName>Data.d.json          ← dialog data class
└── <DialogName>Process.p.json       ← HTML_DIALOG logic process
```

- The data class `namespace` = `<package>.<DialogName>` (e.g. `invoice.parser.upload.UploadInvoice`)
- The process `config.data` = `<namespace>.<DialogName>Data` (e.g. `invoice.parser.upload.UploadInvoice.UploadInvoiceData`)

## Dialog Types

Load the appropriate file when **creating a new dialog**:

- Creating a **Template Dialog** (full-page user task) → Load `dialog-template.md`
- Creating a **Component Dialog** (reusable composite component) → Load `dialog-component.md`

## Always Load

These references are needed for every HTML dialog:

- Load `primefaces.md` — JSF & PrimeFaces component rules
- Load `css-js.md` — Styling, layout, icons, CSS & JS rules

## Load When Needed

- Building input forms → Load `form-design.md`
- Using date picker or calendar components (`p:datePicker`) → Load `date-picker.md`
- Using file upload components (`p:fileUpload`) → Load `file-upload.md`
  - Implementing a file upload dialog process from scratch → also Load `logic-process-example.md`
- Working with dialog logic, events, or methods (`#{logic.*}`, `#{data.*}`) → Load `logic-process.md` and `../axon-ivy-process/code.md`
- Creating or updating managed beans for dialogs → Load `managed-bean.md`
- Using Ivy HTML components (`<ic:*>`) → Load `ivy.md`
- Looking up icon names → Refer to `icons.txt`
- Adding/updating UI labels or translations → Use `axon-ivy-cms` skill to create CMS entries
