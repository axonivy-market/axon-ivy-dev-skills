# Smart Workflow Tools

Tools are functions the agent can decide to call while it works. List the tool names in the element's `tools` key as a comma-separated string:

```json
"tools" : "findSupplier,createSupplier"
```

- Only listed tools are available to the agent. `""` means no tools.
- Name the tools in the `system` prompt and say when to use them. Models follow explicit instructions much better.

There are three kinds of tools:
1. Callable sub-processes tagged `tool`
2. Java tools registered via SPI
3. Built-in tools: `webSearch`, plus `openSearchSearch` from the RAG module

---

## 1. Callable sub-process as tool

Any `CallSubStart` becomes a tool when it carries the **`tool` tag**. Without the tag the agent cannot see it, even if its name is listed in `tools`.

Tools are found in the current project and all projects it requires.

| Tool property | Comes from |
|---------------|-----------|
| Tool name | `config.signature` (must be unique among tools) |
| Tool description | `visual.description` of the `CallSubStart` |
| Parameters | `config.input.params`: `name`, `type`, `desc` |
| Result returned to the AI | All `config.result.params`, serialized as JSON |

Parameter types can be simple (`String`, `Integer`, `Boolean`, `Date`...) or complex data classes and Java beans, including `List<...>`. The JSON schema the model sees is generated from the type. Write a precise `desc` for every parameter and put `required:` in front of mandatory ones.

```json
{
  "id" : "f3",
  "type" : "CallSubStart",
  "name" : "findSupplier(String,String)",
  "config" : {
    "signature" : "findSupplier",
    "input" : {
      "params" : [
        { "name" : "name", "type" : "String", "desc" : "required: supplier name or part of it" },
        { "name" : "country", "type" : "String", "desc" : "optional: ISO country code to narrow the search" }
      ],
      "map" : {
        "out.name" : "param.name",
        "out.country" : "param.country"
      }
    },
    "result" : {
      "params" : [
        { "name" : "suppliers", "type" : "List<erp.supplier.Supplier>", "desc" : "matching suppliers, empty when none found" }
      ],
      "map" : {
        "result.suppliers" : "in.suppliers"
      }
    }
  },
  "tags" : [
    "tool"
  ],
  "visual" : {
    "at" : { "x" : 96, "y" : 64 },
    "description" : "Find existing suppliers by name. Always call this before creating a new supplier."
  },
  "connect" : [
    { "id" : "f4", "to" : "f5" }
  ]
}
```

Error behavior inside a sub-process tool:
- **A BpmError** (ErrorEnd, or `BpmError.create(...).throwError()`) stops the agent. It is re-thrown at the AgenticProcessCall element with the extra attributes `tool.name`, `tool.arguments`, `tool.id` and `ai.invocationId`. Catch it with an `ErrorBoundaryEvent` on the agent element. This is also how [human-in-the-loop](human-in-the-loop.md) works.
- **Any other exception** goes back to the model as the tool's text result, and the agent keeps going.

---

## 2. Java tools (SPI)

Use a Java tool for pure computation or Java API access, where no process is needed.

```java
package com.example.tool;

import java.util.List;
import java.util.Map;

import com.axonivy.utils.smart.workflow.tools.provider.SmartWorkflowTool;

public class TaxCalculatorTool implements SmartWorkflowTool {

  public record TaxResult(double totalTax, double totalWithTax) {}

  @Override
  public String name() {
    return "calculateTax"; // default: the simple class name
  }

  @Override
  public String description() {
    return "Calculate tax for all invoice items. Returns total tax and total amount with tax.";
  }

  @Override
  public List<ToolParameter> parameters() {
    return List.of(
        new ToolParameter("invoice", "The invoice with line items", "com.example.Invoice"));
  }

  @Override
  public Object execute(Map<String, Object> args) {
    var invoice = (com.example.Invoice) args.get("invoice"); // already deserialized to the declared type
    double tax = invoice.getTotalAmount() * 0.1;
    return new TaxResult(tax, invoice.getTotalAmount() + tax); // String is passed through, anything else becomes JSON
  }
}
```

Register it with a provider:

```java
package com.example.tool;

import java.util.List;

import com.axonivy.utils.smart.workflow.tools.provider.SmartWorkflowTool;
import com.axonivy.utils.smart.workflow.tools.provider.SmartWorkflowToolsProvider;

public class MyToolProvider implements SmartWorkflowToolsProvider {
  @Override
  public List<SmartWorkflowTool> getTools() {
    return List.of(new TaxCalculatorTool());
  }
}
```

File `src/META-INF/services/com.axonivy.utils.smart.workflow.tools.provider.SmartWorkflowToolsProvider`:

```
com.example.tool.MyToolProvider
```

Providers are loaded from smart-workflow and from **every project that depends on smart-workflow**. Each provider class needs a public no-arg constructor.

---

## 3. Built-in tools

### webSearch

Searches the web (DuckDuckGo by default) and returns `{query, results[title,url,snippet], note}`.

```json
"system" : "You are a research assistant. Use the webSearch tool to find current information, then summarize the key findings.",
"tools" : "webSearch",
"resultType" : "com.example.WebSearchSummary.class",
"resultMapping" : "in.summary",
"query" : "<%=in.question%>"
```

Variables:
- `AI.Tool.WebSearch.Engine` (default `duckduckgo`)
- `AI.Tool.WebSearch.MaxResults` (default 5)
- `AI.Tool.WebSearch.WhitelistDomains` (comma list; empty allows all domains)

A custom engine implements `SmartWebSearchEngine` and is registered through a `SmartWebSearchEngineProvider` SPI.

### openSearchSearch

Semantic search over an OpenSearch index. See [rag.md](rag.md).

---

## Patterns

### Agent pipeline

A chain of agents where each one passes its result to the next. Put a `TaskSwitchEvent` (with `"skipTasklist" : true`) in front of each agent. That way every stage is tracked, and on failure the work resumes at that stage instead of re-running earlier LLM calls.

```
RequestStart → TaskSwitch "Task 1: Extract" → Agent (image → text) → Script (in.stream = null)
             → TaskSwitch "Task 2: Analyze" → SubProcessCall (analysis agent) → End
```

### Self-contained agent (agents as tools)

An orchestrator agent whose tools are **other agents**. Put them in the same callable sub-process file:
- One `CallSubStart` is the public entry. It calls the orchestrator agent with `"tools" : "extractHeaderInfo,extractLineItems,validateAmounts"`.
- Each tool is another `CallSubStart` in the same file, tagged `tool` and with a `visual.description`. Each one leads to its own focused AgenticProcessCall (`"tools" : ""`) and then a `CallSubEnd`.
- The orchestrator's system prompt lists the tools and the order to call them in.

This keeps each specialist prompt small, and the orchestrator decides the flow.

### Calling an agent from Portal or generic code

smart-workflow ships the callable `Portal/SmartWorkflowAgent:invokeAgent(String query, String systemMessage, List<String> tools, Class resultType)` with result `resultObject`. Use it when the agent parameters are only known at runtime.
