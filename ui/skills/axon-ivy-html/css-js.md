# Styling, Layout, Icons, CSS & JS

## Styling & Layout

Use PrimeFlex 3 CSS for layout and responsiveness whenever possible.

Prefer PrimeFlex utility classes for:

- Grid layout
  - Use .grid for container
  - Use .col-12, md:col-6, lg:col-4 for responsive columns
  - Use .p-fluid for form layout if PrimeFaces components are used
- Spacing (e.g., p-2, m-3, gap-2)
- Flex utilities (e.g., flex, justify-content-between, align-items-center)
- Do NOT use inline CSS styles (style="" is forbidden) — use `styleClass` with PrimeFlex 3 utilities

### Targeting PrimeFaces components from custom CSS

When you must style a PrimeFaces component from a project stylesheet, target its **`ui-*`** class.
Components render as `ui-panel`, `ui-button`, `ui-inputtext`, `ui-panel-titlebar`, `ui-slider`,
`ui-state-error`, … — a selector written against the PrimeReact/NG `p-*` name (e.g. `.p-panel { … }`)
**silently does nothing**. When unsure, target both prefixes (`.ui-panel, .p-panel`) or inspect the
rendered DOM. (The Freya theme also honors some `p-button-*` utility classes, but for your own rules
`ui-*` is the safe bet.) Nothing in the build flags a no-op selector — only the rendered page reveals it.

### Icons

Use **Tabler Icons** (`ti ti-*`). Both classes are required: `ti` loads the font, `ti-<name>` picks
the glyph. The font ships with the platform — **no install, no `@font-face`, no stylesheet import**.

```xml
<p:commandButton id="proceed" icon="ti ti-check" styleClass="ui-button-primary" />
<p:commandButton icon="ti ti-trash" styleClass="ui-button-danger" />
<i class="ti ti-cloud-upload text-4xl" />
<h:panelGroup id="warn-icon" styleClass="ti ti-alert-triangle" />
```

Refer to `icons.txt` for a curated list of Tabler names, and for how to look up the rest.

PrimeIcons (`pi pi-*`) also resolve and are what the Designer scaffold emits, but prefer `ti ti-*`
for new markup — the Portal reference implementation uses Tabler for ~97% of its icons, buttons
included.

## Custom CSS Rules

If custom styling is required:

### Case 1: HTML already includes stylesheet reference

If the HTML dialog contains:

```html
<h:outputStylesheet library="css" name="custom.css" />
```

- Define all custom CSS classes inside custom.css.
- Do NOT define `<style>` blocks in the HTML.

### Case 2: No stylesheet exists

If no CSS file is referenced:

1. Search for folder `webContent/resources/css`
2. If missing, create the folder.
3. Create a new CSS file named after the dialog, e.g.: `customer-complaint-dialog.css`
4. Define all custom CSS classes in that file.
5. Add this reference to the HTML dialog:

```html
<h:outputStylesheet library="css" name="customer-complaint-dialog.css" />
```

## JavaScript Rules

- Do NOT use inline JavaScript (no `<script>` blocks inside HTML).
- All JavaScript must be placed in an external .js file.
- Prefer jQuery (available via PrimeFaces) for DOM manipulation, then vanilla JavaScript as fallback.
- Do NOT use other JS libraries (React, Vue, Angular, etc.).
- Code must be modular and reusable.
- Avoid global variables; use a namespace object if needed.

If JavaScript is required:

1. Search for folder `webContent/resources/js`
2. If missing, create the folder.
3. Create a JS file named after the dialog, e.g. customer-complaint-dialog.js
4. Reference the file in the HTML dialog using:

```html
<h:outputScript library="js" name="customer-complaint-dialog.js" />
```
