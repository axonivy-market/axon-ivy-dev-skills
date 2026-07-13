---
name: axon-ivy-cms
description: Create and manage CMS (Content Management System) content — multi-language YAML files, binary content (files), and Portal CMS overrides.
---

## When to Use

- Adding UI labels or translations for dialogs/processes
- Creating email templates stored in CMS
- Overriding Portal (Axon Ivy Portal) default labels
- Adding binary CMS content (images, CSS files)
- Supporting multiple languages (i18n)

## References

This skill includes reference files in the `cms/` subfolder:

| File | Purpose | When to Read |
|------|---------|--------------|
| `cms/cms_en.yaml` | English CMS example with all namespace patterns | Always — primary reference for structure |
| `cms/cms_de.yaml` | German translation showing multi-language pattern | When creating multi-language entries |

Read these to understand the YAML key hierarchy, namespace conventions, and value formatting.

## CMS Content Object Types

Axon Ivy CMS has a hierarchical structure with **three types** of content objects:

| Type | Storage | Description |
|------|---------|-------------|
| **Folder** | Filesystem directory | Hierarchy only — no content values |
| **Text** | `cms_*.yaml` files | Multilingual text strings stored as YAML key-value pairs |
| **File** | Binary files in `cms/` folder | Images, CSS, PDFs — the file path IS the CMS path |

### Text Content Objects

Stored in `cms_<locale>.yaml` files. Each language has its own file with **identical key hierarchies**.

```
cms/
├── cms_en.yaml          # English texts
├── cms_de.yaml          # German texts (same keys, translated values)
└── cms_fr.yaml          # French texts (same keys, translated values)
```

- Locale = language code (e.g., `en`, `de`) or language + region (`en_US`, `en_GB`)
- Accessed via: `ivy.cms.co("/path/to/key")` — returns text for the user's current locale

### File Content Objects (Binary CMS)

Binary files (images, CSS, documents) stored directly in the `cms/` folder tree.
**No YAML entries needed** — the filesystem path IS the CMS path.

```
cms/
├── images/
│   └── Logo.png              # CMS path: /images/Logo
├── Styles/
│   └── Custom.css            # CMS path: /Styles/Custom
└── documents/
    ├── instruction.pdf       # CMS path: /documents/instruction (language-neutral)
    ├── instruction_en.pdf    # CMS path: /documents/instruction (English)
    └── instruction_de.pdf    # CMS path: /documents/instruction (German)
```

- File extension is stripped from the CMS path
- For multilingual files: append locale to filename (e.g., `instruction_en.pdf`, `instruction_de.pdf`)
- For language-neutral files: just use the filename without locale suffix
- Accessed via: `ivy.cm.ref("/images/Logo")` — returns a URL link to the file

## Use Together With

- `axon-ivy-html` — XHTML files reference CMS via `#{ivy.cms.co('...')}`
- `axon-ivy-cms-verify` — **MUST** run after creating/modifying CMS files to catch common errors

## Proactive CMS Creation

**When creating or modifying an XHTML dialog, ALWAYS create corresponding CMS entries for ALL configured languages.**

### Step 0: Check existing CMS before creating new entries

**Before creating any new CMS key, ALWAYS search existing `cms_*.yaml` files for reusable entries.**

1. Read ALL `cms_*.yaml` files in the project's `cms/` folder
2. Search for keys that match the label you need (e.g., "Cancel", "Submit", "Save")
3. Check the `/Labels/` namespace first — common labels are stored there for cross-dialog reuse
4. Check sibling dialog namespaces — a nearby dialog may already define what you need
5. **Only create a new CMS key if no suitable existing key is found**

Example reuse:
```xml
<!-- GOOD: Reuse existing shared label -->
<p:commandButton value="#{ivy.cms.co('/Labels/Cancel')}" />

<!-- BAD: Creating a duplicate dialog-specific key for a common word -->
<p:commandButton value="#{ivy.cms.co('/Dialogs/hr/onboarding/MyDialog/CancelButton')}" />
```

### Step 1: Identify all user-visible strings in the UI

Scan the XHTML for hardcoded text that should be externalized:
- Page titles and section headers (`<h2>`, `<h3>`, panel headers)
- Field labels (`<h:outputLabel value="...">`)
- Button labels (`<p:commandButton value="...">`)
- Placeholder text (`placeholder="..."`)
- Validation/error messages
- Descriptive text (`<p>`, `<span>`)
- Tab titles, tooltip text
- Confirmation messages

### Step 2: Build CMS key paths from dialog package

For **dialog-specific** labels, create CMS entries in the **same namespace as the dialog** (matching its package path):
```
Dialog: hr.onboarding.InputUploadForm
  → CMS key: /Dialogs/hr/onboarding/InputUploadForm/<LabelName>

XHTML usage: #{ivy.cms.co('/Dialogs/hr/onboarding/InputUploadForm/Title')}
YAML path:   Dialogs: hr: onboarding: InputUploadForm: Title: "..."
```

**When to use which namespace:**

| Namespace | Use for | Example |
|-----------|---------|--------|
| `/Dialogs/<package>/<Dialog>/` | Labels specific to ONE dialog (page title, section headers unique to that dialog) | `/Dialogs/hr/onboarding/StartOnboarding/Title` |
| `/Labels/` | Common labels reusable across MULTIPLE dialogs (Cancel, Submit, Yes/No, Status) | `/Labels/Cancel` |
| `/Email/` | Email template content | `/Email/OnboardingNotification/subject` |

### Step 3: Create entries in ALL language files

Check which `cms_*.yaml` files exist in the project. If none exist yet, create at minimum `cms_en.yaml`. For each language file:

1. **English (`cms_en.yaml`)**: Use the original UI text directly
2. **Other languages**: Translate based on business context and domain terminology
   - Use professional/formal tone for business applications
   - Keep technical terms consistent (e.g., "Onboarding" stays "Onboarding" in German)
   - Match existing translation patterns in the project

### Step 4: Replace hardcoded strings in XHTML

Replace all hardcoded strings with CMS references:
```xml
<!-- BEFORE -->
<h2>Start Employee Onboarding</h2>
<p:commandButton value="Submit" />

<!-- AFTER -->
<h2>#{ivy.cms.co('/Dialogs/hr/onboarding/MyDialog/Title')}</h2>
<p:commandButton value="#{ivy.cms.co('/Dialogs/hr/onboarding/MyDialog/SubmitButton')}" />
```

### What to externalize vs. keep hardcoded

| Externalize to CMS | Keep hardcoded |
|---------------------|----------------|
| Page titles, headers | HTML structure, CSS classes |
| Button labels | Component IDs |
| Field labels | Technical attributes (allowTypes, sizeLimit) |
| Descriptive paragraphs | EL expressions (#{data.field}) |
| Error/validation messages | Icon class names (si si-*) |
| Tab titles | Layout classes (col-12, grid) |
| Placeholder text | |

## File Locations

| Type | Location | Format |
|------|----------|--------|
| Text content | `<project>/cms/cms_<locale>.yaml` | YAML |
| Binary/File content | `<project>/cms/<path>/<file.ext>` | Any (PNG, CSS, PDF, etc.) |

## CMS YAML Namespaces

See `cms/cms_en.yaml` reference for full examples. Key namespaces:

| Namespace | Purpose | CMS Access Path |
|-----------|---------|-----------------|
| `ch.ivy.addon.portalkit.ui.jsf:` | Override Portal default labels | `/ch.ivy.addon.portalkit.ui.jsf/...` |
| `ch.ivy.addon.portal.generic:` | Override Portal generic labels | `/ch.ivy.addon.portal.generic/...` |
| `Dialogs:` | Dialog-specific labels (match package path) | `/Dialogs/package/path/DialogName/Key` |
| `Processes:` | Process start names/descriptions | `/Processes/package/path/ProcessName/name` |
| `Labels:` | Shared reusable labels | `/Labels/Key` |
| `Email:` | Email template content | `/Email/TemplateName/subject` |

## Accessing CMS in Code

### In XHTML (JSF/PrimeFaces)
```xml
<!-- Text content -->
<p:outputLabel value="#{ivy.cms.co('/Labels/Actions')}" />

<!-- With parameters -->
<h:outputFormat value="#{ivy.cms.co('/Email/greeting')}">
  <f:param value="#{data.userName}" />
</h:outputFormat>

<!-- File/binary content (images) — use ivy.cm.ref for URL link -->
<p:graphicImage value="#{ivy.cm.ref('/images/Logo')}" />
```

### In Java/IvyScript
```java
// Get CMS text content
String label = Ivy.cms().co("/Labels/Actions");

// With parameters
String greeting = Ivy.cms().co("/Email/greeting", Arrays.asList(userName));
```

### In Process Elements (EMail, etc.)
```
<%=ivy.cms.co('/Email/EmailReminder/newTaskMail/title')%>
```

## Critical Rules

- **Key paths MUST use colons `:` as separators** in the YAML hierarchy (representing `/` in access paths)
- **All language files must have identical key hierarchies** — if a key exists in `cms_en.yaml`, it must also exist in `cms_de.yaml`
- **Dialog CMS keys must match the dialog's package path** — e.g., dialog `com.example.MyDialog` → key path `Dialogs: com: example: MyDialog:`
- Values containing special YAML characters must be quoted: `'The ''quoted'' text'`
- Use single quotes for values containing colons, brackets, or special chars
- **Text content** → use `ivy.cms.co()` (returns String)
- **File/binary content** → use `ivy.cm.ref()` (returns URL link)

### YAML Boolean Key Trap — Quote `Yes`/`No`/`True`/`False`/`On`/`Off` keys

Axon Ivy uses SnakeYAML (YAML 1.1), which treats these words as booleans. Any such word used as a **key** must be single-quoted.

```yaml
# WRONG
Labels:
  Yes: 'Yes'
  No: 'No'

# RIGHT
Labels:
  'Yes': 'Yes'
  'No': 'No'
```

## Portal CMS Overrides

To override Axon Ivy Portal default labels, use the `ch.ivy.addon.portalkit.ui.jsf:` namespace:

```yaml
ch.ivy.addon.portalkit.ui.jsf:
  common:
    save: Speichern        # Override Portal's "Save" label
    cancel: Abbrechen      # Override Portal's "Cancel" label
  caseDetails:
    addNoteHelpText: Write your text here.
```

**IMPORTANT**: Only override keys that exist in the Portal's default CMS. Check Portal documentation for available keys.
