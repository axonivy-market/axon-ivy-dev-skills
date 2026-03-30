---
name: axon-ivy-html
description: Rules and best practices for Axon Ivy HTML Dialog implementations including PrimeFaces, PrimeFlex, CSS, JS, and Ivy components.
---

## Always Load

These references are needed for every HTML dialog:

- Load `primefaces.md` — JSF & PrimeFaces component rules
- Load `css-js.md` — Styling, layout, icons, CSS & JS rules

## Load When Needed

- Building input forms → Load `form-design.md`
- Using date picker or calendar components (`p:datePicker`) → Load `date-picker.md`
- Using file upload components (`p:fileUpload`) → Load `file-upload.md`
- Working with dialog logic, events, or methods (`#{logic.*}`, `#{data.*}`) → Load `logic-process.md` and `../axon-ivy-process/code.md`
- Creating or updating managed beans for dialogs → Load `managed-bean.md`
- Using Ivy HTML components (`<ic:*>`) → Load `ivy.md`
- Looking up icon names → Refer to `icons.txt`
- Adding/updating UI labels or translations → Use `axon-ivy-cms` skill to create CMS entries
