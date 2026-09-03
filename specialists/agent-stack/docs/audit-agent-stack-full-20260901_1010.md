# Agent Stack: Full Architecture Audit

**Audit date:** 2026-09-01  
**Scope:** `/Volumes/Data/_ai/_skills/skills_stuff/specialists/agent-stack` at `1201e42`  
**Mode:** Evidence-based audit only. No canonical source, upstream state, global link, or configuration was modified.

## Contents

- [1. Executive Assessment](#1-executive-assessment)
- [2. What Agent Stack Is](#2-what-agent-stack-is)
- [3. Current Architecture](#3-current-architecture)
- [4. Repository Inventory](#4-repository-inventory)
- [5. End-to-End Behaviour](#5-end-to-end-behaviour)
- [6. What Is Designed Well](#6-what-is-designed-well)
- [7. Architectural Findings](#7-architectural-findings)
- [8. Orchestrator Findings](#8-orchestrator-findings)
- [9. Persona Findings](#9-persona-findings)
- [10. Skill Findings](#10-skill-findings)
- [11. Installation and Runtime Compatibility](#11-installation-and-runtime-compatibility)
- [12. Upstream Sync and Translation Review](#12-upstream-sync-and-translation-review)
- [13. Safety and Governance](#13-safety-and-governance)
- [14. Testing and Eval Coverage](#14-testing-and-eval-coverage)
- [15. Portability and Operational Risks](#15-portability-and-operational-risks)
- [16. Complexity and Duplication](#16-complexity-and-duplication)
- [17. Missing Capabilities](#17-missing-capabilities)
- [18. Intent-vs-Implementation Matrix](#18-intent-vs-implementation-matrix)
- [19. Prioritised Findings](#19-prioritised-findings)
- [20. Recommendations](#20-recommendations)
- [21. Proposed Target Architecture](#21-proposed-target-architecture)
- [22. Remediation Roadmap](#22-remediation-roadmap)
- [23. Final Verdict](#23-final-verdict)

## Evidence convention

- **FACT**: directly demonstrated by the cited repository path, line range, or command result.
- **INFERENCE**: conclusion from evidence that needs fault injection or a target runtime to prove.
- **RECOMMENDATION**: proposed future change.
- **UNKNOWN**: the repository cannot establish the point.

## 1. Executive Assessment

**Judgement: SOUND WITH MATERIAL GAPS.**

**FACT:** Agent Stack has a coherent core: an English canonical library, manifest-backed symlink installation, conservative upstream comparison, and a human-governed orchestrator. `just test` passed all 25 tests. `just upstream-dry-run` found no delta, and global status/dry run reported 123 correct links, zero missing links, and zero collisions.

**INFERENCE:** The project is usable in its controlled macOS environment. It does not yet prove reliable orchestration across runtimes, whole-library skill integrity, or failure-safe upstream application.

The three highest-value improvements are transactional hardened sync, a runnable library contract validator, and manifest-driven routing evals.

## 2. What Agent Stack Is

**FACT:** The project is an English-only extraction of Auto Company personas and skills that intentionally excludes autonomous loops, consensus machinery, daemons, and other no-human-gate patterns (`README.md:3-4`). It contains 15 personas and 37 skills: 36 `SKILL.md` packages plus `skills/frontend-design.md`. The manifest lists 52 capabilities (`manifest.yaml:14-71`).

**FACT:** `orchestrator` is the intended normal entry point. Direct specialist use is limited to a named specialist or deliberately narrow task (`skills/orchestrator/SKILL.md:10-16`). `orchestrator-follett` supplies persona-aware coordination guidance (`personas/orchestrator-follett.md:3-25`).

**FACT:** This directory is inside the parent `skills_stuff` Git checkout. Global installation resolves the primary checkout through Git before linking (`scripts/install_global.py:37-54`).

## 3. Current Architecture

```text
Auto Company upstream
        |
        v
sync_auto_company.py ---> review reports / translation brief
        |
        v
canonical personas/ + skills/ <--- manifest.yaml
        |
        v
install_global.py
  |        |         |          |
Claude    Codex   ~/.agents   project-local manual link
  \        |         |        /
   \       v         v       /
    ------- orchestrator -----
                |
                v
     human-governed synthesis
```

**FACT:** The installer creates verified individual absolute symlinks for persona files, packages, and the frontend adapter. It rejects a non-primary worktree, reconciles manifest and source inventory, preflights all targets, and deletes only links it created in a failed install (`scripts/install_global.py:50-96, 135-208`).

**FACT:** `upstream-state.json` records 186 imported upstream files, 17 in translated mode. `personas/orchestrator-follett.md` and `skills/orchestrator/SKILL.md` are intentional local extensions outside that import baseline.

**INFERENCE:** Canonical ownership is strong for global installation but weaker for project-local consumption: README gives a manual `ln -s` with no companion status, repair, or unlink workflow (`README.md:39-50`).

**FACT:** Manifest metadata stops at identity, kind, path, and portability. It does not expose triggers, exclusions, dependencies, risk, output contract, or required tools (`manifest.yaml:14-66`).

## 4. Repository Inventory

| Area              | Files/components                        | Purpose                                  | Authority           | Consumers                |
| ----------------- | --------------------------------------- | ---------------------------------------- | ------------------- | ------------------------ |
| Canonical library | `personas/*.md`, `skills/**`            | Roles, prompts, scripts, references      | Canonical           | Runtimes/projects        |
| Inventory         | `manifest.yaml`                         | Capability and upstream mappings         | Canonical inventory | Installer/orchestrator   |
| Installation      | `scripts/install_global.py`, `justfile` | Status, install, uninstall               | Canonical           | Claude, Codex, `.agents` |
| Upstream update   | Sync script, state, memory, policy      | Compare, classify, report, limited apply | Canonical           | Maintainers              |
| Documentation     | `README.md`, `justfile`                 | Operator procedure                       | Intended procedure  | Operators                |
| Core tests        | `tests/test_*.py`                       | Installer and sync behaviour             | Coverage evidence   | Maintainers              |
| Skill-local tests | DevOps tests, research fixtures         | Individual skill testing                 | Partial             | Skill maintainers        |
| Derived data      | `translation-memory.json`               | Translated-file hash index               | Derived             | Sync tool                |
| Runtime state     | External working-cache mirror/reports   | Disposable mirror/reports                | Runtime only        | Sync operator            |
| Unclear state     | `.remember/`, `.code-context-notes/`    | Present but not inventory-tracked        | UNKNOWN             | Local tooling            |

**FACT:** The project boundary contains no `LICENSE`, `CONTRIBUTING`, `CHANGELOG`, `SECURITY`, `CODEOWNERS`, workflow directory, or `.gitignore`. Parent-level governance is **UNKNOWN**.

## 5. End-to-End Behaviour

### Scenario A: normal user task

1. User invokes `orchestrator`.
2. It reads local instructions and frames scope, owner, evidence, constraints, and useful completion.
3. It reads manifest, calls `team`, selects two to five roles, and adds matching skills.
4. It requires independent critique for material, irreversible, or weakly evidenced work.
5. It returns facts, inference, disagreement, recommendation, risks, and next action as one synthesis.

**FACT:** This is defined in `skills/orchestrator/SKILL.md:8-47`; `team` supplies the role matrix and two-to-five rule (`skills/team/SKILL.md:16-59`).

### Scenario B: direct specialist invocation

**FACT:** Direct invocation fits a named specialist or narrow one-skill task, such as a pre-mortem or browser workflow (`skills/orchestrator/SKILL.md:15-16`). It does not fit cross-functional product, architecture, pricing, or deployment decisions.

### Scenario C: global installation

1. Operator runs `just global-dry-run`, then `just global-install install`.
2. Installer validates manifest paths against discovered source entries.
3. It refuses a non-primary checkout and preflights every selected target.
4. A collision blocks the full selected install before any links are created.
5. Uninstall removes only a link that still resolves to expected canonical source.

**FACT:** Tests cover dry run, idempotency, collision refusal, unexpected-target preservation, `skill-creator` exclusion, frontend collision, and worktree refusal (`tests/test_install_global.py:34-166`).

### Scenario D: project-local installation/discovery

**FACT:** README permits a canonical skills-directory link into `<project>/.agents/skills` only if the project does not own that directory. Persona linkage is optional because `.agents` has no universal persona convention (`README.md:39-50`).

### Scenario E: upstream refresh

1. `upstream-dry-run` compares existing detached mirror; `upstream-fetch-dry-run` fetches then compares.
2. Source maps `.claude/agents` and `.claude/skills` into canonical paths.
3. Files classify as `safe_add`, `safe_replace`, `translation_required`, `manual_merge`, or `remove_review`.
4. Apply copies only safe English additions/replacements and emits review proposals for all other classes.

**FACT:** Implementation is in `scripts/sync_auto_company.py:91-203, 253-399`. Existing mirror equals `ebfab9b4bd5f0ab5ad452a1ff85285b3c141acdd`; dry run reported no changes.

## 6. What Is Designed Well

- **FACT:** Installer collision handling prioritises user safety over convenience (`scripts/install_global.py:135-177`).
- **FACT:** Primary-worktree validation avoids global links into expendable worktrees (`scripts/install_global.py:37-54`).
- **FACT:** Sync protects local editorial work: divergence becomes `manual_merge`; removal becomes `remove_review`; translated updates remain review-only (`scripts/sync_auto_company.py:149-178`).
- **FACT:** Translation policy preserves reviewed English wording instead of whole-file model regeneration (`translation-policy.md:3-18`).
- **FACT:** Orchestrator preserves operator decision rights and prohibits loops, daemons, forced consensus, and cross-project memory (`skills/orchestrator/SKILL.md:28-34`).

## 7. Architectural Findings

| ID  | Priority | Finding                                                                                                                                                                             |
| --- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A1  | P1       | **INFERENCE:** Apply is non-atomic. Direct copy followed by report/state write can split source and state after failure, then force `manual_merge` on recovery                          |
|     |          |   (`scripts/sync_auto_company.py:181-203, 372-389`).                                                                                                                                |
| A2  | P1       | **INFERENCE:** Sync follows upstream and canonical symlinks through `is_file`, reads, and `copy2`; Git-supplied or local symlinks can escape intended roots                             |
|     |          |   (`scripts/sync_auto_company.py:91-103, 181-190`).                                                                                                                                 |
| A3  | P1       | **FACT:** `websh` specifies background agents, automatic eager crawl, and implicit `.websh` persistence, contradicting the no-background/no-implicit-persistence posture                |
|     |          |   (`skills/websh/state/cache.md:80-91, 396-405`; `state/crawl.md:1-78`).                                                                                                            |
| A4  | P1       | **FACT:** `deep-research` creates Documents and `~/.claude/research_output` state, continuation agents, and viewer launches without opt-in                                              |
|     |          |   (`skills/deep-research/SKILL.md:205-255, 437-607`).                                                                                                                               |
| A5  | P1       | **FACT:** `quick_validate.py` fails because configured Python lacks `yaml`; its schema rejects current `version`, `tags`, `auto_activate`, `agents`, and `argument-hint` metadata       |
|     |          |   (`skills/skill-creator/scripts/quick_validate.py:9, 41-50`).                                                                                                                      |
| A6  | P1       | **FACT:** `startup-business-models` references six absent local resources, missing `data/sources.json`, and four absent related skills                                                  |
|     |          |   (`skills/startup-business-models/SKILL.md:27-37, 85-109`).                                                                                                                        |
| A7  | P1       | **INFERENCE:** Normal routing depends on model judgement because manifest lacks semantics and no behavioural eval tests selection, disagreement, or direct-vs-orchestrated routing      |
|     |          |   (`skills/orchestrator/SKILL.md:20-22`, `manifest.yaml:14-66`).                                                                                                                    |
| A8  | P2       | **FACT:** Manifest says `directory-symlink`; global install creates individual links. README calls all 37 entries packages despite one single-file adapter.                             |
| A9  | P2       | **FACT:** `orchestrator-follett` lacks YAML frontmatter. Runtime acceptance is **UNKNOWN** and untested.                                                                                    |
| A10 | P2       | **INFERENCE:** Installer parses manifest paths with narrow regex rather than YAML, so formatting changes are brittle (`scripts/install_global.py:57-80`).                               |
| A11 | P2       | **FACT:** Overlapping security skills point to absent skills, agents, and task systems (`skills/code-review-security/SKILL.md:34-40`, `skills/security-audit/SKILL.md:23-43`).          |
| A12 | P2       | **FACT:** README says `project_agnostic`/`tool_specific`; manifest uses `general`/`tool-specific` (`README.md:54-55`, `manifest.yaml:30-66`).                                           |
| A13 | P2       | **FACT:** Root tests omit skill-local tests. DevOps collection fails because `pytest` is not in configured `mise` Python.                                                               |
| A14 | P2       | **INFERENCE:** Origin URL comparison does not authenticate commit content. `--source` accepts a matching checkout and no final hash check closes TOCTOU                                 |
|     |          |   (`scripts/sync_auto_company.py:114-135, 253-308`).                                                                                                                                |
| A15 | P3       | **FACT:** No project-boundary provenance, security-reporting, runtime matrix, or release/migration policy exists. Parent coverage is **UNKNOWN**.                                           |

## 8. Orchestrator Findings

**FACT:** The prompt-level contract is strong: scope, decision owner, evidence, constraints, team/gates, bounded hand-offs, critique, one synthesis, and stop conditions (`skills/orchestrator/SKILL.md:18-34`).

**FACT:** Its inventory cannot determine routing. Manifest lacks domain, precedence, dependencies, safety tier, and tool requirements. `team` maps personas only (`skills/team/SKILL.md:16-55`).

**INFERENCE:** The model must infer outbound versus lifecycle email, SEO audit versus SEO strategy, and code security review versus security audit. Runtime variability is a design risk.

**RECOMMENDATION:** Keep the prose contract; add manifest fields for domain, exclusions, risk tier, tools, dependencies, direct-use eligibility, and composition.

## 9. Persona Findings

| Persona                | Unique role                     | Recommendation                               |
| ---------------------- | ------------------------------- | -------------------------------------------- |
| `ceo-bezos`            | Customer-backwards strategy     | Keep for company trade-offs.                 |
| `cfo-campbell`         | Pricing/capital discipline      | Keep; skills calculate, persona judges.      |
| `critic-munger`        | Inversion/independent review    | Keep as independent check.                   |
| `cto-vogels`           | Architecture/reliability        | Keep; owns system trade-offs.                |
| `devops-hightower`     | Delivery/observability          | Keep; owns operational design.               |
| `fullstack-dhh`        | Vertical slices                 | Keep; implementation scope differs from CTO. |
| `interaction-cooper`   | Goals/task flows                | Keep; flow boundary is clear.                |
| `marketing-godin`      | Positioning/audience            | Keep; owns demand story.                     |
| `operations-pg`        | Early-stage execution           | Keep; weekly operating focus differs.        |
| `orchestrator-follett` | Coordination                    | Add metadata and conformance test.           |
| `product-norman`       | Usability/control/recovery      | Keep; requirements boundary differs.         |
| `qa-bach`              | Quality risk/release confidence | Keep; persona sets risk posture.             |
| `research-thompson`    | Evidence-led research           | Keep; evidence governance differs.           |
| `sales-ross`           | ICP/qualification/pipeline      | Keep; process differs from copy.             |
| `ui-duarte`            | Visual hierarchy/system         | Keep; visual ownership is distinct.          |

**Conclusion:** Do not consolidate personas. Most apparent overlap separates strategic judgement from tactical workflow.

## 10. Skill Findings

| Skill                              | Category       | Core purpose               | Quality/gap                             |
| ---------------------------------- | -------------- | -------------------------- | --------------------------------------- |
| `agent-browser`                    | Browser        | Navigation/forms/snapshots | Strong, tool-specific.                  |
| `code-review-security`             | Security       | OWASP review               | Overlap and stale routes.               |
| `cold-email-sequence-generator`    | Outbound       | Sales campaign copy        | Lifecycle overlap.                      |
| `community-led-growth`             | Growth         | Community programmes       | Missing output/failure contract.        |
| `competitive-intelligence-analyst` | Research       | Competitor intelligence    | Strong workflow.                        |
| `content-strategy`                 | Marketing      | Content planning           | Broad SEO overlap.                      |
| `deep-analysis`                    | Analysis       | Audit templates            | Too broad for routing.                  |
| `deep-reading-analyst`             | Analysis       | Long-form analysis         | Strong references.                      |
| `deep-research`                    | Research       | Multi-source research      | Unsafe persistence/background defaults. |
| `devops`                           | Delivery       | Cloud/container work       | Test environment incomplete.            |
| `email-sequence`                   | Lifecycle      | Drip/lifecycle flow        | Missing tools registry.                 |
| `financial-unit-economics`         | Finance        | CAC/LTV analysis           | Strong resources.                       |
| `find-skills`                      | Discovery      | External skill install     | Needs install-authority gate.           |
| `frontend-design`                  | UI             | Frontend design            | Clear single-file adapter.              |
| `github-explorer`                  | Research       | GitHub assessment          | Strong checklist.                       |
| `market-sizing-analysis`           | Finance        | TAM/SAM/SOM                | Strong methodology.                     |
| `micro-saas-launcher`              | Startup        | Validation/launch          | Weak evidence discipline.               |
| `orchestrator`                     | Coordination   | Team/synthesis             | Strong intent, unenforced.              |
| `ph-community-outreach`            | Marketing      | Product Hunt outreach      | Unsourced counts age.                   |
| `premortem`                        | Risk           | Failure analysis           | Focused and useful.                     |
| `pricing-strategy`                 | Finance        | Pricing/packaging          | Finance-skill overlap.                  |
| `product-strategist`               | Strategy       | Market/GTM/portfolio       | Overbroad trigger.                      |
| `scientific-critical-thinking`     | Research       | Research rigor             | Missing schematics dependency.          |
| `security-audit`                   | Security       | Code/dependency/config     | Overlap and stale tools.                |
| `senior-qa`                        | QA             | Test/coverage/E2E          | Environment not packaged.               |
| `seo-audit`                        | SEO            | Technical/on-page audit    | SEO strategist overlap.                 |
| `seo-content-strategist`           | SEO            | Organic strategy           | Broad activation.                       |
| `skill-creator`                    | Meta           | Create/validate skills     | Validator broken.                       |
| `startup-business-models`          | Finance        | Revenue/pricing model      | Broken references.                      |
| `startup-financial-modeling`       | Finance        | Startup forecast           | Large but usable.                       |
| `tailwind-v4-shadcn`               | Frontend       | Toolchain setup            | Correctly tool-specific.                |
| `team`                             | Coordination   | Persona selection          | Static matrix duplicates manifest.      |
| `user-persona-creation`            | UX research    | Persona research           | Long but usable.                        |
| `user-research-synthesis`          | UX research    | Qual/quant synthesis       | Strong methodology.                     |
| `ux-audit-rethink`                 | UX             | Broad UX audit             | Overlong and broad.                     |
| `web-scraping`                     | Web data       | Extraction/API discovery   | Anti-bot needs approval gate.           |
| `websh`                            | Web navigation | Web shell/cache            | Contradicts safety model.               |

**FACT:** Skill shapes range from concise packages to 500–1,100-line monoliths. `skill-creator` requires concise frontmatter-led packages and avoiding duplicated supporting text (`skills/skill-creator/SKILL.md:20-82`).

## 11. Installation and Runtime Compatibility

| Runtime/path           | Assessment                                         |
| ---------------------- | -------------------------------------------------- |
| Claude personas        | Installed, parser untested.                        |
| Claude skills          | Installed; frontend adapter correct at link level. |
| Codex skills           | Installed, discovery untested.                     |
| Compatible `.agents`   | Installed; README limits claim.                    |
| Project `.agents`      | Manual link; no status, repair, unlink helper.     |
| Other persona runtimes | UNKNOWN; no adapter/conformance test.              |

**FACT:** Status and dry run report 123 correct links and no collision. **INFERENCE:** Add a `doctor` command. `uninstall` lacks the primary-checkout guard that protects install; exact source resolution makes it narrow, but symmetry is clearer.

## 12. Upstream Sync and Translation Review

| Branch                              | Actual behaviour        | Assessment                        |
| ----------------------------------- | ----------------------- | --------------------------------- |
| New English file                    | `safe_add`              | Safe if source trusted/contained. |
| New non-English file                | `translation_required`  | Blocks direct import.             |
| Changed translated file             | `translation_required`  | Strong English protection.        |
| Changed adapted file                | `manual_merge`          | Strong editorial protection.      |
| Mirrored unchanged-canonical change | `safe_replace`          | Correct fast path.                |
| Canonical divergence                | `manual_merge`          | Strong source protection.         |
| Upstream removal                    | `remove_review`         | Strong no-delete default.         |
| Rename                              | Add plus removal review | Safe, no rename pairing.          |

**FACT:** Tests cover classifications, safe-only copy, detached checkout, and baseline rejection (`tests/test_sync_auto_company.py:55-175`).

**INFERENCE:** Stage copies, reports, and state in a same-filesystem temporary location, validate, then atomically promote. Direct copy and JSON write cannot recover cleanly from interruption (`scripts/sync_auto_company.py:50-52, 181-203, 372-389`).

**INFERENCE:** Reject symlinks and validate resolved containment before hashing, reading, reporting, or copying. A hostile upstream symlink and local target symlink both escape roots.

**FACT:** `--source` accepts any local Git checkout and `--upstream-url` overrides run URL (`scripts/sync_auto_company.py:311-365`). **INFERENCE:** Operator intent is the trust boundary; no signature, commit pin, remote attestation, or final source hash check exists.

## 13. Safety and Governance

| Area                           | Classification      |
| ------------------------------ | ------------------- |
| Installer overwrite protection | Safe by design.     |
| Upstream deletion              | Safe by design.     |
| Translation replacement        | Safe by design.     |
| Orchestrator decision rights   | Safe by convention. |
| `websh` background work        | Contradictory.      |
| `deep-research` persistence    | Contradictory.      |
| Web scraping anti-bot patterns | Potentially unsafe. |
| Deploy scripts                 | Safe by convention. |

**RECOMMENDATION:** Give every skill a safety tier: read-only, local write, external effect, persistent state, background work, or privileged action. Require explicit approval above read-only unless user already requested that effect.

## 14. Testing and Eval Coverage

| Command                        | Result                       |
| ------------------------------ | ---------------------------- |
| `just test`                    | 25/25 passed.                |
| `just upstream-status`         | 186 tracked, 17 translated.  |
| `just upstream-dry-run`        | No changes.                  |
| `just global-status` / dry run | 123 correct, no collision.   |
| Skill validator                | `ModuleNotFoundError: yaml`. |
| DevOps pytest collection       | `No module named pytest`.    |

**FACT:** Tests do not cover runtime discovery, persona parsing, routing, direct-vs-orchestrated behaviour, disagreement, reference integrity, atomic recovery, symlink rejection, malformed state, or broken-link diagnosis.

Minimum viable evals: manifest/reference validation; routing fixtures; synthesis-label fixtures; sync fault injection; and runtime adapter conformance tests.

## 15. Portability and Operational Risks

| Assumption                     | Classification                                  |
| ------------------------------ | ----------------------------------------------- |
| `/Volumes/Data/...` paths      | Intentional limitation.                         |
| Bash and `just`                | Portability limitation.                         |
| Python 3.14 via `mise`         | Intentional limitation, dependencies absent.    |
| POSIX symlinks                 | Portability limitation.                         |
| `~/.claude` state              | Architectural defect.                           |
| Documents and automatic `open` | Architectural defect.                           |
| External CLIs/packages         | Harmless when declared, declaration incomplete. |

## 16. Complexity and Duplication

**Justified complexity:** Hash classification, translation memory, per-entry collision checks, and worktree protection prevent concrete canonical-ownership loss.

**Accidental complexity:** Multiple skill conventions, finance/SEO/security/startup overlap, static persona matrix duplication, and large monoliths increase selection and context cost without verified guarantees.

**Do not simplify:** Keep `manual_merge`, `translation_required`, `remove_review`, exact collision refusal, and symlink-only installation.

## 17. Missing Capabilities

| Capability                 | Priority |
| -------------------------- | -------- |
| Library contract validator | P1       |
| Routing metadata/evals     | P1       |
| Transactional sync         | P1       |
| Safety tier                | P1       |
| Project-local doctor       | P2       |
| Runtime matrix             | P2       |
| Reference checker          | P2       |
| Licence/provenance record  | P2       |
| Release/migration policy   | P3       |

## 18. Intent-vs-Implementation Matrix

| Principle                 | Alignment    | Gap                                              |
| ------------------------- | ------------ | ------------------------------------------------ |
| One canonical source      | Strong       | Project-local flow manual.                       |
| Symlink-only install      | Strong       | Manifest wording differs.                        |
| No copying                | Strong       | Sync copies upstream into source by design.      |
| Orchestrator normal entry | Partial      | No dispatcher, metadata, eval.                   |
| Smallest useful team      | Partial      | No enforcement/test.                             |
| Fact/inference separation | Partial      | No synthesis eval.                               |
| Disagreement surfaced     | Partial      | No protocol.                                     |
| No autonomous daemon      | Contradicted | `websh` and deep research use background agents. |
| Human approval            | Partial      | Skills can persist, crawl, deploy.               |
| Safe upstream update      | Partial      | Non-atomic and trust gaps.                       |
| Preserve English          | Strong       | Heuristic limit undocumented.                    |
| Multi-runtime support     | Partial      | Parser/discovery untested.                       |

## 19. Prioritised Findings

| Priority | Findings                                                                                                               |
| -------- | ---------------------------------------------------------------------------------------------------------------------- |
| P0       | None. Default core commands do not delete canonical source or overwrite existing global entries.                       |
| P1       | A1 transactional sync, A2 symlink escape, A3 `websh`, A4 deep-research, A5 validator, A6 startup skill, A7 routing.    |
| P2       | A8 terminology, A9 persona schema, A10 regex parse, A11 security routes, A12 class drift, A13 tests, A14 trust/TOCTOU. |
| P3       | Boundary docs, release/migration process, selective prompt compression.                                                |

## 20. Recommendations

| Timing      | Recommendation                                                                            | Benefit                         |
| ----------- | ----------------------------------------------------------------------------------------- | ------------------------------- |
| DO NOW, P1  | Stage sync copies/report/state, validate, atomically promote.                             | Prevent split state/source.     |
| DO NOW, P1  | Reject symlinks, validate containment, atomically write JSON.                             | Prevent path escape/corruption. |
| DO NOW, P1  | Repair/remove broken dependencies; use one metadata schema.                               | Make library runnable.          |
| DO NOW, P1  | Make websh/deep-research persistence/background opt-in.                                   | Restore human control.          |
| DO NEXT, P1 | Add routing/safety metadata and fixture evals.                                            | Stable cross-model routing.     |
| DO NEXT, P2 | Use YAML parser and declared dev test environment.                                        | Trustworthy health check.       |
| DO NEXT, P2 | Add `just doctor` and project-local link helper.                                          | Better recovery.                |
| DO NEXT, P2 | Add persona schema and runtime matrix.                                                    | Testable compatibility.         |
| OPTIONAL    | Add provenance/release docs; split monoliths after tests.                                 | Lower ambiguity/context cost.   |
| DO NOT DO   | Do not auto-merge translations, delete removals, bulk-replace directories, or add daemon. | Preserve safeguards.            |

## 21. Proposed Target Architecture

```text
agent-stack/
  manifest.yaml                 # inventory + routing/safety/runtime metadata
  personas/                     # concise, frontmatter-valid roles
  skills/                       # self-contained link-valid packages
  scripts/
    install_global.py           # status/install/doctor/uninstall
    sync_auto_company.py        # staged atomic report-first update
    validate_library.py         # metadata, references, dependencies
  tests/
    test_install_global.py
    test_sync_auto_company.py
    test_library_contract.py
    test_routing_evals.py
  docs/
    compatibility.md
    provenance.md
```

**RECOMMENDATION:** Keep the source model, installer approach, personas, `just` commands, and conservative sync categories. Add only machine-checkable facts needed to enforce existing promises.

## 22. Remediation Roadmap

### Phase 0: protect existing behaviour

| Task                        | Acceptance criteria                                          |
| --------------------------- | ------------------------------------------------------------ |
| Capture regression fixtures | Existing 25 tests remain green; zero-delta fixture retained. |
| Add sync fault tests        | Copy/report/state errors leave recoverable source/state.     |
| Add inventory test          | Every manifest path/internal reference resolves.             |

### Phase 1: correctness

| Task                     | Acceptance criteria                                       |
| ------------------------ | --------------------------------------------------------- |
| Transactional sync       | No partial update survives injected failure.              |
| Containment/atomic state | Symlinks/traversal rejected; state atomic.                |
| Repair broken skills     | Validator/workflows run in configured environment.        |
| Make unsafe work opt-in  | No persistence/background/viewer launch without approval. |

### Phase 2: architecture

| Task                        | Acceptance criteria                                          |
| --------------------------- | ------------------------------------------------------------ |
| Add routing/safety metadata | Every capability declares domain, exclusions, tools, safety. |
| Define precedence           | Email, SEO, security, finance conflicts documented/tested.   |
| Align install vocabulary    | Manifest, README, installer agree.                           |
| Add persona schema          | Every persona parses under agreed schema.                    |

### Phase 3: quality

| Task                                  | Acceptance criteria                                           |
| ------------------------------------- | ------------------------------------------------------------- |
| Add `just validate` and `just doctor` | Read-only health output covers library/dependency/link state. |
| Add runtime matrix                    | Support claims have parser/discovery evidence.                |
| Add behavioural evals                 | Tasks select minimal roles and expose disagreement/unknowns.  |

### Phase 4: optional evolution

| Task                            | Acceptance criteria                                        |
| ------------------------------- | ---------------------------------------------------------- |
| Refactor selected large prompts | No contract loss; links valid; activation context reduced. |
| Add provenance/release docs     | Operators can establish rights and upgrade handling.       |

## 23. Final Verdict

1. **Architecturally sound?** Yes, with material gaps. Canonical ownership, collision refusal, and report-first sync are strong foundations.
2. **Orchestrator appropriate?** Yes. It needs metadata and behavioural evals before universal reliance.
3. **Personas and skills separated correctly?** Mostly. Personas carry strategic judgement; skills carry tactical workflow. Do not consolidate personas.
4. **Canonical ownership protected?** Strong for global install; incomplete for sync until transactional and containment-safe.
5. **Upstream sync safe?** Conservative on normal paths, insufficient under copy/state failure or malicious path input.
6. **Unnecessarily complex?** Core safeguards are justified. Skill overlap, stale dependencies, and monoliths are accidental complexity.
7. **Three highest-value improvements?** Transactional sync, library validator, manifest-driven routing evals.
8. **What should not change?** Symlink-only install, whole-selection collision refusal, translation/removal review gates, human decision ownership, and two-to-five-role orchestration.

### Validation limits

The audit did not fetch/apply upstream changes, mutate global links, install dependencies, invoke external CLIs, or exercise target runtime parsing. Those require a separate scoped change or compatibility test.
