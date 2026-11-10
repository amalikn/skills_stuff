**Title:** cmdhelp v0.1 — A CLI help standard for LLMs

**Source:** [https://www.getpad.dev/cmdhelp](https://www.getpad.dev/cmdhelp)

---

# Page Structure Map
```text
cmdhelp v0.1 — A CLI help standard for LLMs
├── 1\. Goal
├── 2\. Non-goals
├── 3\. Surface
│   ├── Formats
│   └── Flags
├── 4\. Scope levels
├── 5\. JSON schema (--format json)
│   ├── 5.1 Argument-type vocabulary
│   ├── 5.2 exit\codes shape
│   └── 5.3 Boolean flag arity
├── 6\. Markdown shape (--format md)
├── 7\. Context-awareness (the key differentiator)
├── 8\. Discovery
├── 9\. Versioning
├── Implementations
├── Why this can become a real standard
└── Adopt cmdhelp in your CLI
```

---

## 1\. Goal

Define a small, vendor-neutral convention for CLI tools to expose their documentation and invocation schema to LLMs and LLM harnesses (Claude Code, Cursor, MCP servers, IDE plugins). Two outputs from one source of truth:

- **Markdown** — drop-in context for an LLM to *read*.
- **JSON** — schema for an LLM (or its harness) to *call*.

## 2\. Non-goals

- Replace `man` pages, `--help`, or `tldr`.
- Define how to *execute* a CLI (that is MCP / shell / language SDKs).
- Specify the prose content — only the *envelope*.
- **Emit MCP server descriptors directly.** MCP descriptor generation is a downstream transformation of `--format json`, not a first-class cmdhelp output (see §11 Q3).

## 3\. Surface

Every conforming CLI MUST support the **mandatory surface**:

```
<cmd> help [subcommand…] [--format <fmt>] [--depth <n>]
```

Plus capability discovery (mandatory; the flag location varies — see §8).

A CLI MAY additionally support optional convenience flags (e.g. `--all`); these are not part of the mandatory surface.

### Formats

| `--format` | Mandatory? | Purpose |
| --- | --- | --- |
| `text` | yes (default) | Existing human-readable `--help` |
| `md` | yes | Markdown for LLM context ingestion |
| `json` | yes | Structured schema for programmatic dispatch |
| `llm` | optional alias | Equivalent to `md` today; reserved for future "best for LLMs" default |

### Flags

| flag | Mandatory? | Purpose |
| --- | --- | --- |
| `--format <fmt>` | yes | One of the supported formats. CLIs MUST support `text`, `md`, `json`; MAY support `llm` (alias for `md`). |
| `--depth <n>` | yes | Truncate the command tree to N levels (canonical scope control — see §4) |
| `--all` | no | MAY be supported as a convenience alias for "unlimited depth + full detail" |

A CLI MAY also accept `<cmd> <subcommand> --help --format md` for ergonomic parity, but `<cmd> help <subcommand> --format md` is the canonical form.

## 4\. Scope levels

Default behavior depends on what the user has narrowed to:

- `<cmd> help` → **tree summary**: subcommand list with one-line descriptions only. No flags, args, or examples are emitted. Equivalent to `--depth=0`.
- `<cmd> help <group>` → same summary, scoped to one subtree.
- `<cmd> help <group> <command>` → single command with **full detail** (flags, args, examples, output). At a leaf, default is full detail, not summary.
- `--depth=N` (canonical) → controls expansion at tree/subtree scope: `--depth=0` is summary; each increment recurses one more level with full detail.
- `--all` → MAY be supported as a convenience alias for "unlimited depth + full detail at every level". Implementations are not required to support `--all`; consumers SHOULD prefer `--depth` for portable behavior.

## 5\. JSON schema (--format json)

```
{
  "cmdhelp_version": "0.1",
  "binary": "pad",
  "version": "1.4.2",
  "summary": "Pad — project management for developers and AI agents",
  "homepage": "https://getpad.dev",
  "global_flags": { /* same shape as command flags */ },
  "commands": {
    "item create": {
      "summary": "Create a new item in a collection.",
      "args": [
        { "name": "collection", "type": "enum", "required": true,
          "enum_source": "dynamic:pad collection list",
          "enum": ["tasks","ideas","plans","docs","..."] },
        { "name": "title", "type": "string", "required": true }
      ],
      "flags": {
        "priority": { "type": "enum", "enum": ["low","medium","high","critical"] },
        "parent":   { "type": "ref" },
        "field":    { "type": "string", "repeatable": true, "format": "key=value" },
        "stdin":    { "type": "bool" },
        "cache":    { "type": "bool", "negate_flag": "--no-cache" }
      },
      "stdin": { "accepted": true, "format": "text/markdown" },
      "stdout": {
        "text_template": "Created {ref}: {title}",
        "json_schema_ref": "#/schemas/Item"
      },
      "exit_codes": {
        "0": "ok",
        "2": { "when": "validation error",
               "recovery": "Check argument types and try again" },
        "4": { "when": "not authenticated",
               "recovery": "Run pad auth login" }
      },
      "examples": [
        { "cmd": "pad item create task \"Fix OAuth\" --priority high",
          "note": "create a high-priority task" }
      ],
      "see_also": ["item update", "item delete"],
      "since": "0.1.0",
      "stability": "stable"
    }
  },
  "schemas": { "Item": { /* JSON Schema */ } },
  "context": {
    "workspace": "docapp",
    "collections": ["tasks","ideas","..."]
  }
}
```

Required keys: `cmdhelp_version`, `binary`, `commands`. Each command requires `summary`. Everything else is optional.

### 5.1 Argument-type vocabulary

Argument and flag `type` values are drawn from a closed set, plus an extension namespace for tool-specific types.

- **Required** (every conforming implementation MUST recognise): `string`, `int`, `float`, `bool`, `enum` (paired with `enum: [...]`).
- **Recommended** (every conforming implementation SHOULD support): `path`, `url`, `duration`, `date`, `datetime`, `json`, `ref`.
- **Extension**: types prefixed `x-` are tool-specific (e.g. `x-pad-issue-ref`). Wrappers MAY treat unknown `x-*` types as `string`.

The `ref` type denotes an **opaque tool-specific identifier** (e.g. an issue ID like `TASK-5`, a commit hash, a resource URI). Wrappers MUST treat the value as opaque — they MAY render it as a clickable resource link in UIs but MUST NOT attempt to parse or validate the value beyond passing it through unchanged. Tools wanting stricter semantics SHOULD use the `x-*` extension namespace instead.

### 5.2 exit\_codes shape

Each entry MAY be either a terse string or a rich object. v0.1 defines this as a string-or-object **union from day one** — there is no "old" shape; consumers MUST tolerate both forms:

```
"exit_codes": {
  "0": "ok",                                      // string form, terse
  "2": { "when": "validation error",              // object form, rich
         "recovery": "...",                       // optional
         "message_template": "Invalid: {field}" } // optional
}
```

Object form requires `when`. Both forms are valid; tools choose per-code based on whether the extra structure adds value. Validators (e.g. `cmdhelp.schema.json`) MUST encode `oneOf: [string, object]` for each entry.

### 5.3 Boolean flag arity

CLI booleans are not pure values — flags appear in multiple invocation styles. To make `bool` flags reliably invokable from an LLM:

- A `bool` flag is a **presence switch** by default. The flag is either present (true) or absent (false). It MUST NOT accept a value on the command line.
- If a flag accepts an explicit value (e.g. `--cache=true`, `--cache=false`), declare it as `"type": "enum", "enum": ["true", "false"]` instead of `bool`.
- Negation flags (e.g. `--no-cache`) are declared on the original flag using the optional `negate_flag` field.

Wrappers SHOULD render presence-switch booleans without a value when constructing invocations, and MUST NOT pass `true` / `false` as a separate argument unless the flag is `enum`\-typed.

## 6\. Markdown shape (--format md)

Single markdown doc with a **predictable section order** so LLMs can pattern-match. Per command:

````markdown
## `<cmd> <subcommand>`

<one-line summary>

### Synopsis
`<usage line>`

### Arguments
| name | type | required | description |

### Flags
| flag | type | default | description |

### Stdin
<if accepted>

### Examples
```bash
…runnable examples…
```

### Output
<text + JSON schema notes>

### Workspace context
<dynamic, optional — e.g. "Available collections: …">

### See also
- `<cmd> <related>`
````

The doc MAY include YAML frontmatter:

```yaml
---
cmdhelp_version: "0.1"
binary: pad
version: 1.4.2
generated: 2026-05-01T15:00:00Z
---
```

Examples in `--format md` MUST be drawn from the same canonical example set as `--format json` — same source, different rendering. Conforming implementations **MUST** validate examples in their test suite (parse each example's `cmd`, verify it resolves against the actual flag tree) so semantic drift between docs and implementation is caught at build time.

## 7\. Context-awareness (the key differentiator)

CLIs with session state (workspace, project, account) SHOULD splice **dynamic facts** into help output:

- Available enum values (collections, projects, environments)
- Currently selected workspace / profile
- Auth status

JSON marks these with `enum_source: "dynamic:<command>"`. Markdown puts them under `### Workspace context`. This is what makes the format dramatically more useful than a static man page for an LLM.

## 8\. Discovery

Conforming CLIs MUST expose a capability bit. Either of two forms is acceptable:

```
# Default form — preferred when `help` is not already overloaded:
$ <cmd> help --capabilities
cmdhelp/0.1: text, md, json, llm

# Fallback form — for CLIs whose `help` subcommand has tool-specific behavior:
$ <cmd> --cmdhelp-capabilities
cmdhelp/0.1: text, md, json, llm
```

Whichever form the CLI exposes, it MUST be:

- **Single-line** on stdout, parseable, stable across releases.
- **Side-effect-free** — no logging, no network calls, no config writes, no auth challenges.
- **Exit 0** on success.

Format: `cmdhelp/<MAJOR>.<MINOR>: <comma-separated formats>`. The format list MUST include every supported format, including the mandatory `text`. Order is not significant.

## 9\. Versioning

The wire format `cmdhelp_version` is **`MAJOR.MINOR`** (no patch component):

- **MAJOR** bumps are breaking changes — consumers expecting an earlier MAJOR will not understand the new shape.
- **MINOR** bumps are additive, non-breaking — new optional fields, new format aliases, new recommended types. Tools advertising `0.1` MUST tolerate unknown fields (forward-compat).

There is **no PATCH** in the wire format — patch-level corrections are implementation details and never appear in `cmdhelp_version` or `--capabilities` output. Implementations bump their own software versions independently in `version`.

Examples: `cmdhelp_version: "0.1"`, `cmdhelp/0.1: text, md, json, llm`. Both are correct. `0.1.0` is **not** a valid wire version.

## Implementations

| Tool | Status | Notes |
| --- | --- | --- |
| [**Pad**](https://getpad.dev/) | Reference implementation (v0.1) | Cobra-based. [internal/cmdhelp](https://github.com/PerpetualSoftware/pad/tree/main/internal/cmdhelp) drives all four formats. Try it: `pad help --format json`. |
| *Your CLI here* | — | Implement the spec, advertise `cmdhelp/0.1`, and [open an issue](https://github.com/PerpetualSoftware/pad/issues) to be listed. |

## Why this can become a real standard

1. **Tiny surface.** One verb (`help`), three formats. Trivial for any CLI to add.
2. **Already aligned with Cobra / clap / click conventions.** Doc generators exist; we just need a uniform output shape.
3. **Solves a real, current pain.** Every agent harness currently re-implements its own way to teach an LLM about CLIs.
4. **Composable with MCP.** JSON output is a foundation for MCP tool descriptors. Operation naming, transport (stdio / SSE / streamable HTTP), auth, error mapping, and confirmation policy live downstream — but the input shape and command surface come straight from cmdhelp. No `--format mcp` needed.

## Adopt cmdhelp in your CLI

1. Read this spec. Implement `<cmd> help --format json|md` and the capability bit. Pad's [reference implementation](https://github.com/PerpetualSoftware/pad/tree/main/internal/cmdhelp) is ~600 LoC of Go (Cobra-based) and is permissively licensed — copy/adapt freely.
2. Validate your `--format json` output against [`cmdhelp.schema.json`](https://www.getpad.dev/cmdhelp.schema.json) as a CI step. The schema enforces every contract in §3–§9.
3. Add an example-vs-flag-tree validator to your test suite (spec §6 drift-prevention contract). Pad's implementation is in [`example_validation.go`](https://github.com/PerpetualSoftware/pad/blob/main/internal/cmdhelp/example_validation.go).
4. [Open an issue](https://github.com/PerpetualSoftware/pad/issues) to be listed in the Implementations table above.

---

Spec drafted 2026-05-01 in conversation with Claude. v0.1 frozen 2026-05-01 after four rounds of independent review. Reference implementation tracked at [PerpetualSoftware/pad](https://github.com/PerpetualSoftware/pad). This page mirrors the spec text; the canonical source is [`schema/cmdhelp.schema.json`](https://github.com/PerpetualSoftware/pad/blob/main/schema/cmdhelp.schema.json) plus the design doc in pad's workspace (IDEA-927).
