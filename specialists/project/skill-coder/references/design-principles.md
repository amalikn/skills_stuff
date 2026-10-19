---
Title: Design principles
Category: reference
Status: current
Authority: local-supplement
Scope: How to shape a program of any size and language before writing its code
Last reviewed: 2026-10-19
Summary: >-
  Layers with dependencies pointing inward, thin front ends, earned abstraction, data decides and code executes, one seam per
  external system, native first and reuse before build with a search order, and stdlib in the core.
---

# Design principles

Rules here hold in every language. A project's own architecture document outranks them; read it first. Most of these rules were first written as the code architecture target design of a governed
project (unified-network-controller) and are generic.

## Contents

- [The principles](#the-principles)
- [Layers](#layers)
- [Native first, reuse before build](#native-first-reuse-before-build)
- [When the principles conflict](#when-the-principles-conflict)

## The principles

| #   | Principle                 | In practice                                                                                               | Why                                                    |
| --- | ------------------------- | --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| 1   | One package, many         | The CLI, scheduled jobs, an HTTP API and UI handlers are thin: parse input, build a run context, call one | A fix written once reaches every front end             |
|     |   front ends              |   service, render the result                                                                              |                                                        |
| 2   | Dependencies point inward | Core records and pure policy import nothing outward; backends and drivers depend on the core, never the   | Inner layers test with no network and no               |
|     |                           |   reverse; no import cycles                                                                               |   tool installed                                       |
| 3   | The product's             | Services speak of the domain (device, order, invoice); a tool or vendor name appears only in the module   | Replacing a tool does not ripple into callers          |
|     |   own vocabulary          |   that talks to it                                                                                        |                                                        |
| 4   | Data decides,             | Facts about kinds of things (capabilities, limits, mappings) live in a data file; code reads them and     | One fact has one home, so two copies cannot disagree   |
|     |   code executes           |   never restates them                                                                                     |                                                        |
| 5   | One seam per              | One client module per outside system; retries, timeouts, paging and error translation live there          | A behaviour is fixed in one place and every caller     |
|     |   external system         |                                                                                                           |   gets the fix                                         |
| 6   | Safe by construction      | Read is the default; writes need an explicit plan and apply; the layer below enforces budgets and gates   | A caller cannot forget a safety rule                   |
|     |                           |                                                                                                           |   (see [safety-and-writes.md](safety-and-writes.md))   |
| 7   | Native first, reuse       | Use what the platform and its libraries already offer; build only a thin adapter                          | Less code to own; upgrades come for free               |
|     |   before build            |                                                                                                           |                                                        |
| 8   | Earned abstraction        | A contract, layer or service exists when two real consumers need it, or a named future one does; it names | Speculative layers cost reading time and never         |
|     |                           |   them in its docstring                                                                                   |   pay back                                             |
| 9   | Standard library in       | Third-party libraries sit only in the layers that need them                                               | The core stays easy to test and to upgrade             |
|     |   the core                |                                                                                                           |   (see [dependencies.md](dependencies.md))             |

## Layers

A typical layered program, innermost first. Outer rings may use inner rings, never the reverse.

```text
+--------------------------------------------------------------+
| FRONT ENDS   CLI | jobs | API handlers      thin; no rules   |
|  +--------------------------------------------------------+  |
|  | SERVICES   use cases in the product's vocabulary       |  |
|  |  +--------------------------------------------------+  |  |
|  |  | BACKENDS + DRIVERS   one seam per outside system |  |  |
|  |  |  +--------------------------------------------+  |  |  |
|  |  |  | CONTRACTS   interfaces, each earned        |  |  |  |
|  |  |  |  +--------------------------------------+  |  |  |  |
|  |  |  |  | POLICY + DATA   pure decisions       |  |  |  |  |
|  |  |  |  |  +--------------------------------+  |  |  |  |  |
|  |  |  |  |  | CORE   records, errors, settings|  |  |  |  |  |
|  |  |  |  |  +--------------------------------+  |  |  |  |  |
|  |  |  |  +--------------------------------------+  |  |  |  |
|  |  |  +--------------------------------------------+  |  |  |
|  |  +--------------------------------------------------+  |  |
|  +--------------------------------------------------------+  |
+--------------------------------------------------------------+
```

- Write the layer table down (which package may import which) and check it mechanically; the pack's `scripts/import_layers.py` does this for Python. Why: a rule that is only in a reviewer's head
  erodes.
- Records crossing a layer are typed values (a dataclass, struct or record type), not loose maps. Why: the shape is checked once, at the boundary.
- An interface (a Python `Protocol`, a Go interface, a Rust trait, a TypeScript interface) is defined by the consumer that needs it, and every implementation has a fake for tests. Why: a fake lets
  services be tested without the outside system.
- A small single-purpose script does not need all six rings. Apply principle 8: a one-off administrator task stays a task.

## Native first, reuse before build

Before writing new code, search in this order and record what you found (a sentence in the change, or a research report where the project keeps them):

1. **The project itself.** An existing helper, seam or data file that already answers the need. Why: a second copy is the commonest source of drift.
2. **The platform's native objects.** What the framework or application already models (a built-in relationship, location type or setting). Recommend it before a custom field or model, and propose
   custom only with the reason native cannot hold it. Why: the operator rejected custom fields where a native object fitted (operator lesson, 2026-10-09).
3. **The standard library** of the language.
4. **The platform's installed extensions and the vendor's own libraries.**
5. **Established community libraries**, judged by maintenance, licence and supply-chain posture ([security.md](security.md)).
6. **Build**, as a thin adapter: one module calls the tool, the version relied on is noted, and a test fails if an upgrade changes the behaviour relied on.

Say so when something is confusing or a better option exists. Before building on a decided layer, read the decision's inherited constraints in the project's decision register. Why: a design that
ignores a recorded constraint is rework.

## When the principles conflict

The project's rules win, then safety (principle 6), then correctness, then simplicity. If two sources the agent reads disagree, stop and report the conflict; do not guess. Why: a silent merge of two
contradicting rules hides the decision from its owner.
