---
name: axon-ivy-primefaces-verify
description: Verification checklist for PrimeFaces components — column widths, table layout, AJAX updates, and common rendering pitfalls.
---

**MANDATORY**: Run this checklist after creating or modifying any PrimeFaces `.xhtml` dialog. Read the XHTML and CSS, then verify each check below. Fix any violations before considering the task done.

## Checklist

### 1. Column Width — Use `width` attribute with percentages, not CSS fixed pixels

Set column widths via the `width` attribute on `p:column` using percentages. Do NOT use CSS `width: Npx` on column style classes.

```xhtml
<!-- WRONG -->
<p:column headerText="Name" styleClass="col-name">  <!-- relies on .col-name { width: 280px } -->

<!-- RIGHT -->
<p:column headerText="Name" width="35%">
```

Action columns (buttons only) should have no `width` attribute — use `white-space: nowrap` in CSS to shrink to content.

---

### 2. Column Width — Size based on intended content

Choose percentages based on what the column displays:

| Content Type | Typical Width |
|---|---|
| Name / identifier / description (case name, task name, UUID) | 30–40% |
| Date / timestamp | 12–15% |
| Short numeric / badge (count, tokens) | 7–10% |
| Model name / enum | 12–18% |
| Action button(s) | fit-content (no `width`) |

The total of all explicit widths should stay under 100%.

---

### 3. AJAX Update Targets — Use `<h:panelGroup id>`, not `<div id>`

When using `update="someId"` on a command button or AJAX listener, the target must be a JSF component with an `id`. Plain HTML `<div id>` elements are not in the JSF component tree and will silently fail to re-render.

```xhtml
<!-- WRONG — plain div, not updatable by AJAX -->
<div id="table-section">...</div>

<!-- RIGHT — JSF component, fully updatable -->
<h:panelGroup id="table-section" layout="block">...</h:panelGroup>
```

---

### 4. Component IDs — Use kebab-case

All `id` attributes on JSF/PrimeFaces components must use kebab-case.

```xhtml
<!-- WRONG -->
<h:panelGroup id="tableSection" ...>
<h:form id="mainForm" ...>

<!-- RIGHT -->
<h:panelGroup id="table-section" ...>
<h:form id="main-form" ...>
```

---

### 5. Process/Update Scope on Buttons

Verify `process` and `update` attributes on `<p:commandButton>` and `<p:ajax>`:

- **Submit buttons** (Save, Approve): `process="@form"` and `update="@form"` (or specific panel IDs)
- **Action-only buttons** (Cancel, Close): `process="@this"` to skip validation, `update` as needed
- **Inline AJAX** (toggle, filter): `process="@this"` with targeted `update` IDs

```xhtml
<!-- WRONG — Cancel triggers full form validation -->
<p:commandButton value="Cancel" actionListener="#{logic.cancel}" process="@form" />

<!-- RIGHT — Cancel skips validation -->
<p:commandButton value="Cancel" actionListener="#{logic.cancel}" process="@this" immediate="true" />
```

---

### 6. Missing `id` on Components Referenced by `update`

Every component ID referenced in an `update="..."` attribute must exist in the page. Scan all `update` attributes and verify each referenced ID has a matching component.

```xhtml
<!-- WRONG — "detail-panel" doesn't exist anywhere in the page -->
<p:commandButton update="detail-panel" />

<!-- RIGHT — target exists -->
<h:panelGroup id="detail-panel" layout="block">...</h:panelGroup>
<p:commandButton update="detail-panel" />
```

---

### 7. Form Nesting — No nested `<h:form>` tags

JSF does not support nested forms. Scan for `<h:form>` inside another `<h:form>` — this causes silent submission failures.

```xhtml
<!-- WRONG — nested forms -->
<h:form id="outer-form">
  <h:form id="inner-form">...</h:form>
</h:form>

<!-- RIGHT — single form or separate forms -->
<h:form id="main-form">...</h:form>
```

---

### 8. EL Operator Syntax — Use word operators, not symbols

In JSF EL expressions, use word-based logical operators:

```xhtml
<!-- WRONG -->
<p:panel rendered="#{data.status != null && data.status == 'ACTIVE'}">

<!-- RIGHT -->
<p:panel rendered="#{data.status != null and data.status == 'ACTIVE'}">
```

| Use | Instead of |
|-----|-----------|
| `and` | `&&` |
| `or` | `\|\|` |
| `not` | `!` |

---

### 9. No Inline Styles or Scripts

Scan for `style="..."` on components and `<script>` blocks in the XHTML. Both are forbidden.

- Styles must go in an external CSS file (see `axon-ivy-html` skill, `css-js.md`)
- JavaScript must go in an external JS file

---

### 10. DataTable sorting — `sortBy`, NOT `sortField`

PrimeFaces 14 uses `sortBy` with an EL expression on the row variable. The legacy `sortField` attribute is silently ignored.

```xhtml
<!-- WRONG -->
<p:dataTable value="#{bean.projects}" var="proj" sortField="sortOrder">

<!-- RIGHT -->
<p:dataTable value="#{bean.projects}" var="proj" sortBy="#{proj.sortOrder}">
```

---

### 11. `<p:tooltip for="...">` — target must be a JSF component

`<p:tooltip>` resolves the target via the JSF component tree. Plain HTML elements (`<span>`, `<div>`, `<i>`) have no client ID in that tree, so the tooltip silently fails to attach. Wrap the icon/anchor in a JSF component (typically `<h:panelGroup>`).

```xhtml
<!-- WRONG -->
<span id="info-icon" class="pi pi-info-circle" />
<p:tooltip for="info-icon" value="..." />

<!-- RIGHT -->
<h:panelGroup id="info-icon" styleClass="pi pi-info-circle" />
<p:tooltip for="info-icon" value="..." />
```

---

### 12. `update` paths — no `<p:dialog>` ID prefix

`<p:dialog>` is **not** a NamingContainer (unlike `<p:tabView>` / `<p:tab>`). Components inside a dialog do **not** carry the dialog ID in their client ID. Prefixing them in `update` makes the path unresolvable.

```xhtml
<p:dialog id="quick-alloc-dialog">
  <h:panelGroup id="quick-pt" layout="block">...</h:panelGroup>
</p:dialog>

<!-- WRONG -->
<p:commandButton update="quick-alloc-dialog:quick-pt" />

<!-- RIGHT -->
<p:commandButton update="quick-pt" />
<!-- or absolute from the form: -->
<p:commandButton update=":main-form:quick-pt" />
```

---

### 13. `<p:panelGrid columns="N">` — direct children must be JSF components

`<p:panelGrid columns="N">` distributes its **direct children** across N columns. A plain HTML `<div>` is rendered but is not a JSF component, breaking the column count and shifting all subsequent cells. Wrap layout containers in `<h:panelGroup layout="block">`.

```xhtml
<!-- WRONG — <div> shifts subsequent cells -->
<p:panelGrid columns="2">
  <p:outputLabel value="Name" />
  <div class="flex">
    <p:inputText value="#{bean.name}" />
    <p:commandButton icon="pi pi-search" />
  </div>
</p:panelGrid>

<!-- RIGHT -->
<p:panelGrid columns="2">
  <p:outputLabel value="Name" />
  <h:panelGroup layout="block" styleClass="flex">
    <p:inputText value="#{bean.name}" />
    <p:commandButton icon="pi pi-search" />
  </h:panelGroup>
</p:panelGrid>
```
