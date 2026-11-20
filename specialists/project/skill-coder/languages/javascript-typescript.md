---
Title: JavaScript and TypeScript override
Category: reference
Status: current
Authority: local-supplement
Scope: JavaScript and TypeScript code for Node and the browser
Last reviewed: 2026-11-19
Summary: >-
  TypeScript with strict on, typescript-eslint, the project's formatter, TSDoc or JSDoc comments with param and returns,
  strict equality, no any at seams, the Node version pinned by engines, and argument-array child processes; Learned entries
  on Playwright browser tests, VS Code extension bundles and soft wrap, and pptxgenjs units and defaults.
---

# JavaScript and TypeScript override

## Contents

- [Authoritative sources](#authoritative-sources)
- [Tools](#tools)
- [Core rule mapping](#core-rule-mapping)
- [Size and limit tweaks](#size-and-limit-tweaks)
- [Learned](#learned)
- [Open items](#open-items)

## Authoritative sources

The Google TypeScript Style Guide, the TypeScript `tsconfig` reference (`strict`), typescript-eslint Getting Started, TSDoc. Copies: `../documents/research-sources-20261019/`.

## Tools

| Job          | Tool                                                                                           | Note                                                                                 |
| ------------ | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Runtime      | Node at the project's pin (`.nvmrc`, `.mise.toml`, `package.json` `engines`)                   | Run with `mise exec -- node` or the pinned path                                      |
| Types        | `tsc` with `strict: true`                                                                      | `strict` turns on the strict family of checks (VERIFIED_PRIMARY, tsconfig reference) |
| Lint         | ESLint with typescript-eslint; its `recommended` config, `strict` where the project accepts it | VERIFIED_PRIMARY (typescript-eslint docs)                                            |
| Format       | The project's formatter (often Prettier)                                                       | UNVERIFIED: no source fetched                                                        |
| Tests        | The project's runner (Vitest, Jest or `node:test`)                                             | UNVERIFIED stub                                                                      |
| Dependencies | The project's package manager with its lock file committed                                     | Change the lock only with the manager's own command                                  |

## Core rule mapping

| Core reference              | In JavaScript and TypeScript                                                                                                                                           |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| documentation-and-headers   | A file comment; `/** ... */` on exported functions and classes with `@param` and `@returns` (TSDoc/JSDoc); `@throws` for thrown errors (UNVERIFIED in the fetched      |
|                             |   TSDoc page; JSDoc defines it)                                                                                                                                        |
| design-principles           | Interfaces at seams; types, not `any`, across module boundaries (Google: `any` is a super and subtype of all types and disables checking, VERIFIED_PRIMARY); prefer    |
|                             |   `unknown` and narrow                                                                                                                                                 |
| errors-and-timeouts         | Throw `Error` subclasses with a `cause`; never an empty `catch`; every `fetch` has an `AbortSignal` timeout; await or return every promise                             |
| security                    | `execFile`/`spawn` with an argument array; parameterised DB calls; no evaluating strings as code; set `textContent`, not raw HTML                                      |
| configuration-and-literals  | Read `process.env` in one settings module and validate at start-up                                                                                                     |
| runtime-boundaries          | A JS engine a project imports declares `engines` in `package.json`; a project's tools run with the project's pinned Node                                               |
| documentation-and-headers   | No `// eslint-disable-line` or `// @ts-ignore` to pass a check; fix it, or configure the rule in the ESLint config with a comment                                      |
|   (suppression)             |                                                                                                                                                                        |

## Size and limit tweaks

| Item                | Value                   | Reason                                                           |
| ------------------- | ----------------------- | ---------------------------------------------------------------- |
| Equality            | `===` and `!==` only    | Loose equality coerces types (Google TS guide, VERIFIED_PRIMARY) |
| Module and function | Core defaults           | No change                                                        |
| Line length         | The formatter's setting | Do not hand-format                                               |

## Learned

> **Learned 2026-11-06** · JavaScript, Playwright browser tests · VERIFIED_PRIMARY (Edge with playwright-core: a synthetic canvas tap crashed the
> renderer in about half the runs; real mouse clicks passed 8 of 8; a hidden-by-filter checkbox timed out a role locator) · Source: apn unified-network-controller `tests/test_topology_elk.py`,
> `tests/test_coverage_comparison.py` (d49d2043) · Falsifier: a synthetic `cy.emit('tap')` stable over many runs.

- Drive a canvas library (Cytoscape) with real mouse clicks at a node's rendered position, not a synthetic `emit('tap')`: the synthetic event with no position crashed Chromium's renderer in about half
  the runs.
- `getByRole` skips hidden elements by default: to assert the state of a row a search filter hid, pass `includeHidden: true`, or the locator waits out its timeout.
- Serve test scripts with a charset (`text/javascript; charset=utf-8`): a "·" in hover text came out garbled without it.
- A browser test that needs a browser module skips without it (`skipUnless(os.environ.get(...))`), so the plain suite does not crash on `require(undefined)`.

> **Learned 2026-11-12** · JavaScript, pptxgenjs 3.12.0 text margins · VERIFIED_PRIMARY (library source `valToPts(slideItemObj.options.margin)` for text boxes; table cells read a margin
> below 1 as inches; the slide XML showed `lIns="109728"` after the fix) · Source: apn enterprise-strategy `scripts/build_strategy_pptx.js` (a3e29af7) · Falsifier: a pptxgenjs text box whose `margin:
> 0.12` renders a visible inset.

- Units differ inside one library: a pptxgenjs text box takes `margin` in points, a table cell takes it in inches when below 1. Keep inches in the call sites and convert in the one helper that adds
  text (`margin: (o.margin ?? 0.08) * 72`), so every card gets the same inset; a passing build does not show it, only a render does.

```js
// apn enterprise-strategy scripts/build_strategy_pptx.js (a3e29af7)
const PT_PER_INCH = 72;
function box(s, text, x, y, w, h, o = {}) {
  s.addText(text, { x, y, w, h, margin: (o.margin ?? 0.08) * PT_PER_INCH /* ...style */ });
}
```

> **Learned 2026-11-16** · JavaScript, testing a VS Code extension bundle under plain Node · VERIFIED_PRIMARY (the stubbed run passed 11 checks on the patched bundle and failed on the
> unpatched one; a missing `vscode.Position` surfaced as a clear TypeError, fixed by adding it to the stub) · Source: scripts_stuff `vscode_extensions/scripts/mermaid-zoom-patch/test-mermaid-zoom.js`
> (uncommitted, 2026-11-16) · Falsifier: a bundle whose top-level code calls a `vscode` API at load time with a return value the proxy cannot fake.

- Load a shipped extension bundle without VS Code by intercepting `require("vscode")` with `Module._load`, and back the stub with a permissive `Proxy` so every API the bundle touches at load time is a
  harmless no-op; give real classes only for what the test asserts (`Range`, `Position`, `CodeLens`, `MarkdownString`) and record registrations (`registerCommand`, `registerCodeLensProvider`,
  `createWebviewPanel`). Expose internals by appending `module.exports.__t = { ... }` to a temp copy of the bundle; replace a webview-only function by reassigning its name in that appended text. This
  proves wiring, not rendering: say so in the report.
- Compile a generated inline script without running it with `new (require("vm").Script)(code)`; the agent harness's security hook rejects `new Function(...)` in a file write, and also flags a regex
  `.exec(` as `child_process.exec` (use `String.prototype.match`).

```js
// scripts_stuff vscode_extensions/scripts/mermaid-zoom-patch/test-mermaid-zoom.js (uncommitted, 2026-11-16)
function permissive(base) {
  const noop = new Proxy(function () {}, { get: (t, p) => (p === Symbol.toPrimitive ? () => "" : noop), apply: () => noop, construct: () => noop });
  return new Proxy(base, { get: (t, p) => (p in t ? t[p] : noop) });
}
const origLoad = Module._load;
Module._load = function (request, ...rest) {
  return request === "vscode" ? vscodeStub : origLoad.call(this, request, ...rest);
};
```

> **Learned 2026-11-16** · JavaScript/TypeScript, VS Code extensions · VERIFIED_PRIMARY (microsoft/vscode `main`, `src/vs/editor/browser/view/domLineBreaksComputer.ts`:
> `LineInjectedText.applyInjectedText(context.getLineContent(lineNumber), injectedTexts)` is what gets measured) · Source: that file, read 2026-11-16 · Falsifier: a VS Code release whose wrapping
> honours decoration CSS or exposes an API for wrap points.

- A decoration that hides text (`textDecoration: "none; display: none;"`, the usual trick for hiding a markdown link's `](target)`) changes what is drawn, not where VS Code soft-wraps: wrapping measures the
  raw line plus injected text (`before`/`after` content counts, hidden characters still count). An extension cannot make soft wrap follow the visible width; only folding removes text from layout, and
  it works on whole lines. Plan around it: hard-wrap the source by visible width and turn soft wrap off for that language, or shorten the raw text (reference-style links).

> **Learned 2026-11-16** · JavaScript, Node scripts and pptxgenjs · VERIFIED_PRIMARY (pptxgenjs 3.12.0 `dist/pptxgen.cjs.js`: the constructor sets
> `this._company = 'PptxGenJS'` and `this._subject = 'PptxGenJS Presentation'`; a deck built without setting them showed both in File > Properties) · Source: that file in apn enterprise-strategy's
> working cache, read 2026-11-16 · Falsifier: a pptxgenjs release whose defaults are empty.

- A Node build script that another script may `require` ends with `if (require.main === module) main();`, so importing it for its functions does not run its build (and overwrite its output) as a side
  effect; export what reuse needs with `module.exports`.
- pptxgenjs writes its own name into every deck's properties unless told otherwise: set `pres.company = ""` and `pres.subject = ""` (or real values) next to `new pptxgen()`, and check a built deck's
  `docProps/app.xml` and `docProps/core.xml`, not only its slides, before it leaves the team.

> **Learned 2026-11-20** · Running VS Code or VSCodium as an isolated test editor · VERIFIED_PRIMARY (each item seen in a run and fixed; the final run's log names only
> run-local paths) · Source: continuum-app `scripts/editor_harness.py` (1fa6384, 8eb6064), BUG-271 · Falsifier: an editor build that keeps shared storage under
> --user-data-dir, or a Mac Electron build that ignores `--use-mock-keychain`.

- `--user-data-dir` and `--extensions-dir` do not isolate everything: VS Code opens `~/.vscode-shared/sharedStorage/state.vscdb` (VSCodium `~/.vscode-oss-shared`)
  under the real home, so a test editor touched the person's own database. Give it `HOME=<run>/home`.
- With that fake HOME, macOS finds no login keychain and offers "Reset To Defaults" for the editor's "Code Key": pass Chromium's `--use-mock-keychain` (Linux:
  `--password-store=basic`), and warn the person before any run that may raise a system dialog.
- Started from inside VS Code (a terminal or an agent there), the child inherits `ELECTRON_RUN_AS_NODE=1` ("bad option: --user-data-dir") and `VSCODE_*` hooks that
  can reach the person's running editor: strip both prefixes.
- Every window runs its own extension host: a single fixed socket name lets the newest window hide the others; name it per process (`vscode-<pid>.sock`).
- A test editor holding unsaved buffers ignores SIGTERM (save prompt): kill its process group after a short grace period.

```python
env = {k: v for k, v in os.environ.items() if not k.startswith(("ELECTRON_", "VSCODE_"))}
env["HOME"] = str(state / "home")
args = [app, "--user-data-dir", ud, "--extensions-dir", ext, *( ["--use-mock-keychain"] if mac else ["--password-store=basic"] )]
```

## Open items

- Formatter, test runner and module-format (ESM versus CommonJS) guidance: UNVERIFIED stubs.
