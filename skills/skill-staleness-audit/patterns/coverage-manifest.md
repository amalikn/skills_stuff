# Coverage manifest

<!-- claim-scan:examples reason="names filenames as examples of a class, not as references" -->

The contract that makes the audit **exhaustive rather than opportunistic**: every file in scope is classified, and nothing is left unexamined by accident.

## Contents

- [The rule](#the-rule)
- [Coverage accounting](#coverage-accounting)
- [File classes](#file-classes)
- [Binary and tabular data](#binary-and-tabular-data)
- [Generated context](#generated-context)
- [Legitimate exemptions](#legitimate-exemptions)
- [Worked accounting](#worked-accounting)

---

## The rule

**Every file under the audit root lands in exactly one of three states**, and the count of all three must equal the total file count:

1. **Examined** — inspected, with a verdict.
2. **Exempt, with a stated reason** — archives, evidence, vendored code, generated output.
3. **Out of scope, stated** — the operator scoped the run to a subtree.

There is no fourth state. "I did not get to it" is not a state; it is state 3 with an honest label.

The failure this prevents is specific and common: a sweep that greps `*.md` and `*.py`, reports clean, and never touched the `.parquet` holding the query layer, the `.xlsx` that is the actual model,
or the `.json` presets that every tool reads. **The most decision-relevant files in a project are often the ones a text sweep cannot open.**

## Coverage accounting

Produce this before Phase 2 and include it in the final report:

```text
Total files in scope:            412
  Examined:                      118
  Exempt (reason stated):        291
  Out of scope (stated):           3
                                ----
                                 412   ✓ reconciles
```

If it does not reconcile, the audit does not yet know what it looked at. Fix that before fixing anything else.

```bash
# Inventory by extension — the starting point, not the answer
git ls-files | sed 's/.*\.//' | sort | uniq -c | sort -rn
find . -type f -not -path './.git/*' | wc -l
```

## File classes

Each class, what staleness means for it, and how to detect it.

| Class | Typical files | What staleness looks like | Detection |
|---|---|---|---|
| **Agent governance** | `AGENTS.md`, `CLAUDE.md`, `.cursor/rules` | Rules citing moved paths; stale counts; layout sections omitting new directories; "last reviewed" | Read fully. Verify every path and count against disk |
| **Routing / navigation** | `AI_NAVIGATION.md`, `context-map.yaml`, docs index | Routing rows pointing at superseded owners; supersession lists missing recent chains; **structurally valid but semantically wrong keys** | Read fully. **Parse YAML/JSON and inspect the structure**, not the text |
| **Durable decisions** | `.archcore/`, ADRs, RFCs | Accepted claims later contradicted; figures historical by design but read as live | Read fully. Mark in place; never rewrite an accepted claim |
| **Knowledge base** | `docs/NN-*.md` | The core supersession problem — old documents reading as current | Read fully. Banner per `supersession-banners.md` |
| **Process / runbooks** | `process/`, playbooks, SOPs | Steps naming decommissioned things; costs stated as literals instead of referencing the model | Read fully. Follow the steps mentally against current reality |
| **Code / scripts** | `*.py`, `*.sh`, `*.ts` | Stale assumptions in output shape — see `per-artifact-reasoning.md` | **One line of reasoning each.** Not discharged by grep |
| **Task runners** | `justfile`, `Makefile`, `Taskfile.yml` | Recipes referencing removed scripts; comments stating stale counts; descriptions that no longer match behaviour | Read fully. Cross-check every recipe against the script catalog, both directions |
| **Structured config** | `*.yaml`, `*.json`, `*.toml` | Duplicate keys silently discarding blocks; presets carrying disproven values; misplaced keys | **Parse with a strict loader.** Compare parsed structure to intent |
| **Tabular data** | `*.csv`, `*.parquet`, `*.xlsx` | Derived from a superseded source; schema drift; stale despite a fresh mtime | See below — **cannot be grepped** |
| **Generated context** | `.ai-context/`, repomix output, graph exports | Stale **by definition** between rebuilds | Do not audit contents. **Regenerate and confirm** |
| **Evidence / captures** | `trackers/`, `source-captures/`, fixtures | Silently reformatted; no longer byte-faithful | **Byte-compare against committed.** Never edit |
| **Correspondence** | Emails, letters, replies | Superseded by a later reply; commitments no longer accurate | Read. Never edit inbound records |
| **Dependency locks** | `package-lock.json`, `uv.lock` | Drift from the manifest; versions stated in prose | Compare lock to manifest and to any prose claim |
| **Archives** | `docs/archive/`, `*.bak`, snapshots | **Supposed to be stale** | Exempt, stated |
| **Vendored / third-party** | `node_modules/`, vendored libs | Not yours | Exempt, stated |
| **Secrets / env** | `.env`, credentials | Stale endpoints or rotated keys | **Do not read values.** Check referenced hosts/paths still exist |
| **Binaries / media** | Images, PDFs, diagrams | Diagrams showing removed components; screenshots of old UI | Open and look. A diagram with no date is a finding |
| **Notebooks** | `*.ipynb` | Outputs from code that has since changed | Check output cells against current code |
| **IaC** | `*.tf`, CloudFormation | State drift; resources renamed outside the code | Compare plan against reality where safe |

## Binary and tabular data

**These cannot be grepped and are routinely skipped, while frequently being the most decision-relevant files in the project.** They need a different set of questions:

1. **Provenance** — which source produced this, and is that source still current? A parquet built from snapshot *N* when *N+1* exists is stale regardless of its timestamp.
2. **Freshness against its source, not the clock** — compare to the newest input, not to today. Prefer a filename or embedded stamp over mtime, which a restore or a copy silently resets.
3. **Schema** — do the columns still match what consumers expect?
4. **Row counts and derivation** — does the count reconcile against the source? A silently truncated export looks perfectly healthy.
5. **Is it derived or authoritative?** If derived, the audit target is the **generator**, and the file itself should be disposable and rebuilt.

```bash
python3 -c "import pandas as pd; d=pd.read_parquet('f.parquet'); print(d.shape, list(d.columns))"
python3 -c "import openpyxl; w=openpyxl.load_workbook('m.xlsx'); print(w.sheetnames)"
head -1 data.csv; wc -l data.csv
```

**For a spreadsheet that is the model rather than a report**, the audit target is whatever builds it. A hand-edited cell in a generated workbook is a finding in its own right.

## Generated context

`.ai-context/`, repomix packs, graph exports and similar are **stale by definition** the moment their sources change.

Do not audit their contents — you would be auditing a copy. **Regenerate them at the end of Phase 2** and confirm the rebuild succeeded. If one embeds copies of managed blocks or governance text, a
stale pack will keep serving pre-audit content to the next agent, which makes regeneration part of the fix rather than housekeeping.

## Legitimate exemptions

State the reason for each; a bare exemption list is where coverage quietly dies.

| Exemption | Reason |
|---|---|
| `docs/archive/`, `*.bak`, snapshots | Archives are *supposed* to contain superseded figures |
| `trackers/`, `source-captures/`, fixtures | Evidence — auditing it for staleness misunderstands what it is |
| `CHANGELOG.md` | Append-only audit trail; historical entries are correct as written |
| Generated context | Regenerated, not audited |
| `node_modules/`, vendored | Not the project's to fix |
| `.git/`, `__pycache__` | Machine state |

**Never exempt a file because it was noisy or awkward.** That is the ignore-list failure — it converts a real finding into a permanent blind spot.

## Worked accounting

From the originating run, abridged:

```text
Total files (excl. .git):        159
  Examined:                       97
    governance/routing             8   all read fully
    knowledge base (docs/)        27   all read; 8 gained supersession banners
    process/runbooks              12   read; no cost literals by design — confirmed
    code/scripts                  23   one line of reasoning each; 2 findings
    task runner                    1   stale check-count comment found
    structured config              3   parsed; misplaced key + duplicate key found
    tabular/binary                 2   xlsx via its generator; parquet freshness-checked
    trackers (derived views)       6   regenerated
    root governance               15   counts, dates, layout reconciled
  Exempt (stated):                59
    source-captures                6   evidence — byte-compared instead
    dated snapshots               42   evidence
    docs/archive/                  2   archive
    CHANGELOG.md                   1   audit trail
    generated context              8   regenerated, not audited
  Out of scope:                    3   .remember/ session buffers
                                 ----
                                  159   ✓
```

The line that matters: **`tabular/binary 2`**. A text-only sweep would have reported clean coverage while never opening the workbook that *is* the financial model, or the parquet that every query
reads. Both needed a different method, and both were in scope.
