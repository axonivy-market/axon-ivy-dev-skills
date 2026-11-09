# Guardrails and the Circuit Breaker

Guardrails check the user message before it reaches the model (input) and the model's answer before it is returned (output).

## Selecting guardrails

On the element:

```json
"inputGuardrails" : "PromptInjectionInputGuardrail,PiiMaskingGuardrail",
"outputGuardrails" : "SensitiveDataOutputGuardrail,PiiMaskingGuardrail"
```

- If a key is empty, the application defaults apply: `AI.Guardrails.DefaultInput` and `AI.Guardrails.DefaultOutput` in `variables.yaml` (also comma-separated).
- Unknown names are ignored silently, so check the spelling.

## Built-in guardrails

| Name | Side | What it does |
|------|------|-------------|
| `PromptInjectionInputGuardrail` | input | Regex detection of prompt injection: "ignore previous instructions", "forget everything", "pretend to be", "you are now", "reveal your system prompt", `system:`, `assistant:`, 10+ special characters in a row, and **any control character**. Blocks the message. |
| `AiPromptInjectionInputGuardrail` | input | Asks a separate LLM to classify the message (YES/NO). Catches more than the rule-based one, but costs one extra LLM call per agent call. |
| `PiiMaskingGuardrail` | input + output | Replaces IP and MAC addresses, emails, phone numbers (with `+` or `00` prefix), credit card numbers (Luhn-checked), US SSNs and dates of birth with placeholders before the LLM sees them, then restores the originals in the answer. **Put it in both lists** or the placeholders stay in the result. |
| `SensitiveDataOutputGuardrail` | output | Blocks answers that contain API keys (OpenAI `sk-`, AWS, GitHub, Google, xAI), private keys, or any configured provider secret. |

> **Gotcha: `PromptInjectionInputGuardrail` and line breaks.** Its control-character check (`[\x00-\x1F\x7F]`) also matches `\n`, `\r` and `\t`. Any multi-line `query`, or input text containing line breaks, is **blocked**. With this guardrail, keep the query on one line and flatten the input first, e.g. `<%=in.text.replaceAll("\\s+", " ")%>`. Otherwise use `AiPromptInjectionInputGuardrail` instead.

Configuration for `AiPromptInjectionInputGuardrail` (`AI.Guardrails.PromptInjection.Classifier.*`):
- `Provider` and `Model`: use a small, cheap model, e.g. `gpt-4.1-nano`. Blank means the default provider and its default model.
- `SystemPrompt`: a custom classifier prompt. It must instruct the model to answer only YES or NO.
- `MinLength`: messages shorter than this are not classified (default `0`, meaning all are).

## Handling a block

A blocked call throws a BpmError with code `smartworkflow:guardrail:input:violation` or `smartworkflow:guardrail:output:violation` (all codes: "Error codes to catch" in [SKILL.md](../SKILL.md)). Catch it on the agent element:

```json
"boundaries" : [ {
    "id" : "f10",
    "type" : "ErrorBoundaryEvent",
    "name" : "Guardrail violation",
    "config" : {
      "errorCode" : "smartworkflow:guardrail:input:violation",
      "output" : {
        "map" : {
          "out" : "in",
          "out.error" : "error"
        }
      }
    },
    "visual" : {
      "at" : { "x" : 616, "y" : 273 },
      "icon" : "res:/webContent/icons/shield.png"
    },
    "connect" : [
      { "id" : "f11", "to" : "f8" }
    ]
  } ]
```

`error.getMessage()` contains the guardrail's reason.

## Custom guardrails

Implement `SmartWorkflowInputGuardrail` and/or `SmartWorkflowOutputGuardrail`:

```java
package com.example.guardrails;

import java.util.Locale;

import com.axonivy.utils.smart.workflow.guardrails.entity.GuardrailResult;
import com.axonivy.utils.smart.workflow.guardrails.entity.SmartWorkflowInputGuardrail;

public class BlockCompetitorMentionGuardrail implements SmartWorkflowInputGuardrail {

  @Override
  public GuardrailResult evaluate(String message) {
    if (message != null && message.toLowerCase(Locale.ROOT).contains("acme corp")) {
      return GuardrailResult.block("Do not reference competitor products in AI queries.");
    }
    return GuardrailResult.allow();
  }

  @Override
  public String name() {
    return "BlockCompetitorMentionGuardrail"; // default: the simple class name; this name goes into inputGuardrails
  }
}
```

`GuardrailResult` options:
- `allow()`: pass the message unchanged.
- `allowWithRewrite(text)`: replace the message, e.g. for masking or redaction.
- `block(reason)`: stop the call. The agent element throws the violation error with this reason.
- `block(reason, cause)`: same, with a typed cause attached.

If the guardrail needs per-call state (like PII masking does), override `evaluate(String message, String invocationId)` instead.

Register it with a provider:

```java
package com.example.guardrails;

import java.util.List;

import com.axonivy.utils.smart.workflow.guardrails.entity.SmartWorkflowInputGuardrail;
import com.axonivy.utils.smart.workflow.guardrails.entity.SmartWorkflowOutputGuardrail;
import com.axonivy.utils.smart.workflow.guardrails.provider.GuardrailProvider;

public class MyGuardrailProvider implements GuardrailProvider {
  @Override
  public List<SmartWorkflowInputGuardrail> getInputGuardrails() {
    return List.of(new BlockCompetitorMentionGuardrail());
  }

  @Override
  public List<SmartWorkflowOutputGuardrail> getOutputGuardrails() {
    return List.of();
  }
}
```

File `src/META-INF/services/com.axonivy.utils.smart.workflow.guardrails.provider.GuardrailProvider`:

```
com.example.guardrails.MyGuardrailProvider
```

Custom guardrails then appear in the element editor's guardrail pickers and can be listed in `AI.Guardrails.DefaultInput` and `AI.Guardrails.DefaultOutput`.

## Circuit breaker (emergency stop)

The circuit breaker is an internal guardrail that is always active. While it is on, **every** agent call in the application fails immediately with `smartworkflow:stop`.

There are two ways to switch it:
- Set the variable `AI.CircuitBreaker.Enabled` to `"true"` or `"false"` (cockpit or `variables.yaml`).
- Call it from code:

```java
import com.axonivy.utils.smart.workflow.guardrails.circuitbreaker.CircuitBreakerSignal;

CircuitBreakerSignal.stopAll();   // sets AI.CircuitBreaker.Enabled = true
CircuitBreakerSignal.resumeAll(); // sets it back to false
```

Handle `smartworkflow:stop` wherever stopping must not crash the case. For example, set an `isStopped` flag and route to an alternative path:

```json
{
  "id" : "f26",
  "type" : "ErrorBoundaryEvent",
  "name" : "Agent stopped",
  "config" : {
    "errorCode" : "smartworkflow:stop",
    "output" : { "map" : { "out" : "in", "out.error" : "error" } }
  },
  "visual" : { "at" : { "x" : 328, "y" : 353 }, "icon" : "res:/webContent/icons/shield.png" },
  "connect" : [ { "id" : "f27", "to" : "f28" } ]
}
```
