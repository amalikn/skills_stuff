---
Title: Testing
Category: reference
Status: current
Authority: local-supplement
Scope: What to test, at which level, and how to make tests and checks trustworthy
Last reviewed: 2026-10-19
Summary: >-
  Test first for bugs, characterisation before refactoring, a negative test proving each check can fail, fakes per
  contract with a shared contract suite, deterministic output, drift checks for generated files, and real-target proof.
---

# Testing

## Contents

- [Levels](#levels)
- [Rules](#rules)
- [Checks that can fail](#checks-that-can-fail)
- [Proof against the real target](#proof-against-the-real-target)

## Levels

| Layer | Test kind | Why |
| --- | --- | --- |
| Core, pure policy, data | Unit tests, no network, no fixtures beyond values | Fast and exact; most tests live here (the test pyramid, VERIFIED_SECONDARY, Fowler) |
| Drivers and parsers | Fixture tests on recorded real output | The parser is checked against what the target really says |
| Services | Tests on fakes of each contract | Use cases test without outside systems |
| Seams to outside systems | A shared contract suite every implementation (real and fake) passes | The fake cannot drift from the real thing |
| Whole program | A few end-to-end or smoke runs, read-only | Wiring is checked without a broad slow suite |

## Rules

- **Test first for a bug.** Write a test that fails on the bug, then fix it, then watch it pass. Why: a fix without a failing test may not fix the bug.
- **Characterise before refactoring.** Before changing the structure of code that has no tests, capture its current output for representative inputs (a
  characterisation test, Michael Feathers' term) and compare after. Why: refactoring by definition changes no observable behaviour, so the comparison must be
  byte-identical ([refactoring-and-promotion.md](refactoring-and-promotion.md)).
- **Every contract has a fake.** A project checks that each interface has one and that each implementation passes the shared suite. Why: a fake without the
  suite is a guess.
- **Deterministic output.** Sort what the program emits, fix seeds, inject the clock, and avoid environment-dependent paths in output. Why: a diff is only
  useful when the same input gives the same bytes.
- **Offline by default.** Tests do not reach the network or production. Write paths are tested offline with recorded responses and live only on a
  disposable instance. Why: a test run must be safe to repeat anywhere.
- **Name tests for the behaviour** they pin, and keep one behaviour per test. Why: a failing name should say what broke.
- **Run the project's test command, not an ad-hoc one** (`just test`, `make test`, `npm test`); gate on its exit code. Why: the project's command sets the paths
  and interpreter the code needs.

## Checks that can fail

A governance check, lint rule or validator lands with a negative test that turns it red on a crafted bad input. Why: a check that cannot fail is not coverage
(skill-ai-it governance-check doctrine). When a check starts in warn mode, its count is held by a shrink-only baseline and switches to fail mode at a named
milestone.

> **Learned 2026-10-20** · any project · VERIFIED_PRIMARY · Source: unified-network-controller `tests/test_topology_preview_scripts.py`, `wc-local/scripts/nautobot_tools/app_verify.py` (both fixed 2026-10-20) · Falsifier: a mirror tool kept in step with its source for months with no test tying them
> A helper that mirrors product inputs (a preview page that loads the page's scripts, a verifier that builds the product's image) drifts silently
> when the product changes, and a stale mirror passes its own checks while proving nothing: one preview loaded two of a template's five scripts
> and drew an empty canvas, one verifier built from a context the Dockerfile no longer used. Keep the mirrored list as a named constant and test it
> against the source it copies (the template's script tags, the Dockerfile's context), and prove that test fails on the old list.
>
> Excerpt (unified-network-controller `tests/test_topology_preview_scripts.py`, commit 15159f3):
>
> ```python
> drawing = block.split("{% else %}")[1].split("{% endif %}")[0]          # the template's drawing branch
> keys = re.findall(r"assets\.(\w+)", block.split("{% if map_data %}")[0]) + re.findall(r"assets\.(\w+)", drawing)
> self.assertEqual(tuple(asset_to_file[key_to_asset[k]] for k in keys), SCRIPTS)   # the preview's own constant
> ```

> **Learned 2026-10-20 (b)** · any parser of captured device output · VERIFIED_PRIMARY · Source: unified-network-controller `tests/test_mikrotik_ata_onboarding.py` `test_real_s11_page_classifies_within_the_probe_read` (commit 075d6b9) · Falsifier: a page whose marker
> sits inside the made-up sample's length and also inside the production cut
> Test a matcher on a real captured sample, cut where production cuts it, not on a short made-up string: a vendor-marker test passed on a
> one-line sample while the real 24.9 KB page carried the marker at byte 24,545, past the 4 KB the probe kept, so the unit was missed in the field.
> Keep the real sample as a fixture (with a readme saying it holds no secrets) and assert the old behaviour failed on it too.
>
> ```python
> page = (ROOT / "tests" / "fixtures" / "ddc-voip" / "s11-home-page.txt").read_text(encoding="utf-8")
> for cut in (PAGE_BYTES, 4096):                                   # the production cut, and the old one
>     cands = {"192.0.2.53": {"vendor": "other"}}
>     classify_by_page(cands, {"192.0.2.53": page[:cut]}, vendor_markers())
>     self.assertEqual(cands["192.0.2.53"].get("family"), "ddc-voip", cut)
> ```

> **Learned 2026-10-20** · core (negative tests for a script's guards) · VERIFIED_PRIMARY · Source: smc-resiliency justfile `_script-guards` and scripts/confext_probe.sh (apn, 2026-10-20) · Falsifier: a script whose guards exit with distinct codes, where the exit code alone tells them apart
> A guard test that asserts only the exit code can pass for the wrong guard: a probe refusing "not the named lab host" and "not root" both exit 2,
> so a copy with the host check removed still exited 2 on a non-root machine and the proof was void. Assert the guard's own message (or give each
> guard its own code), then prove red on a copy with that one guard removed.
>
> ```bash
> out=$(bash "${PROBE:-scripts/confext_probe.sh}" --lab-host "not-$(hostname)" --apply 2>&1); rc=$?
> { [ $rc -eq 2 ] && [[ "$out" == *"refusing: this box is"* ]]; } || { echo "guard: did not refuse a box it was not named for (rc $rc)"; fail=1; }
> ```

> **Learned 2026-10-29** · core (a check whose tool may be missing) · VERIFIED_PRIMARY · Source: unified-network-controller `scripts/githooks/pre-commit` (fixed in 36e88ef) · Falsifier: a hook that reports a missing tool and still passed silently.
> A check guarded by "skip when the tool is not there" is a pass that cannot fail: when a dependency moved its scripts, the pre-commit hook's
> target-map check skipped for two days with no output, while its doc-freshness call failed loudly. Report a missing tool as a failure (or at
> least a warning line); skip silently only for a tool that is optional by design, and say which.
>
> ```bash
> # before: a moved script turns the check off without a word
> tm=.../skill-ai-it/scripts/target_map.py
> [ -f "$dir/target-map.yaml" ] && [ -f "$tm" ] || continue
> ```

> **Learned 2026-10-29 (b)** · core (access-control and enforcement tests) · VERIFIED_SECONDARY (harvest 2026-10-29 of unified-network-controller) · Source: unified-network-controller `docs/field-ownership/field-ownership-model-20260923_1336.md` section 9 · Falsifier: an enforcement test that passes for the right reason while the acting identity or the refusing layer is never asserted
> A test of a guard must prove which mechanism allowed or refused the action, not only the outcome. Two near-false results in one project: a
> token minted through an API that ignored its `user` field was really an administrator's, so a successful write looked like broken
> enforcement; a real low-privilege token was refused by object permissions before the validator under test ever ran. Mint the identity the
> way production does, assert the acting identity in the audit trail, and grant every other permission so that only the mechanism under
> test can produce the refusal (here: the validator's 400, never a 403).

> **Learned 2026-10-29 (c)** · core (regressions from real incidents) · VERIFIED_SECONDARY (harvest 2026-10-29 of a personal research project) · Source: project_stuff/me vehicle-import track `scripts/verify_regressions.py` · Falsifier: an incident regression that keeps
> passing after the tool starts emitting the withheld figure again
> Turn each real failure into a permanent regression that asserts the behaviour that prevents it: what the tool withholds (no verdict from a
> single record, no output figure from an unchecked outlier), not an exit code or a message string. A refusal is the feature; text and exit
> codes are incidental and change without the refusal changing.

> **Learned 2026-10-29 (d)** · core (architectural invariants as tests) · VERIFIED_SECONDARY (harvest 2026-10-29 of a personal decision-support project) · Source: project_stuff/me decision-support project `tests/test_no_llm.py` · Falsifier: an indirect import
> of a forbidden client that the static scan misses and the clean-interpreter import also misses
> A layer claim such as "this engine never calls a model or the network" is only worth something when a test enforces it three ways:
> every import in the package resolves to the standard library or the package itself (AST scan); no source file names a forbidden vendor
> or client; importing the package in an isolated interpreter (`python -I -c "import pkg, sys; print(sorted(sys.modules))"`) loads no
> client module, which catches indirect imports the scan cannot see. A negative control (a planted forbidden import) proves the test can
> go red. `scripts/import_layers.py` covers the static half; the runtime half needs the clean interpreter.

> **Learned 2026-10-29 (e)** · core (verifiers over fetched or derived data) · VERIFIED_SECONDARY (harvest 2026-10-29 of a personal corpus project) · Source: project_stuff/me corpus project `scripts/verify_*.py`, `scripts/corpus_pins.py` · Falsifier: a baseline edited
> without a matching provenance change that the verifier still accepts
> Pin the expected state (counts, hashes, directory set) in the verifier and exit non-zero on any divergence; a refresh that silently
> restored purged material was caught this way. Bake the fetch filter into the recipe so a refresh cannot widen the set, and change a
> baseline only in the same change that updates its provenance record, so the pin and the reason for it move together.

> **Learned 2026-10-29 (f)** · core (analysis over exported files) · VERIFIED_SECONDARY (harvest 2026-10-29 of equinix-cost-cutting) · Source: equinix-cost-cutting `docs/invoices/readme.md:88-94`, `CHANGELOG.md:173` · Falsifier: an analysis whose first figure survives
> a reconciliation against an independent asset list with no profiling step
> Profile every source file before analysing it: its true format (files named `.xls` were MIME-HTML report exports), what one row means,
> units and tax basis. A first report's headline count was a row count, not an asset count, and was later replaced by a figure eight times
> smaller. Normalise raw exports into one table with row counts and hashes per input, and reconcile any count of things against an
> independent list before writing a conclusion.

> **Learned 2026-11-01** · gates added to a task runner · VERIFIED_PRIMARY · Source: `tools_stuff/continuum/justfile` recipe `check` · Falsifier: a recipe that discards stdout and still shows why it failed
> A new gate wired into a recipe with `>/dev/null` fails with no reason on screen, and the negative test's expected text can never match. Keep the check's own output in the recipe, or print the
> failure to stderr; prove it by running the recipe red and matching the failure text, not the exit code alone.

```just
# continuum/justfile: the gate stays verbose so a red run names what failed
check: _require-venv
    @{{py}} scripts/check_governance.py
    @{{py}} -I scripts/render_claim_registers.py --check
    @{{py}} -I scripts/check_architecture_coverage.py
```

## Proof against the real target

- Before claiming a capability works, verify it against a real target (an isolated or spare one), not only a mock. Why: a stub only proves the code agrees with
  the stub.
- Report success at the outcome the operator sees (stored, visible, healthy), not at "the call returned 200" ([safety-and-writes.md](safety-and-writes.md)).
- A single success is a candidate, not a rule, until a second environment, the official docs or the source agrees ([evolution-and-write-back.md](evolution-and-write-back.md)).

> **Learned 2026-10-20 (b)** · core (helpers and checks over a project) · VERIFIED_PRIMARY · Source: smc-resiliency code-map.toml `roots` and scripts/govcheck/checks/scripts.py `check_code_map` (apn e764a3e) · Falsifier: a helper that lists the files it scanned and still missed a new folder
> A helper's "OK" says nothing about code it never read: `script_headers`, `write_gates` and `call_timeouts` passed on a new `spike/` folder because
> `code-map.toml` set `roots = ["scripts"]`, and the project's code-map check globbed `scripts/` only. Run the helper with `--list` and confirm the new
> files appear; widen the roots (or the check) in the same change that adds a code folder; then the real gaps showed (a test header, two unmapped tests).

> **Learned 2026-10-21** · core (proving a formatter changed layout only) · VERIFIED_PRIMARY · Source: scripts_stuff `python/markdown_rewrap/table_cells_diff.py` and `test_table_cells_diff.py` (uncommitted, pending operator review) · Falsifier: a re-wrapped
> table whose text really moved between columns while the canonical comparison still passes
> To prove a reformatter moved no content, compare the structure it formats, not a flattened diff: rebuild each logical unit (a table row with its
> continuation rows), join each column's fragments, undo the formatter's own artefacts, then compare cell by cell. Give the checker a negative test
> (a word moved to the next column must be reported) or a pass proves nothing. Run it against the old tool's output, the new tool's output and the source.
>
> ```python
> if current and len(current) > 1 and is_continuation(raw):        # fold a continuation row into its logical row
>     for i, cell in enumerate(raw):
>         if i < len(current[-1]) and cell.strip():
>             current[-1][i].append(cell.strip())
> ...
> moved = "| Path | Role |\n| --- | --- |\n| `docs/a/b-long-name.md` first | second third |\n"
> self.assertEqual(len(tcd.differences(ONE_LINE, moved)), 2)     # the negative test
> ```

> **Learned 2026-10-26** · core (test through the entry point the user triggers) · VERIFIED_PRIMARY · Source: skill-drawio `scripts/flowmap/isolate.py` (commit af7bc38) and `scripts/viewer_click.py`; draw.io 32.5.5 `Graph.handleCustomLink` and `executeCustomActions` · Falsifier: a host whose default does not depend on how an action is invoked
> A host can choose a default by call path. draw.io runs a link's actions as unsaved display changes when called without a cell, and as
> saved model changes when a real click passes the clicked cell. A test that invoked the link directly passed (toggled, nothing saved)
> while a real click saved to the file and never toggled back. Drive the host through the same path a user's action takes (here its click
> handler with the cell), state every default the code depends on explicitly (`"transient": true` on each action), and keep an offline
> model test of the logic that asserts the explicit setting, so the unit test fails if it is dropped.
>
> ```python
> # skill-drawio scripts/viewer_click.py: a click through draw.io's own path, the clicked cell given
> LINK_JS = """id => { var c = V.graph.model.getCell(id), l = c && V.graph.getLinkForCell(c); if (!l) return false;
>     V.graph.customLinkClicked(l, c); return true; }"""
> # skill-drawio tests/test_e2e_family.py ClickIsolate._run
> self.assertIs(sel.get("transient"), True)   # never a saved change: a click on a cell defaults to one in draw.io
> ```
