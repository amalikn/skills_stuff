**Title:** Pad for spec-driven development

**Source:** [https://www.getpad.dev/spec-driven](https://www.getpad.dev/spec-driven)

---

# Page Structure Map
```text
Pad for spec-driven development
├── The lifecycle
├── The enforcement half
├── Already have a codebase? Extract the specs from it
├── Verified, criterion by criterion
└── Runs where your code runs
```

---

Specs that live next to the work they govern.

Spec-first tools stop at the spec. You write a careful document, implementation happens somewhere else, and six weeks later nobody knows whether the code still matches it. Pad keeps the spec, the tasks it decomposed into, the conventions that enforce it, and the audit trail that proves it, in one workspace that you and your agents both read and write.

## The lifecycle

`pad workspace init myproject --template spec` seeds a workspace where specs are the parenting artifact: idea → spec → tasks → PRs. A spec moves from draft to in-review to approved to implemented. When an approved spec needs to change, it gets superseded by a new one that references it; silent edits to reviewed specs are against the rules, and the rules ship with the template.

Every new spec starts from the same skeleton: Context, Goals, Non-goals, Specified behavior, Acceptance criteria, Open questions. Acceptance criteria carry stable AC-N ids, and the template is blunt about what qualifies as one:

> AC-1: a statement an agent or reviewer could actually check against the diff or running behavior — if you can't say how you'd verify it, it belongs in Goals, not here

## The enforcement half

Most spec-driven tooling has no enforcement half. In Pad, conventions fire at the trigger points agents actually hit. Two of the four that ship with the template:

> **No implementation without an approved spec** (on-implement): "Before implementing, load the governing SPEC-N and confirm its status is `approved`... don't implement against a draft or in-review spec, its acceptance criteria can still change out from under you."

> **PRs cite the spec and which criteria they satisfy** (on-pr-create): every PR body cites its SPEC-N and lists the criteria it satisfies, like "Implements SPEC-4, satisfies AC-1, AC-2". That citation is what makes review fast: the reviewer walks the cited criteria against the diff instead of re-deriving what the PR was supposed to do.

An agent working in a Pad workspace loads these rules before it acts. Approved specs gate implementation. PRs are checkable against the criteria they claim.

## Already have a codebase? Extract the specs from it

Greenfield tools like Kiro and spec-kit assume you start from the spec. Most codebases started years before anyone wrote one.

`/pad extract-specs target="webhook delivery"` reads a subsystem and proposes specs describing what the code actually does. There is exactly one human checkpoint: the agent presents a subsystem map, you pick which parts to extract. Every extracted spec then opens with a provenance marker:

> **Extracted from observed behavior** in `<paths>` on `<date>`. This spec describes what the code currently does, not independently-verified design intent — review carefully; if something here reads as a bug, that's the point of review, not a drafting error.

Extraction doubles as an audit. Behavior that looks unintentional lands in Open questions instead of being quietly specified as correct, and the review that flips a draft to approved is where "that's actually a bug" gets caught. The playbook's own instruction to the agent: notice and flag, don't adjudicate.

Coverage grows along the path of real work. You extract the subsystem you're about to touch, and the playbook will push back if you ask it to sweep the whole codebase at once.

## Verified, criterion by criterion

`/pad verify SPEC-4` walks each acceptance criterion against the actual diff or running behavior and reports pass, fail, or can't-tell for every one, citing the test name or file that decided it. Fails cite the contradicting behavior. Can't-tells are reported honestly instead of guessed. When everything passes on an approved spec, the agent offers to flip it to implemented.

In the playbook's words, this is what makes "approved" mean something more than "reviewed once." Spec-code drift is a bug in one of them, and the workspace treats it that way until someone resolves which.

## Runs where your code runs

Pad is a single self-hosted binary (SQLite or Postgres), or Pad Cloud if you'd rather not host. Claude Code, Cursor, Codex, and anything MCP-speaking share the same workspace, the same specs, the same conventions. The audit trail — who changed what, which PR satisfied which criterion, why a spec was superseded — accumulates as a side effect of working.

```
brew install PerpetualSoftware/tap/pad
pad init
pad workspace init myproject --template spec
```
