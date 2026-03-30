# PrimeFaces & JSF Components

Rules and best practices for generating JSF and PrimeFaces elements for Axon Ivy HTML Dialog.

## Best Practices

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
