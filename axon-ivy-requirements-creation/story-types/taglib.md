# Story Type: Tag Library Registration

**Source:** Technical necessity — exists only when reusable UI components were created.

**Skip this story entirely** if the reuse matrix from the UI Component analysis shows zero sections appearing in 2+ forms. A tag library with a single component is not needed.

**This story enables** XHTML forms to reference shared components using a short tag namespace instead of full include paths.

---

## Scope

One story per module, registering all reusable components in a single tag library descriptor.

---

## Implementation Details to Include

### Tag Library XML

- File location: `webContent/WEB-INF/[module].taglib.xml`
- Namespace: `http://[company]/[module]/components`
- Prefix: short alias (e.g., `comp`)

### Component registrations

List each component:

| Tag Name | Component File | Description |
| -------- | -------------- | ----------- |
| ContactFields | erp/components/ContactFields.xhtml | Contact info section |
| AddressFields | erp/components/AddressFields.xhtml | Address section |

### Configuration update

- Register the tag library in `webContent/WEB-INF/web.xml` under `javax.faces.FACELETS_LIBRARIES`

---

## Acceptance Criteria

- [ ] Tag library XML is present in `WEB-INF/`
- [ ] Each component is accessible via its tag namespace in XHTML (e.g., `<comp:ContactFields />`)
- [ ] No duplicate namespace or prefix conflicts with other modules
- [ ] Tag library is listed in `web.xml` FACELETS_LIBRARIES parameter
