# Dialog Bean (Controller Bean or JSF Managed Bean)

Rules for the Java bean behind an Axon Ivy HTML Dialog. **Prefer a bean over Axon Ivy process
logic** for UI-related behavior (validation, dynamic visibility, uploads, autocomplete). Keep
process logic (`#{logic.xxx}`) only for navigation (submit/cancel).

## Two valid patterns — ASK the user first

Axon Ivy supports **two equally valid** ways to back a dialog with Java. Pick one per dialog and
stay consistent.

| | **A. Controller bean** (Ivy-native) | **B. JSF managed bean** |
|---|---|---|
| Wiring | Plain POJO held as a `bean` **field on the dialog data class**; referenced as `#{data.bean.*}` | `@ManagedBean @ViewScoped` class referenced as `#{beanName.*}` |
| Init | In `HtmlDialogStart` `input.code`: `out.bean = new MyBean(); out.bean.init();` | `@PostConstruct` or a `preRender()` called from `<f:event>` |
| Annotations | **None** (plain `Serializable` POJO) | `@ManagedBean @ViewScoped` (`javax.faces.bean.*`) |
| Data access | Bean *is* `data.bean`; holds its own state, may call services/DAOs directly | Bean is independent; **XHTML bridges** all `#{data.*}` ↔ bean |
| Best when | Generated/round-tripped by **Axon Ivy Designer**; bean owns the dialog's whole state | Reusable component logic, autocomplete, behavior shared across dialogs |

> **Before creating a bean, ASK the user which pattern they want** — unless the project already
> clearly uses one (then match the existing convention). Suggested question:
>
> *"Should I back this dialog with a **controller bean** (`#{data.bean}`, the Ivy-Designer-native
> style) or a **JSF `@ManagedBean`**?"*
>
> If unsure and the project has a reference: the controller bean is what Axon Ivy Designer
> generates and round-trips; the JSF managed bean is the portable standard-JSF style.

Then follow the matching section below. **File location for both:** `src/package/bean/` (or
`src/package/managedbean/`). **NEVER** put the bean in `src_hd/`.

## When to Create a Bean

Create a bean (either pattern) when a dialog needs:
- Validation or business logic beyond simple field binding
- Dynamic UI visibility/read-only control
- File upload/download handling
- Autocomplete / dynamic dropdown logic
- Any reusable UI behavior

---

## Pattern A — Controller bean (`#{data.bean}`)

A plain `Serializable` POJO (no JSF annotations) declared as a field on the dialog's data class and
referenced from XHTML as `#{data.bean.*}`. This is what **Axon Ivy Designer** generates and the
pattern used by the reference Ivy 14 projects.

### 1. The bean — plain POJO in `src/package/bean/`

```java
package package.bean;

import java.io.Serializable;
import java.util.List;

import javax.faces.application.FacesMessage;
import javax.faces.context.FacesContext;

public class MyDialogBean implements Serializable {

  private static final long serialVersionUID = 1L;

  private MyEntity entity;
  private List<Option> options;

  /** Called by the dialog start: out.bean = new MyDialogBean(); out.bean.init(); */
  public void init() {
    this.entity = new MyEntity();
    this.options = MyService.loadOptions();
  }

  /** Business action invoked from the XHTML via #{data.bean.save}. Stays in the dialog. */
  public void save() {
    if (!validate()) {
      return;
    }
    MyService.save(entity);
    addInfo("Saved.");
  }

  private boolean validate() { /* add FacesMessages, return false on error */ return true; }

  private static void addInfo(String msg) {
    FacesContext.getCurrentInstance().addMessage(null,
        new FacesMessage(FacesMessage.SEVERITY_INFO, msg, null));
  }

  public MyEntity getEntity() { return entity; }
  public void setEntity(MyEntity entity) { this.entity = entity; }
  public List<Option> getOptions() { return options; }
}
```

Rules:
1. **No JSF annotations** — it is a plain POJO; the dialog data class owns its lifecycle.
2. **`implements Serializable` + `serialVersionUID = 1L`** — it crosses Ivy process-state serialization.
3. **No constructor Ivy-API calls** — do engine/DAO work in `init()` (called from the start), not the constructor.
4. The bean **may** call services/DAOs directly and hold the dialog's full state.

### 2. The data class — declare the `bean` field

`src_hd/<ns-path>/<Dialog>/<Dialog>Data.d.json`:

```json
{
  "$schema" : "https://json-schema.axonivy.com/14.0-dev/project/data-class.json",
  "simpleName" : "MyDialogData",
  "namespace" : "package.path.MyDialog",
  "fields" : [ {
    "name" : "bean",
    "type" : "package.bean.MyDialogBean",
    "comment" : "Controller bean for this dialog.",
    "modifiers" : [ ]
  } ]
}
```

### 3. The process — instantiate + init in `HtmlDialogStart`

`<Dialog>Process.p.json` start element:

```json
{
  "id" : "f0",
  "type" : "HtmlDialogStart",
  "name" : "start()",
  "config" : {
    "signature" : "start",
    "input" : {
      "map" : { },
      "code" : "import package.bean.MyDialogBean;\nout.bean = new MyDialogBean();\nout.bean.init();"
    },
    "guid" : "UNIQUE_GUID_16CHARS"
  },
  "connect" : [ { "id" : "f2", "to" : "f1" } ]
}
```

### 4. The XHTML — reference `#{data.bean.*}`

```xml
<h:form id="form">
  <p:messages id="form-messages" showDetail="true" />

  <p:inputText value="#{data.bean.entity.name}" />

  <p:selectOneMenu value="#{data.bean.selectedId}">
    <f:selectItems value="#{data.bean.options}" var="o" itemLabel="#{o.label}" itemValue="#{o.id}" />
    <p:ajax event="change" listener="#{data.bean.onChange}" update="some-panel" />
  </p:selectOneMenu>

  <!-- Business action: bean method, dialog STAYS open (refresh form) -->
  <p:commandButton value="Save" actionListener="#{data.bean.save}" process="@form" update="form" />
  <!-- Navigation: logic event closes the dialog -->
  <p:commandButton value="Close" actionListener="#{logic.close}" process="@this" immediate="true" />
</h:form>
```

Notes:
- No `<f:event preRenderComponent>` needed — init runs in the dialog start (`out.bean.init()`).
- Use `#{data.bean.method}` for business actions that **stay** in the dialog; use `#{logic.xxx}`
  only for navigation events (`submit` → `HtmlDialogExit`, `close` → exit). See `logic-process.md`.
- Avoid entity-typed `p:selectOneMenu` converters by binding to a String id and resolving in an
  AJAX listener (`onChange`).

---

## Pattern B — JSF managed bean (`@ManagedBean`)

A standard JSF `@ManagedBean @ViewScoped` class referenced as `#{beanName.*}`, independent of the
dialog data class. The XHTML bridges all data between `#{data.*}` and the bean.

**Key principle: the bean NEVER references `#{data.xxx}` or `#{logic.xxx}`. The XHTML handles ALL data bridging.**

### Class Structure

```java
package package.managedbean;

import java.io.Serializable;
import javax.faces.bean.ManagedBean;
import javax.faces.bean.ViewScoped;

@ManagedBean
@ViewScoped
public class MyBean implements Serializable {

  private static final long serialVersionUID = 1L;

  private MyEntity entity;
  private boolean readOnly;

  /**
   * Called by XHTML:
   *   <f:event listener="#{myBean.preRender(data.entity, data.isReadOnly)}" type="preRenderComponent" />
   */
  public void preRender(MyEntity entity, Boolean readOnly) {
    this.entity = entity != null ? entity : new MyEntity();
    this.readOnly = Boolean.TRUE.equals(readOnly);
  }

  public void save() {
    entity = MyService.save(entity);
  }

  public MyEntity getEntity() { return entity; }
  public void setEntity(MyEntity entity) { this.entity = entity; }

  public boolean isReadOnly() { return readOnly; }
  public void setReadOnly(boolean readOnly) { this.readOnly = readOnly; }
}
```

### Rules

1. **Always `implements Serializable`** — `@ViewScoped` beans must be serializable.
2. **Always `@ManagedBean @ViewScoped`** — one bean instance per page view.
3. **Use `preRender()` for init** — never use constructor for Ivy API calls.
4. **Bean NEVER references `#{data.xxx}` or `#{logic.xxx}`** — XHTML handles bridging.
5. **All bridged fields need getter AND setter** — `setPropertyActionListener` calls setters.
6. **Prefer bean methods over `#{logic.xxx}`** for business logic — use `#{logic.xxx}` only for navigation.

### Data Bridging (XHTML Side)

#### Init: Process Data → Bean

```xml
<f:event listener="#{myBean.preRender(data.entity, data.isReadOnly)}" type="preRenderComponent" />
```

#### Submit: Bean → Process Data + Navigate

```xml
<!-- Simple: setPropertyActionListener pushes data, then logic navigates -->
<p:commandButton value="Save" actionListener="#{logic.save}" process="@form" update="form">
  <f:setPropertyActionListener target="#{data.entity}" value="#{myBean.entity}" />
</p:commandButton>

<!-- Two-step: bean processes first, then remoteCommand pushes data + navigates -->
<p:commandButton value="Submit" actionListener="#{myBean.save()}"
                 process="@form" update="form"
                 oncomplete="if(!args.validationFailed) submitToProcess();" />
<p:remoteCommand name="submitToProcess" actionListener="#{logic.save}" process="@this">
  <f:setPropertyActionListener target="#{data.entity}" value="#{myBean.entity}" />
</p:remoteCommand>
```

#### Cancel: Direct Logic Call

```xml
<p:commandLink value="Cancel" actionListener="#{logic.close}" process="@this" immediate="true" />
```

### Example: RoleSelectionBean (Autocomplete Component)

A bean that provides autocomplete logic for a reusable composite component.

**Bean:** `src/com/axonivy/portal/components/bean/RoleSelectionBean.java`

```java
package com.axonivy.portal.components.bean;

import java.io.Serializable;
import java.util.List;
import javax.annotation.PostConstruct;
import javax.el.MethodExpression;
import javax.faces.bean.ManagedBean;
import javax.faces.bean.ViewScoped;

@ManagedBean
@ViewScoped
public class RoleSelectionBean implements Serializable {

  private static final long serialVersionUID = 1L;
  private MethodExpression completeRoleMethod;

  @PostConstruct
  public void init() {
    completeRoleMethod = BeanUtils.createCompleteMethod("#{roleSelectionBean.completeRole}");
  }

  public List<RoleDTO> completeRole(String query) {
    List<String> fromRoles = Attrs.currentContext().getAttribute("#{cc.attrs.fromRoleNames}", List.class);
    List<String> excludedRoleNames = Attrs.currentContext().getAttribute("#{cc.attrs.excludedRoleNames}", List.class);
    return RoleUtils.findRoles(fromRoles, excludedRoleNames, query);
  }

  public MethodExpression getCompleteRoleMethod() {
    return completeRoleMethod;
  }
}
```

**XHTML (composite component):** `src_hd/.../RoleSelection.xhtml`

```xml
<cc:interface componentType="IvyComponent">
  <cc:attribute name="selectedRole" type="com.axonivy.portal.components.dto.RoleDTO" required="true" />
  <cc:attribute name="completeMethod" method-signature="java.util.List completeMethod(java.lang.String)" />
  <!-- ... other attributes ... -->
</cc:interface>

<cc:implementation>
  <c:set var="completeMethod"
    value="#{not empty cc.attrs.completeMethod ? cc.attrs.completeMethod : roleSelectionBean.completeRoleMethod}" />

  <p:autoComplete id="#{cc.attrs.componentId}"
    value="#{cc.attrs.selectedRole}"
    completeMethod="#{completeMethod}"
    var="role" itemValue="#{role}" itemLabel="#{role.displayName}"
    forceSelection="true" dropdown="true" converter="pojoConverter" />
</cc:implementation>
```

**Key patterns shown:**
- Bean provides a `MethodExpression` for `p:autoComplete completeMethod`
- XHTML falls back to bean method when no custom `completeMethod` attribute is passed
- Bean reads composite component attributes via `Attrs.currentContext().getAttribute()`

---

## Shared — File Upload Listener (both patterns)

The bean method must accept `FileUploadEvent` (not no-arg):

```java
import org.primefaces.event.FileUploadEvent;

public void upload(FileUploadEvent event) {
  if (event == null || event.getFile() == null) return;
  try {
    java.io.File tempFile = java.io.File.createTempFile("upload_", ".pdf");
    java.nio.file.Files.write(tempFile.toPath(), event.getFile().getContent());
    this.inputFile = tempFile;
  } catch (Exception e) {
    Ivy.log().error("Failed to process uploaded file", e);
  }
}

public void removeFile() {
  if (inputFile != null && inputFile.exists()) inputFile.delete();
  inputFile = null;
}
```

## Shared — Displaying Messages

```java
FacesContext.getCurrentInstance().addMessage("form-messages",
    new FacesMessage(FacesMessage.SEVERITY_ERROR, "", "Validation failed"));
```

## Common Mistakes

- **Bean in `src_hd/`** — always use `src/package/bean/` or `src/package/managedbean/`.
- **Mixing the patterns in one dialog** — pick A or B and be consistent.
- **Constructor with Ivy API** — use `init()` (Pattern A) or `preRender()`/`@PostConstruct` (Pattern B).
- **(Pattern A) Forgetting `out.bean = new …(); out.bean.init();`** in the `HtmlDialogStart` code — `#{data.bean}` is null.
- **(Pattern A) Declaring the `bean` field** missing from the dialog `…Data.d.json` — `#{data.bean}` won't resolve.
- **(Pattern B) Missing setter** for fields used in `setPropertyActionListener` — silently fails.
- **No-arg upload method** with `listener` attribute — must accept `FileUploadEvent`.
```
