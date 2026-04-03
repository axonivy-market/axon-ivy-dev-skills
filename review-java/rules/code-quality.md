# Code Quality Rules — M4, L1–L3

Apply to all files.

---

**M4a. Always Use Braces — Control Flow and Methods**
*Scan for:* `if`, `else`, `for`, `while` statements without curly braces (including single-line guard returns); **methods written as single-line inline bodies** (`public String getFoo() { return foo; }`).
*Why:* Brace-less and single-line bodies are a common source of bugs when a second statement is added. Consistent multi-line formatting makes control flow and method bodies unambiguous at a glance.

```java
// ✗ — brace-less guard
if (caseNode == null || selectedTaskUuid == null) return null;

// ✓ — always use braces
if (caseNode == null || selectedTaskUuid == null) {
  return null;
}

// ✗ — single-line method body
public String getRole() { return role; }

// ✓ — expand to full method body
public String getRole() {
  return role;
}
```

---

**M4. Self-Documenting Code — No Restatement Comments**
*Scan for:* inline comments that restate what the code already clearly expresses; sub-steps inside a method described by a comment instead of a named private method.
*Why:* Restatement comments become outdated and misleading. If a comment describes a step, extract that step into a private method whose name *is* the documentation. Reserve comments only for non-obvious *why* reasoning.

---

**L1. Dedicated Types for Constants and Error Codes**
*Scan for:* error codes, status strings, or configuration keys scattered as fields on large classes rather than in a dedicated interface or enum.
*Why:* Scattered constants are hard to discover and maintain. Extract into a dedicated type (e.g., `GuardrailErrors`, `StatusCodes`).

---

**L1b. Extract Constructor Type Discriminator Strings to Enum**
*Scan for:* the same constructor or factory called multiple times across a class where the **first argument is a string literal acting as a type selector** (e.g. `new DefaultTreeNode<>("case", data, parent)`, `new DefaultTreeNode<>("task", data, parent)`).
*Why:* These are type codes in disguise. Changing one value requires grep across the whole codebase. Centralize in an enum that owns the string key, any associated behaviour (e.g. `expandedByDefault`), and a factory method — so all nodes of that type are configured in exactly one place.
```java
// ✗ — raw strings as type discriminators, expansion state scattered
TreeNode<Object> n1 = new DefaultTreeNode<>("case", data, parent);
n1.setExpanded(false);
TreeNode<Object> n2 = new DefaultTreeNode<>("task", data, parent);
n2.setExpanded(false);

// ✓ — enum owns the key and default state; callers are identical
public enum HistoryNodeType {
  CASE("case", false), TASK("task", false);
  public TreeNode<Object> createNode(Object data, TreeNode<Object> parent) {
    TreeNode<Object> node = new DefaultTreeNode<>(key, data, parent);
    node.setExpanded(expandedByDefault);
    return node;
  }
}
HistoryNodeType.CASE.createNode(data, parent);
HistoryNodeType.TASK.createNode(data, parent);
```

---

**L2. YAGNI — No Speculative Code**
*Scan for:* utility classes, helper methods, or configuration hooks with no current caller; abstractions introduced for hypothetical future requirements; filter fields wired to UI forms but never passed to any query.
*Why:* Code written for futures that may never arrive adds maintenance burden with zero present value. Delete it; re-add when a concrete use case exists.

---

**L3. Unit Test Coverage for Complex Logic**
*Scan for:* new algorithmic units (parsers, converters, validators, correlators, tree builders) with no accompanying test class.
*Why:* Non-trivial logic without tests is a maintenance liability. Testability pressure also often reveals missing interface extraction — a design benefit, not just a testing convenience.
