# DatePicker Component

Rules and patterns for using `<p:datePicker>` in Axon Ivy HTML Dialogs.

## Use `p:datePicker` Instead of `p:calendar`

**CRITICAL**: Always use `<p:datePicker>` for date and date-time input. Do NOT use the older `<p:calendar>` component.

## Basic Date Picker

```xml
<p:outputLabel for="start-date" value="Start Date:" />
<p:datePicker id="start-date"
  value="#{data.startDate}"
  showIcon="true"
  required="true"
  requiredMessage="Date is required" />
```

## Date Picker with Validation and AJAX

```xml
<p:outputLabel for="start-date" value="Start Date:" />
<p:datePicker id="start-date"
  value="#{data.startDate}"
  showIcon="true"
  required="true"
  requiredMessage="Start date is required"
  converterMessage="Invalid date format">
  <p:ajax event="dateSelect"
    listener="#{logic.onStartDateChange}"
    update="end-date form-messages" />
</p:datePicker>
```

## Date Range Pattern (From / To)

Use two `p:datePicker` components side by side for date ranges. The `p:ajax` on the start date can update the end date to enforce constraints.

```xml
<div class="ui-g-6 ui-sm-12">
  <p:outputLabel for="from-date" value="From:" />
  <p:datePicker id="from-date"
    value="#{data.fromDate}"
    showIcon="true"
    required="true"
    requiredMessage="From date is required"
    converterMessage="Invalid date format">
    <p:ajax event="dateSelect"
      listener="#{logic.onFromDateChange}"
      update="to-date form-messages" />
  </p:datePicker>
</div>

<div class="ui-g-6 ui-sm-12">
  <p:outputLabel for="to-date" value="To:" />
  <p:datePicker id="to-date"
    value="#{data.toDate}"
    showIcon="true"
    required="true"
    requiredMessage="To date is required"
    converterMessage="Invalid date format">
    <p:ajax event="dateSelect"
      listener="#{logic.onToDateChange}"
      update="form-messages" />
  </p:datePicker>
</div>
```

## Common Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `value` | Binding to data field | `#{data.startDate}` |
| `showIcon` | Show calendar icon button | `true` |
| `required` | Make field mandatory | `true` |
| `requiredMessage` | Message when empty | `"Date is required"` |
| `converterMessage` | Message on invalid format | `"Invalid date format"` |
| `placeholder` | Placeholder text | `"dd.MM.yyyy"` |
| `locale` | Locale for date format | `#{localeBean.locale}` |
| `pattern` | Date format pattern | `"dd.MM.yyyy"` |
| `mindate` | Earliest selectable date | `#{data.minDate}` |
| `maxdate` | Latest selectable date | `#{data.maxDate}` |
| `disabled` | Disable the component | `#{data.isReadOnly}` |
| `showTime` | Show time selector | `true` |
| `timeOnly` | Time input only | `true` |

## AJAX Events

- `dateSelect` — Fired when the user selects a date from the popup. This is the primary event to use.

```xml
<p:ajax event="dateSelect"
  listener="#{logic.onDateChange}"
  update="other-component form-messages" />
```

## Rules

1. **Always set `showIcon="true"`** for better UX — gives users a clickable calendar button.
2. **Always add validation** — use `required`, `requiredMessage`, and `converterMessage`.
3. **Use `p:ajax` with `dateSelect`** to react to date changes (e.g., update dependent fields, validate ranges).
4. **Use CMS for labels and messages** in Axon Ivy projects — e.g., `#{ivy.cms.co('/path/to/label')}`.
5. **Use `p:outputLabel` with `for`** pointing to the datePicker `id` for proper label association.
6. **Use numeric date patterns only** — `p:datePicker` does NOT support text-based month patterns like `MMM dd, yyyy`. Use `MM/dd/yyyy`, `dd.MM.yyyy`, or `yyyy-MM-dd` instead.

```
WRONG: pattern="MMM dd, yyyy"   ← causes "'Mar 07, 2025' could not be understood as a date"
RIGHT: pattern="MM/dd/yyyy"
RIGHT: pattern="dd.MM.yyyy"
```
