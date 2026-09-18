# Dependency Handling

Verify dependency outputs exist and are usable before implementing the story.

Typical outputs:

| Story Type | Expected Artifacts |
|---|---|
| Data Model | `.d.json`, model/enum `.java` |
| Entity + Repository | entity and repository `.java` |
| Smart Workflow | `.p.json`, data classes |
| UI Component | `.xhtml` |
| Tag Library | `.taglib.xml` |
| Form | `.xhtml`, `.p.json`, dialog data |
| Main Process | `.p.json` |
| Roles + Config | config files |

Do not treat an empty/stub file as a satisfied dependency.

If missing:

- dependency is included in requested stories → implement it first
- otherwise → report the current story as blocked

Do not create temporary substitutes for missing dependencies.