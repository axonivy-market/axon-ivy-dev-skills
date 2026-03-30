# Component Dialog (Type 2 — Reusable Composite Component)

Load this file when **creating a new Component Dialog** (a reusable UI fragment embedded in other pages).

## File Structure

Components go under a `components` subpackage in the namespace path:

```
src_hd/<namespace-path>/components/<ComponentName>/
├── <ComponentName>.xhtml               ← composite component
├── <ComponentName>Data.d.json          ← component data class
└── <ComponentName>Process.p.json       ← HTML_DIALOG logic process
```

- The data class `namespace` = `<package>.components.<ComponentName>` (e.g. `invoice.parser.components.InvoiceReview`)
- The process `config.data` = `<namespace>.components.<ComponentName>.<ComponentName>Data`

## Reference Template

See `template/components/TemplateComponentName/` in this skill folder for all 3 reference files.

## XHTML Structure

Uses `<cc:interface componentType="IvyComponent">` with **NO own form or layout** — the embedding page provides the `<h:form>`:

```xml
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:f="http://xmlns.jcp.org/jsf/core"
  xmlns:h="http://xmlns.jcp.org/jsf/html" xmlns:ui="http://xmlns.jcp.org/jsf/facelets"
  xmlns:cc="http://xmlns.jcp.org/jsf/composite" xmlns:ic="http://ivyteam.ch/jsf/component"
  xmlns:p="http://primefaces.org/ui" xmlns:pe="http://primefaces.org/ui/extensions">
<cc:interface componentType="IvyComponent">
</cc:interface>

<cc:implementation>

  <!-- fields needs to be inside a h:form tag (which is normally added by the outer page) -->

</cc:implementation>

</html>
```
