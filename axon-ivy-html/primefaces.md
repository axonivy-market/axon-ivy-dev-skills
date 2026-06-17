# PrimeFaces & JSF Components

Rules and best practices for generating JSF and PrimeFaces elements for Axon Ivy HTML Dialog.

## Best Practices

### Component availability — not every PrimeReact/NG component is a PrimeFaces (JSF) tag

The PrimeFaces build bundled with Ivy 14 has **no `<p:inputGroup>` / `<p:inputGroupAddon>` tags** — using
them fails at render with `TagException: no tag was defined for name: inputGroup`. For a leading-icon
field, build the group with CSS instead of the component:

```xml
<span class="my-inputgroup">
  <span class="my-inputgroup-addon"><i class="pi pi-user"></i></span>
  <p:inputText id="firstName" value="#{data.bean.customer.firstName}" />
</span>
```

…styled in your project CSS (`.my-inputgroup{display:flex} .my-inputgroup-addon{…border-right:0} .my-inputgroup input{flex:1;width:100%;border-top-left-radius:0;border-bottom-left-radius:0}`). When in doubt about a tag, confirm it exists in this PrimeFaces version before using it — `mvn` does not catch a missing tag, only Designer/runtime does.

### JSF Component Usage

Prefer JSF components (`h:*`) over raw HTML in these cases:

- `<h:form>` for JSF forms
- `<h:outputText>` for rendering text

Expression Language (EL) rules:

- Use string-based operators:
  - `or` instead of `||`
  - `and` instead of `&&`
  - `not` instead of `!`
- Always use `#{}` for Ivy data binding.

### PrimeFaces Component Usage

Prefer PrimeFaces components (`p:*`) over raw HTML inputs when possible. Use:

- `<p:inputText>` for single-line text input
- `<p:inputTextarea>` for multiline text
- `<p:selectOneMenu>` for dropdown selection
- `<p:selectOneRadio>` for radio button groups
- `<p:selectManyCheckbox>` for multi-select checkboxes
- `<p:selectBooleanCheckbox>` for boolean values
- `<p:datePicker>` for date and date-time input (do NOT use the older `<p:calendar>`)
- `<p:commandButton>` for primary actions (Submit, Approve, Save)
- `<p:commandLink>` for secondary actions (Cancel, Close, Back)

## Rules

### ID and naming rules

- All components must have explicit id attributes.
- Use kebab-case (hyphen-case) for IDs.
- Do not use spaces or special characters in IDs.
- Use camelCase for `widgetVar` and `name` attributes.

### Rendering & Conditional Rules

- Avoid JSTL (c:if, c:forEach) unless explicitly requested.
- Prefer PrimeFaces iteration component `<ui:repeat>` when needed.

---

## Common Pitfalls (PrimeFaces 14)

### DataTable sorting — use `sortBy`, not `sortField`

PrimeFaces 14 binds the sort target with `sortBy="#{...}"` (an EL expression on the row variable). The legacy `sortField` attribute is not recognized.

```xhtml
<!-- WRONG (PrimeFaces 14) -->
<p:dataTable value="#{bean.projects}" var="proj" sortField="sortOrder">

<!-- RIGHT -->
<p:dataTable value="#{bean.projects}" var="proj" sortBy="#{proj.sortOrder}">
```

### Tooltip target must be a JSF component

`<p:tooltip for="...">` resolves the target via the JSF component tree. Plain HTML elements (`<span>`, `<div>`) have no client ID in that tree, so the tooltip silently fails to attach.

```xhtml
<!-- WRONG — span is not a JSF component -->
<span id="info-icon" class="pi pi-info-circle" />
<p:tooltip for="info-icon" value="..." />

<!-- RIGHT — h:panelGroup is a JSF component with a real client ID -->
<h:panelGroup id="info-icon" styleClass="pi pi-info-circle" />
<p:tooltip for="info-icon" value="..." />
```

### `<p:dialog>` is NOT a NamingContainer

Unlike `<p:tabView>` / `<p:tab>`, a `<p:dialog>` does not create a JSF naming scope. IDs of components inside the dialog stay flat under the surrounding form. Do **not** prefix them with the dialog ID in `update` attributes.

```xhtml
<p:dialog id="quick-alloc-dialog">
  <h:panelGroup id="quick-pt" layout="block">...</h:panelGroup>
</p:dialog>

<!-- WRONG — "quick-alloc-dialog:quick-pt" does not exist -->
<p:commandButton update="quick-alloc-dialog:quick-pt" />

<!-- RIGHT -->
<p:commandButton update="quick-pt" />
<!-- or absolute: -->
<p:commandButton update=":main-form:quick-pt" />
```

### `<p:panelGrid columns="N">` — wrap layout `<div>`s in `<h:panelGroup>`

`<p:panelGrid columns="N">` distributes its **direct children** across N columns and counts every direct child as one cell. A plain HTML `<div>` is not a JSF component but still renders as a child element, breaking the column count and shifting all subsequent cells.

```xhtml
<!-- WRONG — <div> shifts subsequent cells -->
<p:panelGrid columns="2">
  <p:outputLabel value="Name" />
  <div class="flex">
    <p:inputText value="#{bean.name}" />
    <p:commandButton icon="pi pi-search" />
  </div>
  <!-- next label/input now lands in the wrong column -->
</p:panelGrid>

<!-- RIGHT — h:panelGroup renders <div> AND counts as one JSF child -->
<p:panelGrid columns="2">
  <p:outputLabel value="Name" />
  <h:panelGroup layout="block" styleClass="flex">
    <p:inputText value="#{bean.name}" />
    <p:commandButton icon="pi pi-search" />
  </h:panelGroup>
</p:panelGrid>
```

### ConfirmDialog — `<p:confirm>` belongs inside the trigger

`<p:confirm>` must be nested inside the button or link that opens the confirmation. The `<p:confirmDialog global="true">` is declared once per page.

```xhtml
<p:commandButton actionListener="#{bean.delete(item)}" icon="pi pi-trash">
    <p:confirm header="..." message="#{bean.getDeleteConfirmMessage(item)}" />
</p:commandButton>

<p:confirmDialog global="true">
    <p:commandButton value="Yes" type="button" styleClass="ui-confirmdialog-yes" />
    <p:commandButton value="No"  type="button" styleClass="ui-confirmdialog-no" />
</p:confirmDialog>
```

Parametrized confirm messages cannot use EL string functions with escaped quotes — delegate the message build to a bean method (e.g. `bean.getDeleteConfirmMessage(item)`).

### Update paths inside tabs — use absolute IDs

`<p:tabView>` / `<p:tab>` are NamingContainers, so a component inside a tab has a compound client ID like `:main-form:tab-view:planning-content`. From outside the tab, always use absolute paths in `update`.

```xhtml
<!-- inside the tab -->
<h:panelGroup id="planning-content" layout="block">...</h:panelGroup>

<!-- from outside the tab -->
<p:commandButton update=":main-form:tab-view:planning-content :main-form:growl" />
```

### `cellEdit` AJAX — re-rendering the same DataTable

PrimeFaces blocks updates to the `<p:dataTable>` that fires a `cellEdit` event during the same AJAX cycle. KPI rows or aggregate cells that depend on the edited value won't refresh if they live in the same table.

Workaround: split aggregates into a second table and trigger its update via `<p:remoteCommand>` from the cellEdit's `oncomplete`.

```xhtml
<p:remoteCommand name="refreshMetaTable" update="meta-table" />

<p:dataTable id="meta-table" value="#{bean.metaRows}" var="row">...</p:dataTable>

<p:dataTable id="planning-table" value="#{bean.displayRows}" var="row" editable="true">
  <p:ajax event="cellEdit"
          listener="#{bean.onCellEdit}"
          update=":main-form:growl"
          oncomplete="refreshMetaTable()" />
  ...
</p:dataTable>
```

The `<p:remoteCommand>` must live **outside** any `<p:dataTable>` — placing it inside breaks NamingContainer ID resolution.
