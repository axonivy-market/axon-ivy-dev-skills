# PrimeFaces & JSF Components

Rules and best practices for generating JSF and PrimeFaces elements for Axon Ivy HTML Dialog.

## Best Practices

### Component availability — not every PrimeReact/NG component is a PrimeFaces (JSF) tag

Ivy 14 bundles **PrimeFaces 15.0.18** (`jakarta` classifier) — 176 tags in
`META-INF/primefaces.taglib.xml`. It has **no `<p:inputGroup>` / `<p:inputGroupAddon>` tags** — using
them fails at render with `TagException: no tag was defined for name: inputGroup`. For a leading-icon
field, build the group with CSS instead of the component:

```xml
<span class="my-inputgroup">
  <span class="my-inputgroup-addon"><i class="ti ti-user"></i></span>
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

## Common Pitfalls (PrimeFaces 15.0.18)

DataTable `sortBy` vs `sortField`, `<p:tooltip for>` targets, `<p:dialog>` ID prefixes in `update`,
and `<p:panelGrid columns="N">` child counting are covered by the **`axon-ivy-primefaces-verify`**
skill (items 10-13) — use it to check finished markup. The pitfalls below exist only here.

### ConfirmDialog — `<p:confirm>` belongs inside the trigger

`<p:confirm>` must be nested inside the button or link that opens the confirmation. The `<p:confirmDialog global="true">` is declared once per page.

```xhtml
<p:commandButton actionListener="#{bean.delete(item)}" icon="ti ti-trash">
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
