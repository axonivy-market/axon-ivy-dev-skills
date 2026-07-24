---
name: custom-fields-l10n
description: Localize (translate) Axon Ivy custom-field labels, descriptions, categories, and STRING/NUMBER values into multiple languages via CMS entries under the /CustomFields/ namespace. Use when custom fields must display in more than one language.
---

## When to Use

Translating a custom field's **Label**, **Description**, **Category**, or (for `STRING`/`NUMBER`) its **values** into other languages. Define the fields first in `config/custom-fields.yaml`.

## Core Concept

The `Label`/`Description`/`Category` in `config/custom-fields.yaml` are **static, single-language** and act as the fallback. To translate them, add matching **CMS text entries** under `/CustomFields/` in each `cms/cms_<locale>.yaml`.

## CMS Paths

| Path | Localizes | Applies to |
|---|---|---|
| `/CustomFields/{kind}/{name}/Label` | display label | all types |
| `/CustomFields/{kind}/{name}/Description` | description | all types |
| `/CustomFields/Categories/{category}` | category name (shared, not per-kind) | all |
| `/CustomFields/{kind}/{name}/Values/{value}` | a stored value's label | **`STRING` / `NUMBER` only** |

- `{kind}` = `Tasks` / `Cases` / `Starts`.
- `{name}` = the field **identifier** (camelCase key), not its Label.
- `{value}` = the raw stored value (the key); the entry's value is the translated label.

Path separators map to nested YAML keys — `/CustomFields/Tasks/branchOffice/Label`:

```yaml
CustomFields:
  Tasks:
    branchOffice:
      Label: Branch Office
      Values:            # STRING/NUMBER only — omit for TEXT/TIMESTAMP
        Vienna: Vienna   # → 'Wien' in cms_de.yaml
```

## Rules

- **Values only for `STRING`/`NUMBER`** — never `TEXT`/`TIMESTAMP`.
- **Identical key hierarchies across all `cms_<locale>.yaml`** files.
- **Quote value keys** that are booleans (`'Yes'`, `'No'`, `'On'`, `'Off'`) or numbers (`'1'`) so SnakeYAML keeps them as strings.
- Use the field identifier in the path, not the Label.

See `example/cms_en.yaml` + `example/cms_de.yaml` for a full localized pair.
