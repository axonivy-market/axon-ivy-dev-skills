# Form Design

Design responsive input forms for Axon Ivy HTML Dialog using PrimeFaces and PrimeFlex.

## General UX Principles

- Labels and fields must align vertically across columns
- Keep spacing consistent between rows
- Prefer p-fluid for responsive behavior
- Avoid custom CSS when PrimeFlex utility classes can be used

## Mobile Responsive Rule

On small screens:

- Columns must stack vertically
- Use PrimeFlex responsive classes

## Dialog Type Detection

### Page Dialog (Template-Based)

Detect a page dialog by:

```xml
<ui:composition template="/layouts/*.xhtml">
```

Suggested Structure for Page Dialog

```html
<div class="card">
<h:form id="form" styleClass="grid w-full">

  <!-- Global validation messages -->
  <div class="col-12">
    <p:messages id="form-messages" showDetail="true" />
  </div>

  <!-- FORM CONTENT GOES HERE -->

  <!-- Action Buttons -->
  <div class="col-12 mt-3 text-right">
    <!-- Buttons here -->
  </div>

</h:form>
</div>
```

### Component Dialog (IvyComponent)

Detect a component dialog by:

```xml
<cc:interface componentType="IvyComponent">
```

Rules for Component Dialog

- Only generate `<h:form>` if parent dialog didn't define it or there is no parent dialog
- DO NOT generate messages block
- Only generate form content rows
- Assume the parent dialog already manages form and actions

## Form Layout Rules

### Grid System

- Use PrimeFlex 3 grid system
- Ensure labels and inputs are aligned consistently across all rows
- Maintain a clean, uniform column structure

### Default Layout (2 Columns)

If no layout is specified, assume 2-column layout.

```html
<h:form styleClass="grid">
  <!-- Error messages -->
  <div class="col-12">
    <p:messages id="form-messages">
  </div>

  <!-- Left Column -->
  <div class="col-6 p-fluid grid pr-1">
    <!-- normal field -->
    <div class="grid p-fluid field col-12 align-content-center align-items-center">
      <div class="col-5">Label 1</div>
      <div class="col-7">Field 1</div>
    </div>

  <!-- Right Column -->
  <div class="col-6 p-fluid grid pl-1">
    <div class="grid p-fluid field col-12 align-content-center align-items-center">
      <div class="col-5">Label 2</div>
      <div class="col-7">Field 2</div>
    </div>
    <div class="grid p-fluid field col-12 align-content-center align-items-center">
      <div class="col-5">Label 3</div>
      <div class="col-7">Field 3</div>
    </div>
  </div>

  <!-- Full width field -->
  <div class="col-12 p-fluid grid">
      <div class="grid p-fluid field col-12">
        <div class="col-12 mb-3">label 4</div>
        <div class="col-12">field 5</div>
      </div>
    </div>
  </div>

 <!-- Buttons -->
  <div class="grid mt-3">
    <div class="col-12 text-right">
        <p:commandLink id="cancel" actionListener="#{logic.close}"
                    process="@this" value="Cancel" styleClass="ui-button-secondary mr-2" />
        <p:commandButton id="proceed" actionListener="#{logic.submit}"
                        value="Create Project" update="form" icon="si si-check-1"
                        styleClass="ui-button-primary" />
    </div>
  </div>
</h:form>
```

## Styling Guidelines

### Label

- Add spacing between label and input using: pr-2
- Make labels visually prominent using: font-semibold

### Input

- If no specific style is requested, inputs must be full width using class `w-full`

### Standard Button Pattern

```html
<div class="col-12 mt-3 text-right">
  <p:commandLink id="cancel"
                 actionListener="#{logic.close}"
                 process="@this"
                 value="Cancel"
                 styleClass="ui-button-secondary mr-2" />

  <p:commandButton id="submit"
                   actionListener="#{logic.submit}"
                   value="Submit"
                   update="form"
                   icon="si si-check-1"
                   styleClass="ui-button-primary" />
</div>
```
