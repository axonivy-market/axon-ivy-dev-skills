---
name: axon-ivy-smart-workflow
description: Add AI / LLM steps to Axon Ivy processes with Smart Workflow (AgenticProcessCall, a ProgramInterface element in .p.json). Use when a process should let AI (OpenAI, ChatGPT, Gemini, Claude, Azure OpenAI, Ollama...) extract structured data from text, images or PDFs (invoices, forms, CVs), classify or decide, call sub-process or Java tools, ask a human, answer from documents (RAG) or search the web. Also covers guardrails, PII masking and provider/model configuration.
---

# Axon Ivy Smart Workflow

Use this skill when a process needs an AI step: extract structured data, classify or decide, answer with tools, or run a multi-step agent.

The AI step is a `ProgramInterface` element with `javaClass` = `com.axonivy.utils.smart.workflow.AgenticProcessCall`.

## Reference files

Read the matching file before building one of these features:

| Feature | File |
|---------|------|
| Full example: extraction callable sub-process (data class + process) | [references/extraction-example.md](references/extraction-example.md) |
| Tools: callable sub-processes, Java tools, web search, agents as tools, agent pipeline | [references/tools.md](references/tools.md) |
| Guardrails, PII masking, custom guardrails, circuit breaker | [references/guardrails.md](references/guardrails.md) |
| Human-in-the-loop: the agent asks a user and continues afterwards | [references/human-in-the-loop.md](references/human-in-the-loop.md) |
| RAG with OpenSearch | [references/rag.md](references/rag.md) |
| Dependencies, providers, `variables.yaml`, observability | [references/configuration.md](references/configuration.md) |

## Setup

1. Check the project's `pom.xml` for `com.axonivy.utils.ai:smart-workflow` **and at least one provider** artifact (e.g. `smart-workflow-openai`). The artifact list and pom snippet are in [references/configuration.md](references/configuration.md).
2. If they are missing and the library is not in the workspace (glob `**/smart-workflow/pom.xml` or `smart-workflow-*.iar`), use the `ivy-market-import` skill first. If it is in the workspace, add the dependencies. Never hardcode a version; how to find it is in [references/configuration.md](references/configuration.md).
3. Make sure the provider's API key is configured in `variables.yaml`. See [references/configuration.md](references/configuration.md).

## Gotchas

These are the mistakes that break Smart Workflow elements. Check every element against them.

1. **`resultType` is a class literal ending in `.class`**: `"invoice.model.Invoice.class"`, not `"invoice.model.Invoice"`. Empty or `"String.class"` means a text answer.
2. **`resultType` must be a single object.** `java.util.List.class` and `List<x.Item>.class` do not work. Wrap lists in a class with a `List<Item>` field.
3. **`model` is a script expression**, so a literal needs quotes: `"\"gpt-4.1\""`. For Azure it is the deployment name.
4. **`tools`, `inputGuardrails` and `outputGuardrails` are plain comma strings**: `"a,b"`. Not JSON arrays like `"[\"a\",\"b\"]"` (legacy format). `""` means none.
5. **Only PNG, JPEG and PDF files reach the model.** Any other file in `query` (docx, xlsx, txt from a stream...) is dropped without warning. Convert it to text first.
6. **`PromptInjectionInputGuardrail` blocks any line break**, including line breaks in your own `query` template. See [references/guardrails.md](references/guardrails.md) for the workaround.
7. **`PiiMaskingGuardrail` belongs in both `inputGuardrails` and `outputGuardrails`**, or the placeholders stay in the result.
8. **Unknown guardrail names are ignored silently.** Check the spelling.
9. **A sub-process tool needs the `tool` tag** on its `CallSubStart`. Without it the agent cannot see it, even if it is listed in `tools`.
10. **Every field the system prompt asks for must exist on the `resultType` class**, and the other way round.
11. **Name every AgenticProcessCall meaningfully.** The element `name` is the agent name in chat history and traces.
12. **Each call costs one or more LLM round trips.** In multi-step flows, put a `TaskSwitchEvent` before each agent so a failure resumes there. See "Agent pipeline" in [references/tools.md](references/tools.md).
13. **Set large stream or binary fields to `null` after the agent has run**, so they are not persisted with the process data.

## The AgenticProcessCall element

```json
{
  "id" : "f1",
  "type" : "ProgramInterface",
  "name" : "Extract Invoice",
  "config" : {
    "javaClass" : "com.axonivy.utils.smart.workflow.AgenticProcessCall",
    "userConfig" : {
      "system" : "You are an invoice data extraction assistant. ...",
      "query" : "Extract all data from this invoice:\n<%=in.uploadedFile%>",
      "tools" : "",
      "resultType" : "invoice.model.Invoice.class",
      "resultMapping" : "in.invoice"
    }
  },
  "visual" : {
    "at" : { "x" : 256, "y" : 64 },
    "size" : { "width" : 128 }
  },
  "boundaries" : [ {
      "id" : "f2",
      "type" : "ErrorBoundaryEvent",
      "config" : {
        "errorCode" : "ivy:error:program:exception",
        "output" : { "map" : { "out" : "in", "out.error" : "error" } }
      },
      "visual" : { "at" : { "x" : 288, "y" : 104 } },
      "connect" : [ { "id" : "f10", "to" : "errorHandler" } ]
    } ],
  "connect" : [ { "id" : "f11", "to" : "nextElement" } ]
}
```

### userConfig keys

All values are JSON strings. The "Kind" column says how each one is evaluated.

| Key | Kind | Required | Description |
|-----|------|----------|-------------|
| `query` | macro text | Yes | User message. See [Query input](#query-input). If it is empty, the element is skipped. |
| `system` | macro text | Recommended | System message. `<%=expr%>` is expanded as text. |
| `resultType` | script → `Class` | No | Structured output type ending in `.class`. Empty means a `String` result. |
| `resultMapping` | script target | Usually | Where the result is assigned, e.g. `"in.invoice"`. |
| `tools` | comma list | No | Tool names, e.g. `"findProduct,createProduct"`. See [references/tools.md](references/tools.md). |
| `provider` | name | No | `OpenAI`, `AzureOpenAI`, `Gemini`, `Anthropic`, `xAI` or `Ollama`. Empty means `AI.DefaultProvider`. |
| `model` | script → `String` | No | Quoted literal or expression. Empty means the provider's `DefaultModel`. |
| `temperature` | script → `Double` | No | e.g. `"0.2"`. Empty means `0.0`. |
| `inputGuardrails` | comma list | No | Empty means `AI.Guardrails.DefaultInput`. See [references/guardrails.md](references/guardrails.md). |
| `outputGuardrails` | comma list | No | Empty means `AI.Guardrails.DefaultOutput`. |

### Error codes to catch

Add one `ErrorBoundaryEvent` per code you need to handle. The process data class needs a field `error` of type `ch.ivyteam.ivy.bpm.error.BpmError`; `error.getMessage()` holds the reason.

| Error code | Raised when |
|-----------|-------------|
| `ivy:error:program:exception` | Technical failure: provider down, invalid API key, mapping failure. **Always catch this.** |
| `smartworkflow:guardrail:input:violation` | An input guardrail blocked the user message |
| `smartworkflow:guardrail:output:violation` | An output guardrail blocked the AI response |
| `smartworkflow:stop` | The circuit breaker is active (all agents stopped) |
| any BpmError thrown by a tool sub-process | Re-thrown with attributes `tool.name`, `tool.arguments`, `tool.id`, `ai.invocationId` |

Non-BpmError exceptions inside a tool are **not** thrown. They go back to the model as the tool result, and the model decides how to continue.

## Query input

Each `<%=expr%>` in `query` is evaluated on its own. Files are attached; everything else is converted with `String.valueOf(...)`. Several values and files in one query are fine.

| Value in `<%=...%>` | Result |
|------|-------|
| `String`, numbers, Ivy data classes | Text (`toString()`) |
| Plain Java object | Use `dev.langchain4j.internal.Json.toJson(in.obj)` to send it as JSON |
| `java.io.InputStream`, `ch.ivyteam.ivy.scripting.objects.Binary` | File attached, format detected from content |
| `java.io.File`, `java.nio.file.Path`, `ch.ivyteam.ivy.scripting.objects.File` | File attached, format from the file extension |
| `ch.ivyteam.ivy.workflow.document.IDocument` | Case or task document attached, format from the document name |
| `ivy.cms.co("/path")` written **literally** | CMS `png`/`jpg`/`jpeg`/`pdf` attached; `txt`, `md` and string entries become text; other extensions throw |

Examples:

```json
"query" : "Context: <%=in.context%>\n\nData:\n<%=in.inputData%>",
"query" : "Compare these two invoices:\n<%=in.firstStream%>\n<%=in.secondBinary%>",
"system" : "<%=ivy.cms.co(\"/Prompts/ExtractInvoice\")%>"
```

## Result classes

Annotate the `resultType` class and its fields with `@Description`. The model sees these descriptions in the output schema.

```java
package invoice.model;

import java.util.List;

import dev.langchain4j.model.output.structured.Description;

@Description("Invoice header and line items")
public class Invoice {

  @Description("Invoice identifier as printed on the document")
  private String invoiceNumber;

  @Description("Issue date in format yyyy-MM-dd")
  private String invoiceDate;

  @Description("Final amount due, number without currency symbol")
  private Double totalDue;

  @Description("All line items of the invoice")
  private List<LineItem> items;

  // getters and setters
}
```

| Field type | Use for |
|-----------|---------|
| `java.lang.Double` | Prices, amounts, totals |
| `java.lang.Integer` | Quantities |
| `String` | Dates, identifiers, IBAN. Parse in a Script afterwards if needed. |
| `List<T>` inside the result class | Line items and other repeated values |

## System prompt

- List every field to fill, with its format (dates, numbers). Use the same names as the result class.
- Say what to do when a value is missing (return null, never guess IDs).
- When tools are configured, name them and say when and in which order to call them.

```json
"system" : "You are an invoice data extraction assistant.\n\nEXTRACT:\n1. invoiceNumber: The invoice identifier\n2. invoiceDate: Issue date (yyyy-MM-dd)\n3. totalDue: Final amount due\n4. items: Line items (description, quantity, unitPrice, total)\n\nRULES:\n- Amounts are numbers without currency symbols\n- Return null for fields not found in the document"
```
