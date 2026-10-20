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

> **Learned 2026-10-20 (b)** · any parser of captured device output · VERIFIED_PRIMARY · Source: unified-network-controller
> `tests/test_mikrotik_ata_onboarding.py` `test_real_s11_page_classifies_within_the_probe_read` (commit 075d6b9) · Falsifier: a page whose marker
> sits inside the made-up sample's length and also inside the production cut
> Test a matcher on a real captured sample, cut where production cuts it, not on a short made-up string: a vendor-marker test passed on a
> one-line sample while the real 24.9 KB page carried the marker at byte 24,545, past the 4 KB the probe kept, so the unit was missed in the field.
> Keep the real sample as a fixture (with a readme saying it holds no secrets) and assert the old behaviour failed on it too.
>
> ```python
> page = (ROOT / "tests" / "fixtures" / "ddc-voip" / "s11-home-page.txt").read_text(encoding="utf-8")
> for cut in (PAGE_BYTES, 4096):                                   # the production cut, and the old one
>     cands = {"192.168.5.253": {"vendor": "other"}}
>     classify_by_page(cands, {"192.168.5.253": page[:cut]}, vendor_markers())
>     self.assertEqual(cands["192.168.5.253"].get("family"), "ddc-voip", cut)
> ```

## Proof against the real target

- Before claiming a capability works, verify it against a real target (an isolated or spare one), not only a mock. Why: a stub only proves the code agrees with
  the stub.
- Report success at the outcome the operator sees (stored, visible, healthy), not at "the call returned 200" ([safety-and-writes.md](safety-and-writes.md)).
- A single success is a candidate, not a rule, until a second environment, the official docs or the source agrees ([evolution-and-write-back.md](evolution-and-write-back.md)).
