---
name: axon-ivy-mail
description: Rules and patterns for sending email from an Axon Ivy project. Covers sender / recipient resolution, subject and body templating, attachments, and the recommended builder pattern for one mail type per class. Use whenever Java code or a process step composes or sends an email.
---

# Axon Ivy Mail

Axon Ivy provides a basic mail facility — a `Mail` POJO holding sender / recipient / subject / body / attachments, and a process activity that hands it to the configured SMTP server. The mail itself is plumbing; the work is in **structuring how mail templates, sender lookup, and parameter substitution happen consistently across a project**.

This skill describes the builder-per-mail-type pattern that scales to dozens of email kinds without copy-paste.

## When to Use

- Adding a new outgoing email type
- Modifying an existing mail's subject, body, or attachments
- Wiring sender / recipient resolution
- Reviewing why an email did or didn't go out

## When NOT to Use

- For inbound mail processing (POP3 / IMAP) → that's a different Ivy facility, not covered here.
- For SMS / push notifications → different stack.
- For purely transactional acknowledgements (e.g. REST `Response` bodies) → that's REST, not mail.

## File Locations

| Type | Location |
|------|----------|
| Mail builder classes (one per mail type) | `src/<package>/service/mail/` |
| Abstract base builder | same folder, e.g. `AbstractMailBuilder.java` |
| Mail factory / aggregator | same folder, e.g. `WasteMailService.java` |
| Subject / body templates | CMS or `BusinessParameter` table — never inline strings |

## The builder-per-mail-type pattern

Three tiers:

1. **`AbstractMailBuilder`** — handles common boilerplate (sender fallback, sending, attachment lifecycle).
2. **One concrete `*MailBuilder`** per mail type — overrides recipient, subject, body, attachments.
3. **A factory service** — entry point that returns a configured builder.

### `AbstractMailBuilder`

```java
public abstract class AbstractMailBuilder {

  protected abstract String determineRecipient();
  protected abstract String generateMailSubject();
  protected abstract String generateMailContent();
  protected String generateAttachmentPath() { return null; }   // override when needed

  protected String determineSender() {
    // System default; subclasses override for per-mail sender.
    return ServerFactory.getServer()
        .getApplicationConfigurationManager()
        .getSystemProp("EMail.Server.MailAddress")
        .getValue();
  }

  public Mail build() {
    Mail mail = new Mail();
    mail.setSender(determineSender());
    mail.setRecipient(determineRecipient());
    mail.setSubject(generateMailSubject());
    mail.setContent(generateMailContent());
    String attachment = generateAttachmentPath();
    if (attachment != null) {
      mail.setAttachmentPath(attachment);
    }
    return mail;
  }
}
```

### Concrete builder

```java
public class DocumentOfTransportConfirmationEmail extends AbstractMailBuilder {

  private final WasteDisposalActivity activity;

  public DocumentOfTransportConfirmationEmail(WasteDisposalActivity activity) {
    this.activity = activity;
  }

  @Override
  protected String determineSender() {
    BusinessParameter p = businessParameterDAO.findByKey("EMAIL_DISPOSITION_INT_SENDER");
    return p != null ? p.getValue() : super.determineSender();
  }

  @Override
  protected String determineRecipient() {
    return activity.getTransportDocumentsEMail();
  }

  @Override
  protected String generateMailSubject() {
    String template = businessParameterDAO.findByKey("EMAIL_DOT_CONFIRM_SUBJECT").getValue();
    Map<String, String> values = Map.of(
        BusinessParameterPlaceholders.wasteDisposalActivityNumber.toString(),
        activity.getNumber());
    return StringUtilities.replaceAll(template, values);
  }

  @Override
  protected String generateMailContent() { /* same idea as subject */ }

  @Override
  protected String generateAttachmentPath() {
    return exportService.exportTransportConfirmationPdf(activity);
  }
}
```

### Factory service

```java
public class WasteMailService {
  public static AbstractMailBuilder forDocumentOfTransportConfirmation(WasteDisposalActivity a) {
    return new DocumentOfTransportConfirmationEmail(a);
  }
  // … one per mail type
}
```

Caller — Java side **only builds** the Mail POJO and hands it to the process:

```java
Mail mail = WasteMailService.forDocumentOfTransportConfirmation(activity).build();
// 'mail' is now part of process data; the process handles the actual SMTP send.
```

## Process side — the `EMail` activity sends the mail

Axon Ivy does **not** expose an `Ivy.mail().send(...)` Java API. The actual SMTP send happens in a process via the **`EMail` activity** (`"type": "EMail"` in `.p.json`). Java code's job is to build the Mail POJO; the process reads its fields and dispatches.

A typical `.p.json` `EMail` element:

```json
{
  "type" : "EMail",
  "name" : "send email",
  "config" : {
    "headers" : {
      "emailSubject" : "<%=in.mail.subject%>",
      "emailFrom"    : "<%=in.mail.sender%>",
      "emailTo"      : "<%=in.mail.recipient%>"
    },
    "message" : "<%=in.mail.content%>"
  },
  "boundaries" : [ {
    "type" : "ErrorBoundaryEvent",
    "config" : {
      "errorCode" : "ivy:error:email"
    }
  } ]
}
```

The IvyScript bindings (`<%=in.mail.subject%>` etc.) read fields off the Mail object held in process data. Attachments map similarly — set the path on the Mail POJO and reference `<%=in.mail.attachmentPath%>` in the activity config.

A typical end-to-end shape:

1. **Java step** in the process calls `WasteMailService.for…().build()` and stores the `Mail` POJO in `out.mail`.
2. **`EMail` activity** reads `in.mail.*` and sends.
3. **`ErrorBoundaryEvent`** on the EMail activity catches `ivy:error:email` if SMTP fails.

## Critical Rules

### 1. One class per mail type

Do not pass `MailType` enums through a switch. Each mail type gets its own builder class. Reasons:

- Diffs are localised — changing one mail does not risk regressing another.
- Subject / recipient / attachment logic varies enough that branching gets unmanageable past 3-4 types.
- Easier to test: instantiate the builder, call `build()`, assert the resulting `Mail`.

### 2. Sender comes from configuration, not code

Three acceptable sources, in order of preference:

1. **`BusinessParameter` / DB-stored config** — overridable per environment without redeploy.
2. **Ivy global variable** (`Ivy.var().get("mail.sender")`) — overridable per engine via `variables.yaml`.
3. **System property** (`ServerFactory…getSystemProp("EMail.Server.MailAddress")`) — global default, only as fallback.

Hard-coded sender addresses are a FAIL — every project I've seen with hard-coded senders ends up with prod sending from `dev@example.com`.

### 3. Subjects and bodies come from templates, not concatenated strings

Two acceptable template stores:

- **CMS** — for projects that already use CMS for i18n. `Ivy.cms().co("/Mail/Reminder/subject", List.of(deviceName))`.
- **`BusinessParameter`** — for projects that prefer DB-stored config (templates can be edited by admins without a deploy).

Never:

```java
String subject = "Reminder for device " + device.getName() + " expires on " + date;
```

Always:

```java
String template = paramDAO.findByKey("EMAIL_REMINDER_SUBJECT").getValue();
String subject = StringUtilities.replaceAll(template, Map.of(
    "deviceName", device.getName(),
    "expiryDate", formatDate(date)));
```

Reason: templates change per language / per customer; concatenated strings cannot.

### 4. Attachments are file paths, not byte arrays

`Mail.setAttachmentPath(String)` takes a filesystem path. Generate the file (PDF, Excel, …) into a temp location, set the path, send, then delete. Two pitfalls:

- **Don't** use a path inside the IAR — engine can't always read its own packaged resources at that location.
- **Do** clean up the temp file after `Ivy.mail().send(...)` returns. Ivy does not delete it for you.

### 5. Build inside a system-context block when triggered by a job

Scheduled jobs (Quartz / cron triggers) run without an Ivy session, which means `Ivy.session().getSessionUserName()` is null and CMS lookups may fail. Wrap the **builder** call in `ISecurityManager.instance().executeAsSystem(...)` so the Mail POJO can resolve sender / template / recipient under a system context:

```java
Mail mail = ISecurityManager.instance().executeAsSystem(
    () -> WasteMailService.forCriticalAmounts().build());
// then put 'mail' on process data; the process EMail activity sends it.
```

The actual SMTP send happens in the process step — that step inherits the process's security context, so it does not need a separate `executeAsSystem`. User-triggered mail (REST endpoint, dialog) doesn't need this wrapping at all.

### 6. Validate recipient before handing the Mail to the process

A null or blank recipient lets the build step succeed but trips the `EMail` activity at runtime, which surfaces as an `ivy:error:email` boundary. Catching it later costs noise — validate at build time:

```java
String recipient = determineRecipient();
if (recipient == null || recipient.isBlank()) {
  Ivy.log().warn("Skipping mail of type {0} — no recipient configured for entity {1}",
      getClass().getSimpleName(), entityId);
  return;   // skip silently, do not throw
}
```

Whether to throw or skip on missing recipient is a project policy — pick one and apply it uniformly.

### 7. Failure semantics are handled at the process boundary

SMTP failure surfaces as an `ivy:error:email` BpmError on the `EMail` activity. The boundary event decides what to do — there is no Java-level `catch (MessagingException …)` in the call path. Two common patterns:

- **Best-effort** (newsletter, reminder): boundary event logs and routes to the success branch — flow continues.
- **Critical** (legal notice, transactional confirmation): boundary event routes to a retry sub-process or escalates via a task to a fallback owner.

If your code needs to react in Java to a send failure, listen for the `ivy:error:email` BpmError in the process and pass control back to a Java step — see `axon-ivy-error-handling` for the catch-and-translate pattern.

## Common Pitfalls

- **Calling `Ivy.mail().send(...)` from Java** — that API does not exist. Java builds the Mail POJO; the `EMail` activity in a process performs the actual SMTP send.
- **Subject with newlines** — most SMTP servers reject `Subject: foo\nbar`. Strip control chars from any user-supplied substitution before injecting it into a subject template.
- **HTML body without `Content-Type: text/html`** — Mail goes out, recipient sees the raw HTML. The Mail POJO needs a content-type field set; the `EMail` activity respects it. Check the `Mail` class your project uses for the exact setter name.
- **Mail for an entity loaded inside a closed `EntityManager`** — accessing a lazy field at template-render time throws `LazyInitializationException`. Either eager-fetch in the DAO call or build the substitution map *before* the EM closes.
- **`EMail` activity boundaries omitted** — without an `ErrorBoundaryEvent` for `ivy:error:email`, an SMTP failure ends up in the engine's failed-tasks list. Always wire a boundary, even if it just logs and routes to "done".

## Use Together With

- `axon-ivy-error-handling` — for the `mail:sendFailed` BpmError path
- `axon-ivy-cms` — when subject / body templates live in CMS
