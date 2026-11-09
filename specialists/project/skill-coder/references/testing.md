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

> **Learned 2026-11-06** · testing, measurements in a lab · VERIFIED_PRIMARY · Source: apn smc-resiliency S3 report finding S3-6
> (`spike/vm/s3/shape_link.sh`, docs/pi/pi-spike-s3-delivery-20261106_1044.md) · Falsifier: a lab where the unshaped baseline and the
> one-element steps agree with theory but a shaped result is still wrong
> **Prove the instrument before trusting what it measures.** A lab that imitated a satellite link (delay, rate, loss with tc netem) gave
> plausible slow downloads; three runs were explained by loss, then by HTTP/1.1, before a step test showed the lab itself was broken: 0.9 MB/s
> unshaped between two VMs and 3 KB/s with delay alone (segmentation offloads building frames the virtual network dropped). All three runs were
> void. Before any measured run: (1) run the unshaped baseline and compare it with what the hardware should give; (2) add one element at a
> time (delay, then rate, then loss) and check each against theory (a 1 MiB fetch at 700 ms takes a few round trips, not minutes); (3) only then
> measure the thing under test, and record the instrument's own fixes beside the results.

> **Learned 2026-11-06 (b)** · timed cases with an injected fault · VERIFIED_PRIMARY · Source: apn smc-resiliency `spike/vm/s3/s3_case.sh`
> and `shape_link.sh` (verify mode), technical audit F10, 2026-11-06 · Falsifier: a driver that times a case on an unverified link, or counts a
> fault that fired after the work ended, and is still right
> **A result counts only when its setup is read back and its fault overlapped the work.** Read the applied set-up back on every end before
> timing (here: qdisc rate, delay and loss, MTU, offloads, no leftover cut table); record when the fault fired against the work's own start and
> end, cancel a fault still waiting when the work ends, and mark the case INVALID instead of logging a valid-looking line. It fired the same
> day: a power cut scheduled at 120 s met an install that ended at 25 s, and the line said INVALID instead of "survived a power cut".
>
> ```bash
> # smc-resiliency spike/vm/s3/s3_case.sh (2026-11-06)
> if ! V=$(verify_link "$P"); then echo "... INVALID instrument: $V" | tee -a "$LOG"; shape off; exit 3; fi
> (sleep "$KILL_AT"; date +%s > "$FIRED"; prlctl stop "$BOX" --kill) & WPID=$!
> T0=$(date +%s); OUTTXT=$(on "$BOX" 7200 "$RUN ..."); RC=$?; T1=$(date +%s)
> if [ -s "$FIRED" ] && [ "$(cat "$FIRED")" -lt "$T1" ]; then OVERLAP=" fault_at=$(( $(cat "$FIRED") - T0 ))s"
> else kill "$WPID" 2>/dev/null; OVERLAP=" INVALID: install ended before the fault fired"; fi
> ```

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

> **Learned 2026-11-01** · any flag derived from a state · VERIFIED_PRIMARY · Source: skill-knowledge-curator `scripts/knowledge_curator_lib/query.py` at `f819ff3` · Falsifier: a shared predicate that stays right for two callers asking different questions
> A predicate written for one question silently answers another. `settled` reused the publishing test, so a disputed P2 claim read as settled while 42 tests passed: the fixture's conflicts were all P1. Name the question each caller asks, and test the case where the answers differ.

```python
# query.py at f819ff3: effective() asks "may this be published", settled asks "is this disputed"
open_conflicts = st.open_conflicts(cid)
"settled": disp == "CURRENT" and not open_conflicts,
```

> **Learned 2026-11-01 (b)** · a gate that hides records · VERIFIED_PRIMARY · Source: skill-knowledge-curator `scripts/knowledge_curator_lib/triage.py` at `8113528` · Falsifier: a broad gate that cleared no real record in a dry run against known verdicts
> A gate that hides records needs a guard that runs first and a dry run against known verdicts before any `--apply`. The first gates passed their unit tests and cleared 7 of 11 real conflicts, because the guard matched exact paths while the real cases named a child of the path.

```python
# triage.py at 8113528: the guard runs before every gate, and P0 before the guard
if cf["severity"] == "P0":
  return row | {"guard": "p0"}
if _opposite_status(ca, cb):
  return row | {"guard": "same-identifier-opposite-status"}
```

> **Learned 2026-11-02** · closing checks · VERIFIED_PRIMARY · Source: skill-drawio `just check` passed with two erroring unit tests, 2026-11-02 · Falsifier: a project whose `check` recipe runs its tests
> A closing check that does not run the unit tests lets a broken test through a green gate. Know what `check` covers, and run the tests in the same gate before a push.

> **Learned 2026-11-02** · applying reviews · VERIFIED_PRIMARY · Source: 105 agent fixes applied by script to a flow map, one a reviewer's to-do note · Falsifier: text applied by script that cannot hold an instruction
> Review text applied by script lands wherever it was written, instructions included, and a stamp over it claims a review nobody did. Split the fact from the advice in the review's format, scan what was applied, and record who reviewed.

> **Learned 2026-11-08** · core (a test that injects a fault) · VERIFIED_PRIMARY · Source: smc-resiliency `lab/logic/e2e.py` `link`, commit d1a7d894 · Falsifier: a fault-injection step whose effect is read back and still passes a case it never ran
> A case that cuts a link, kills a process or fills a disk passes for the wrong reason when the injection fails quietly: on 2026-11-07 the cut's
> ssh timed out, the code ignored its exit, and the "held while the uplink is down" case judged a link that was never cut. Read the injected state
> back and stop the case when it is not what was asked; retry only the transport's own failure (ssh exit 255), never a wrong state:
>
> ```python
> for _ in range(3):  # ssh's own failure (255) is retried; a wrong state is not
>   rc, out = t.client.run(f"ip link set {t.client_if} {want} && ip -br link show {t.client_if}", root=True, timeout=60)
>   if rc != 255:
>     break
>   time.sleep(5)
> state = out.split()[1] if rc == 0 and len(out.split()) > 1 else ""
> if rc or (state == "UP") != up:
>   raise LabError(f"{t.name}: client {t.client_if} not {want} (rc {rc}: {out.strip()[:120]})")
> ```

> **Learned 2026-11-08 (b)** · Python, a test of bytes on the wire · VERIFIED_PRIMARY · Source: smc-resiliency `lab/tests/test_lab.py` ConsoleTests, commit 60ce8b3a · Falsifier: `Path.read_text()` returning `\r\n` unchanged
> `Path.read_text()` opens in universal-newline mode and turns `\r\n` into `\n`, so a test that a recorder dropped carriage returns passed with the
> strip removed (the mutation stayed green). Read bytes (`read_bytes().decode()`) when the test is about line endings. A pseudo-terminal used as a
> serial stand-in must be raw (`tty.setraw`) before the far end writes, or its line discipline turns `\r` into `\n` itself. A serial port needs no
> pyserial: `os.open` plus `termios` (raw, CS8, CREAD, CLOCAL, the speed constant) and `select` read it.

> **Learned 2026-11-09** · core (a check that matches a token in prose) · VERIFIED_PRIMARY · Source: skill-proxmox `scripts/check_governance.py` `check_version_restated` and `tests/test_helpers.py` `test_a_restated_version_fails_the_gate`, uncommitted on 2026-11-09 · Falsifier: a lookahead of `(?![\d.])` that still matches a version at the end of a sentence
> A token boundary written as "not followed by a digit or a dot" misses every token that ends a sentence ("release 0.1.0."), so the check
> passed on the text it existed to catch. The fail-proof test, written as natural prose rather than a bare token, went red and found it. Reject
> only what extends the token (a digit, or a dot followed by a digit), and write the negative test in the form the defect takes in real files.
> ```python
> token = re.compile(rf"(?<![\d.]){re.escape(version)}(?!\.?\d)")  # was (?![\d.]): missed "0.1.0."
> fh.write(f"\nCurrent release: {version}.\n")                      # the test line that exposed it
> ```

> **Learned 2026-11-08** · test oracles (fault-injection runners) · VERIFIED_PRIMARY · Source: unified-network-controller audit follow-up `docs/reports/project-reviews/unc-technical-audit-followup-20261108_1255.md` (offline fake-target probes), code at e873366b, `unc-simulation-lab/engine/run.py:50-55,103-115` · Falsifier: a tool
> failure or a failed cleanup cannot produce a passing acceptance result.
> A negative assertion ("the service is unreachable") needs a probe that provably ran: a nonzero exit from the tool itself (daemon down, missing
> binary, permission denied) is not the expected outage, it is inconclusive. Cleanup and fault readback are part of the verdict: record each
> fault's readback and each cleanup's receipt, and a failed or uncertain cleanup invalidates the run.
>
> ```python
> # Anti-pattern, sanitized excerpt (run.py at e873366b): any nonzero rc reads as "unreachable".
> reachable = r.returncode == 0
> return {"passed": reachable == expected}
> ```

> **Learned 2026-11-09 (b)** · test oracles (a case judged by its end state) · VERIFIED_PRIMARY · Source: smc-resiliency `lab/logic/x2cases.py` `cause` and `commit_gate`, commit f923adbe · Falsifier: an end state no other cause can produce
> "Ended on slot A" passed the panic, hang and power-cut cases, but firmware refusing slot B ends there too, so a pass proved nothing about the
> fault. Each case must show its own cause from the system's record (the fault marker the failing slot wrote, the armed watchdog, the driver's
> reset, the slot that answered before the cut); missing evidence is inconclusive, not a pass. A commit step gated on `|| true` cannot refuse a
> degraded trial: judge health against the baseline taken before the change. Re-judge old passes from their raw records; never rewrite them.
>
> ```python
> if case.variant == "hang-watchdog":
>   if "smc-x2: hang" not in log: return "no hang marker from B (smc-x2-fault never ran)"
>   if "state active" not in log: return "the hardware watchdog was not armed when B hung"
> if case.variant == "hang-noinit" and not trial.get("driver_reset"):
>   return "back on A without the driver's reset: the hang the case needs never happened"
> ```

> **Learned 2026-11-09 (c)** · shell (testing a function in a script that is uploaded alone) · VERIFIED_PRIMARY · Source: smc-resiliency `spike/tests/test_tool_digests.py` `function`, commit f923adbe · Falsifier: a sourced script that runs nothing at load
> A payload copied to a box as one file cannot source a shared library, and sourcing the payload runs it. Test its check function by cutting the
> function out of the file (from `name() {` to the `}` at column 0) and running it under bash against temporary files: the test executes the
> real code, not a copy. A fake on PATH for a wrapper that quotes with `printf %q` sees backslash-escaped spaces: strip them (`${4//\\/}`) before
> matching, or every pattern misses and the run looks like an instrument failure.
>
> ```python
> m = re.search(rf"^{name}\(\) \{{\n.*?^\}}\n", script.read_text(encoding="utf-8"), re.S | re.M)
> rc = run_group(["bash", "-c", f'{m.group(0)}\nrauc_tarball "{tb}" {good}'], dict(os.environ), 30)[0]
> ```

> **Learned 2026-11-09** · tests that prove a file was rewritten in place · VERIFIED_PRIMARY (smc-resiliency S1V on vfat: inode 11 before a
> reboot, 3 after, same file) · Source: smc-resiliency docs/overview/smc-lab-test-record-20261107_1931.md section 18 · Falsifier: vfat keeping
> inode numbers across mounts. FAT has no inodes; Linux makes them up at mount, so an inode compared across a reboot proves nothing. Compare
> size and inode before and after one write within one boot.

> **Learned 2026-11-10** · tests of a safety guard built on an external tool's output · VERIFIED_PRIMARY (smc-resiliency lab/logic/flash.py:
> fakes with guessed diskutil keys passed; a plan-only run against a real 988 GB APFS USB drive was not refused) · Source: smc-resiliency
> lab/tests/test_lab.py FlashTargetTests · Falsifier: a guard whose fakes were copied from real output missing the same case. Build the fake from
> the tool's real output for the case that must be refused, and smoke the refusal against a real wrong target in plan mode before trusting it.

