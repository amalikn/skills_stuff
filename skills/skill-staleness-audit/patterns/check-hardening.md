# Check hardening

<!-- claim-scan:examples reason="names filenames as examples of a class, not as references" -->

Phase 5: turning each finding into something that cannot recur. A fix that is not enforced is a fix until the next session.

## Contents

- [The six rules](#the-six-rules)
- [Negative testing is the whole discipline](#negative-testing-is-the-whole-discipline)
- [Derive, never author](#derive-never-author)
- [Scan everything, not a hand-listed few](#scan-everything-not-a-hand-listed-few)
- [Guard every phrasing, not the one you wrote](#guard-every-phrasing-not-the-one-you-wrote)
- [Assert on the property that silence hides](#assert-on-the-property-that-silence-hides)
- [Exempt history by marker, never by rewriting](#exempt-history-by-marker-never-by-rewriting)
- [When not to write a check](#when-not-to-write-a-check)

---

## The six rules

1. **Derive, never author.** A claim about the project should be computed from the thing it describes.
2. **Negative-test in both directions.** Prove it goes red on a real defect *and* green when the defect is removed.
3. **Scan everything, not a hand-listed few.** A hand-maintained registry drifts exactly like the claims it polices.
4. **Guard every phrasing and word order**, not the one you happened to write.
5. **Assert on the property that silence hides** — byte-equality, duplicate keys, provenance, "was this ever surfaced".
6. **Exempt history by marker, never by rewriting it.**

## Negative testing is the whole discipline

**A check that never fires breaks nothing and passes forever.** It is indistinguishable from a working check until the day it was supposed to catch something.

This is not hypothetical. In the originating run, a divergence warning was added to a scenario runner, wired in, and the suite passed. It read cell `B70`. The value it needed was in `B71`. The warning
therefore **never fired**, and nothing anywhere reported a problem — because a warning that does not trigger produces no output and breaks no test. It was caught only by deliberately running a preset
that *should* have triggered it and noticing silence.

The protocol, every time:

```bash
# 1. Prove it can go RED — introduce the exact defect the check exists for
cp target.file /tmp/bak
printf '\n<the defect>\n' >> target.file
just check 2>&1 | grep "<expected message>"      # MUST appear

# 2. Prove it goes GREEN again
cp /tmp/bak target.file && rm /tmp/bak
just check 2>&1 | tail -3                        # MUST pass
```

For a check with a threshold or a conditional, test **both sides of the boundary** — one case that must warn and one that must not. A guard that fires on everything is as useless as one that fires on
nothing, and only bidirectional testing separates them.

Record in the change log that the check was negative-tested. An untested check is a claim, and this skill exists because of claims nobody checked.

## Derive, never author

The failure: a project asserted **three different values** for the same check count — 39 in the script's own docstring and the task runner, 57 across six other files, while the two lists actually
totalled 56.

The fix is not to correct the three numbers. It is to make the number **underivable by hand**:

```python
total = 0
for name in ("UNREG", "REG"):
    m = re.search(rf"^{name} = \[(.*?)^\]", src, re.S | re.M)
    total += len(re.findall(r"\(\s*\"B", m.group(1)))
# then fail any surface stating a different figure
```

Now adding a check updates the truth automatically and the build tells you which prose to fix. Applies equally to file counts, row counts, "supports N of X", inventory sizes, and any self-description.

## Scan everything, not a hand-listed few

The count check above was first written scanning **four hand-listed files**. It passed clean. A repo-wide grep immediately found **five more surfaces it had never looked at**, including two rule
documents and a decision register.

**A registry maintained by hand has precisely the drift problem it was written to detect.** Prefer a repo-wide scan with explicit, reasoned exemptions:

```python
skip = ("docs/archive/", "trackers/", ".ai-context/", "CHANGELOG.md")   # audit trail, by design
for path in ROOT.rglob("*"):
    if path.suffix not in {".md", ".py", ".yaml"}: continue
    ...
```

Each exemption needs a reason in a comment. "Archives are *supposed* to contain superseded figures" is a reason; "this file was noisy" is not.

**Also check the inverse.** *Catalog names something that vanished* and *something exists that no catalog names* are different defects, and only the second grows silently. Generate both directions.

## Guard every phrasing, not the one you wrote

A guard matching one phrasing reports clean while the defect sits in the filed document.

The instance: a phrase guard for a superseded threshold matched `profit gate $2,500` — words before the amount. A script wrote `≥$2,500 profit gate` — amount first. No match, no failure, superseded
gate printed into a licence-application working paper through 592 passing checks.

Widening it to the reversed order **immediately surfaced two more unregistered surfaces**, one of which had additionally been stating the gates as a half-set.

When adding a phrasing:

- Both word orders — *value then label*, and *label then value*.
- Formatting between them — markdown emphasis (`**≥ $2,500**`), backticks, line breaks.
- Synonyms the project actually uses — `gate`, `floor`, `threshold`, `limit`, `minimum`.

**A half-set is worse than no restatement**, because a reader has no way to tell the list is partial. Guard for partial statements too, not only wrong ones.

## Assert on the property that silence hides

The highest-value checks assert things no amount of internal agreement can reveal:

| Property | Check | Why nothing else catches it |
|---|---|---|
| Evidence unchanged | Byte-equality with the committed version | A formatter preserves words, links and line counts |
| Config means what it looks like | Strict loader rejecting duplicate keys | The file parses; the parser silently keeps the last |
| Input was verified | A provenance label is present | Arithmetic on an unchecked number is still valid arithmetic |
| A label is actually seen | The runner **prints** it | A label nothing surfaces is inert |
| A generated file is current | Regenerate and diff | The output can be right while the generator is wrong |

The fourth is easy to miss and was a real finding: provenance labels had been added to every input and **no code path ever read them**, so a stated mechanism — "a run cannot present the figure as
settled" — was entirely inert. The label existed and was invisible at the exact moment someone read the result.

## Exempt history by marker, never by rewriting

A dated record of what was true then is **evidence**. Rewriting it so a linter passes destroys the record and is the failure the exemption exists for.

```markdown
- [x] 2026-08-09 — Economics workbook v1; 22/22 formula checks <!-- count:asat -->
```

The marker says: *this is a historical claim, do not enforce it*. The check honours it; the record survives; the live claims elsewhere are still enforced.

Distinguish carefully:

- **"The contract is 39 formula checks"** — a live claim. Fix it.
- **"2026-08-09 — 22/22 checks"** — a dated record. Mark it.

## When not to write a check

- **The invariant is not something the project has stated.** Manufacturing governance the operator never agreed to is worse than leaving a gap. Propose it instead, in the residual-risk register.
- **The check would need to be right about the world**, not about the repo. A check cannot verify that a market price is correct — only that a provenance label exists. Be honest about that limit in
  the check's own docstring.
- **It cannot be made to fail.** If you cannot construct the failing case, you do not yet understand the defect well enough to enforce against it.

Every check should carry, in its docstring, **the specific defect it was written for** — with the date and the real instance. A check whose justification cannot be located is one the next agent
deletes when it becomes inconvenient.
