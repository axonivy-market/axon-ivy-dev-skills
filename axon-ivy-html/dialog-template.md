# Template Dialog (Type 1 — Full Page)

Load this file when **creating a new Template Dialog** (a full-page dialog tied to a user task).

## File Structure

```
src_hd/<namespace-path>/<DialogName>/
├── <DialogName>.xhtml               ← the UI template
├── <DialogName>Data.d.json          ← dialog data class
└── <DialogName>Process.p.json       ← HTML_DIALOG logic process
```

- The data class `namespace` = `<package>.<DialogName>` (e.g. `invoice.parser.upload.UploadInvoice`)
- The process `config.data` = `<namespace>.<DialogName>Data` (e.g. `invoice.parser.upload.UploadInvoice.UploadInvoiceData`)

## Reference Template

See `template/TemplateDialogName/` in this skill folder for all 3 reference files.

**Layout file:** `template/layouts/frame-10-full-width.xhtml` — this is the layout referenced by `template="/layouts/frame-10-full-width.xhtml"`. Copy it to `webContent/layouts/` in the target project if it doesn't already exist.

## XHTML Structure

Always use full `<html><h:body>` with the frame layout:

```xml
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:f="http://xmlns.jcp.org/jsf/core"
  xmlns:h="http://xmlns.jcp.org/jsf/html" xmlns:ui="http://xmlns.jcp.org/jsf/facelets"
  xmlns:ic="http://ivyteam.ch/jsf/component" xmlns:p="http://primefaces.org/ui"
  xmlns:pe="http://primefaces.org/ui/extensions">
<h:body>
  <ui:composition template="/layouts/frame-10-full-width.xhtml">
    <ui:define name="title">Dialog Title</ui:define>
    <ui:define name="content">
      <h:form id="form">
        <p:messages />
        <!-- content -->
        <div class="command-btns">
          <p:commandLink id="cancel" actionListener="#{ivyWorkflowView.cancel()}" process="@this" value="Cancel" />
          <p:commandButton id="proceed" actionListener="#{logic.submit}" value="Proceed" update="form" icon="pi pi-check" />
        </div>
      </h:form>
    </ui:define>
  </ui:composition>
</h:body>
</html>
```
