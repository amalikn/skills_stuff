---
name: skill-careertracker
description: Use when given a job ad URL and asked to assess a role, create a job tracking entry, or evaluate career fit. Also triggers for job-market sourcing requests like "search Melbourne jobs", "find roles matching my profile", or "run jobspy". Triggers on job posting URLs, "track this job", "assess this role", or when a recruiter message accompanies a job link.
---

# skill-careertracker

## Overview

Two complementary workflows:
1. **Source candidates** via JobSpy when given a location or profile-based search request (Step 0).
2. **Assess a specific role** from a job ad URL: fetch the posting, research the company, analyze fit against the user's background, and then drive the **three-phase, approval-gated** build workflow (Phase 1 markdown → Phase 2 docx → Phase 3 PDF).

## Input

- Job ad URL (required for assessment path), or
- Location + expertise angle (for sourcing path — e.g. "Melbourne network roles")
- Recruiter message or additional context (optional)

---

## Three-phase build workflow (authoritative)

Every new-job assessment follows three phases with **explicit user approval gates between each**. Do not collapse phases. Producing docx before the markdown is approved — or PDFs before the docx is approved — wastes iteration budget and is forbidden by the career repo's AGENTS.md. The authoritative contract is [`04-resumes/scripts/CONFIG_CONTRACT.md`](/Volumes/Data/_ai/_project/project_stuff/me/career/04-resumes/scripts/CONFIG_CONTRACT.md).

| Phase | Agent produces | Gate |
|-------|----------------|------|
| **1 — Markdown assessment** | `<company>-<role>.md` (17 sections) + SCRATCHPAD updates + RADAR row + 04-resumes/index.md placeholder | **Stop; ask user to review the markdown before writing any configs.** |
| **2 — DOCX generation** | `scripts/resume_config.py` + `scripts/cover_letter_config.py` + `build_role.py <company> <role>` → resume.docx + cover_letter.docx + workday_profile.docx | **Stop; ask user to review docx layout and content before PDF.** |
| **3 — PDF conversion (opt-in)** | Only on explicit user request: `build_role.py <company> <role> --pdf` (uses Microsoft Word's AppleScript engine) | n/a — terminal phase |

Capability overview is **opt-in only** via `--include-capability` — never auto-copied. PDFs are **opt-in only** — never auto-produced.

---

## Workflow

### 0. Source candidates with JobSpy (optional — when no URL given)

When asked to **search**, **find**, or **discover** roles (no specific URL), use the governed JobSpy tool before any assessment work.

**Tool location**: `/Volumes/Data/_ai/_tool/tools_stuff/jobspy/`
- Runner: `scripts/jobspy-run.sh` (venv resolved automatically)
- Saved queries: `queries/<location>-<angle>.sh` (reusable templates)
- Venv: `/Volumes/Data/_ai/_tool/tools-working-cache/jobspy/venv/`

**Default search angles for this user's profile** (run 3–4 in parallel):
1. `"network engineer"` — carrier/SP/CCIE base
2. `"network architect"` — architect tier
3. `"cloud network engineer"` — Cumulus/DC fabric/cloud provider
4. `"site reliability engineer"` — platform/SRE adjacent
5. Optional: `"ai infrastructure"`, `"platform engineer"`, `"data center network"` depending on explicit focus

**Invocation pattern** (Melbourne example):
```bash
bash /Volumes/Data/_ai/_tool/tools_stuff/jobspy/scripts/jobspy-run.sh \
  --site indeed linkedin \
  --search "<angle>" \
  --location "Melbourne, VIC" \
  --country-indeed "Australia" \
  --hours-old 168 \
  --results 25 \
  --out /Volumes/Data/_ai/_tool/tools_stuff/jobspy/output/<loc>-<angle>.csv
```

Run in background (parallel) — each scrape takes 60–90s per site.

**Scoring regex weights** (apply against concatenated title+company+description; `fit = sum(weights)`):
- POS: carrier/SP/MPLS/BGP/OSPF/IS-IS `+3`; CCIE/CCNP/JNCIE `+3`; Cumulus/SONiC/EVPN/VXLAN/Clos/spine-leaf/fabric/DC `+3`; NVIDIA/Spectrum-X/Mellanox `+3`; AI/LLM/GPU/MLOps/inference `+2`; Ansible/Terraform/Python/Linux/FRR/network-automation `+2`; senior/principal/lead/staff/architect `+2`; Telstra/Optus/NBN/AWS/Azure/GCP `+1`
- NEG: junior/graduate/intern `-4`; helpdesk/desktop/field/cabling `-3`; sales/account-mgr `-2`; wireless/wifi/RF-engineer `-1`; windows/SCCM/Intune/AD `-2`
- Threshold: keep `fit >= 3`

**Outcome archival (mandatory)**:
Every JobSpy run outcome must be archived under the career repo, not left in the tool's shared output dir:
```
01-jobs/00-jobspy-outcomes/<YYYYMMDD>-<location>/
  mel-network-engineer.csv
  mel-network-architect.csv
  mel-cloud-network.csv
  mel-sre.csv
  mel-curated-top.csv      ← fit-scored + deduped top 40
  README.md                ← query angles, weights used, top matches, run date
```
Subfolders OK when outcomes span multiple locations or angle batches. The tool's `output/` dir is staging only; archival to `00-jobspy-outcomes/` is the source of truth.

**Tracker rebuild**: after archiving a new run, also regenerate `01-jobs/00-jobspy-outcomes/TRACKER.md` so the aggregate cross-run table stays current (see the career repo AGENTS.md for the rebuild contract).

**Handoff to Phase 1**: present top 10–15 with fit score, company, URL. User picks 2–3 roles → invoke the Phase 1 flow per URL for full 17-section assessments.

### 1. Fetch and parse the job posting

Use `mcp__plugin_context-mode_context-mode__ctx_fetch_and_index` with the job URL. Extract:
- Role title (exact)
- Company name
- Location
- Key requirements: domain, technical stack, protocols, leadership expectations
- Seniority level and reporting structure (if stated)
- Nice-to-haves vs hard requirements

### 2. Research the company

Use web search to establish:
- What the company sells / builds (plain English, not marketing copy)
- What they are most known for (products, technologies, reputation)
- Their AI and technology positioning
- Closest analogues (e.g. "closer to Cisco than to enterprise IT")
- Melbourne/APAC presence and scale (if role is Melbourne-based)

### 3. Load user background

Read active resumes from:
`/Volumes/Data/_ai/_project/project_stuff/me/career/04-resumes/`

Also read the live capability source of truth:
`/Volumes/Data/_ai/_project/project_stuff/me/career/02-capability/core_strengths.md`

Key anchors (always apply unless capability docs say otherwise):
- Lead credential: CCIE Service Provider. **Always use the full "CCIE Service Provider" phrase — never bare "CCIE"** in resume, cover letter, LinkedIn, or any verbal interview context. The SP qualifier is the lead credential's differentiator.
- Narrative anchor: **Australian decade leads** — APN (2020–present), Telstra/Belong (2017), AINS. Ericsson (Kuwait, 2011–2016) = foundational context only, not headline. Never lead with Ericsson.
- Core strengths: IP/MPLS, service-provider architecture, BGP/OSPF/IS-IS, telecom delivery leadership, customer-facing technical engagement, multivendor environments, Telstra/Belong national-scale ISP, Ericsson telecom vendor delivery foundation, Mada SDH/optical/WiMAX
- **Cumulus Linux**: 6+ years hands-on production at APN (2020–present). Strong fit, not a gap, for Cumulus, SONiC, NVIDIA Spectrum-X, or Linux NOS roles.
- **Agentic AI / LLM hands-on stack** (current practice, not aspiration):
  - Cloud: Anthropic (Claude), OpenAI (GPT family)
  - Local: Ollama, LiteLLM, LM Studio
  - Agent runtime: MCP servers, skills, plugins, slash commands, multi-agent orchestration (governor/specialist/executor patterns), memory architecture (memory-keeper, project-context)
  - Active interest in AI infrastructure strategy, CDAIO/CTO(AI) trajectory
- Target compensation: AUD 250k+ base
- Market: Melbourne, VIC

### 4. Analyze fit

Assess along these dimensions:
- **Strong fit areas**: where background clearly maps to requirements
- **Main mismatch / risk**: what the role needs that background doesn't cover strongly
- **Salary realism**: Melbourne market benchmarks for the level; is AUD 250k achievable?
- **AI/LLM relevance**: does this role accelerate, sideline, or stay adjacent to AI ambitions?
- **Career upside**: vendor credibility, domain expansion, strategic positioning

---

## PHASE 1 — Markdown assessment

### 5. Create folder and write the assessment file

Derive slugs:
- Company slug: lowercase, hyphens, no spaces (e.g. `ciena`, `cisco`, `telstra`)
- Role slug: lowercase, hyphens, from role title (e.g. `senior-network-engineering-manager`)

Create the role folder (configs and generated/ come later in Phase 2 — do **not** create scripts/ or generated/ in Phase 1):

```
/Volumes/Data/_ai/_project/project_stuff/me/career/01-jobs/01-active/<company>/<role-slug>/
  <company>-<role-slug>.md      ← assessment file (this phase's deliverable)
```

Canonical template lives at `01-jobs/_template/job-assessment-template.md`. Copy or use as reference. The embedded template at the bottom of this skill is a backup specification — if the repo template diverges, the repo template wins.

Generate all 17 sections. Add a TOC after the header block.

### 6. Update SCRATCHPADs, RADAR, and resume index (Phase 1 completion)

After the assessment file is written:

**Root `SCRATCHPAD.md`**: update the phase line and add a row to the portfolio snapshot.

**Company `01-jobs/01-active/<company>/SCRATCHPAD.md`**: append a row to Roles table, update Open items, update Recent activity, refresh Memory pointers. If the file does not exist, create it using the template in the "Company SCRATCHPAD template" section below.

**`01-jobs/RADAR.md`**: add a row with fit score, 250k likelihood, AI relevance, next action, and assessment link. Update "Last updated" date and pipeline counts. Recompute the Priority ranking table (combined decision score).

**`04-resumes/index.md`**: add a placeholder entry linking to the forthcoming `scripts/` and `generated/` folders for this role. The scripts and generated docs don't exist yet — this is a placeholder that becomes active in Phase 2.

### 7. **PHASE 1 GATE — stop and ask for approval**

State clearly to the user:

> Phase 1 complete. The markdown assessment is at `<path>`. SCRATCHPADs and RADAR are updated. **Please review the markdown** before I write the config scripts and generate docx. Reply "looks good" or describe any changes you want.

**Do not proceed to Phase 2 until the user approves.**

---

## PHASE 2 — DOCX generation (requires user approval from Phase 1)

### 8. Write config scripts

Only after user approves the markdown, write the two config files:
- `scripts/resume_config.py`
- `scripts/cover_letter_config.py`

Follow the **authoritative contract at [`04-resumes/scripts/CONFIG_CONTRACT.md`](/Volumes/Data/_ai/_project/project_stuff/me/career/04-resumes/scripts/CONFIG_CONTRACT.md)**. Key rules restated here for convenience:

**Density targets** (floors, not ceilings):
- Resume: total content ≥ 1000 words (exec_profile ~298 across 3 substantial paragraphs, capabilities 10 bullets ~77, toolkit 6–8 categories ~148, six job entries with bullets ~494)
- Cover letter: total content ≥ 630 words (opening ~95, 4 section bodies ~491, closing ~45)

**Cover letter section anchors (fixed — do not change)**:
`sections[i].find` values must be exactly `TECHNICAL LEADERSHIP`, `ARCHITECTURE & DELIVERY`, `TECHNICAL DEPTH`, `WHY I ADD VALUE` in that order. Change only the `heading` and `body` values.

**Find-phrase collision rule**: no section `body` may contain any other section's `find` string as a case-insensitive substring. Common trap: writing "technical depth" in section 1 or 2 body collides with section 3's find. Rephrase to "stack depth" or "protocol depth". A builder fix makes section lookup heading-only so this no longer blanks output, but honour the rule as defence in depth.

**AI-relevance tailoring** (from assessment §9):
- Score 9–10: AI featured in exec_profile para 3 + expanded in cover-letter TECHNICAL DEPTH + toolkit category
- Score 7–8: AI mentioned once in exec_profile + expanded in TECHNICAL DEPTH + toolkit category
- Score 4–6: AI mention in toolkit only + one brief line in TECHNICAL DEPTH
- Score 1–3: AI mention in toolkit only — no exec_profile or opening mention

**Reference configs (always read these before authoring)**:
- Gold standard: `01-jobs/02-applied/nvidia/senior-solutions-architect-networking-ethernet/scripts/`
- Second reference: `01-jobs/01-active/armada/ai-factory-customer-engineer/scripts/`

**`scripts/resume_config.py` structure:**

```python
"""<Company> — <Role Title> — resume config."""

OUTPUT_FILENAME = "Malik_Ahmad_Resume_<Company>_<Abbrev>.docx"

CONFIG = {
    "subtitle": "<Role Title> | <Other Title> | CCIE Service Provider",

    "exec_profile": [
        # Para 1 — career overview tailored to this role's domain (~95 words)
        "...",
        # Para 2 — Australian decade leads (APN, Telstra/Belong, AINS); Ericsson as foundational context only (~140 words)
        # Pattern: "Over the past decade in Australia I have... This Australian track record is underpinned by five years at **Ericsson**..."
        "...",
        # Para 3 — value proposition for this specific company/role (~80 words)
        "...",
    ],

    "capabilities": [
        # Exactly 10 bullets — reorder/reword to match job requirements
        "Engineering Team Leadership and Delivery Governance",
        # ... tailor remaining bullets to role keywords
    ],

    "toolkit": (
        # \n-separated lines; format: "Label: content"
        # Builder renders label bold, content plain
        # 6–8 category lines, ~148 words total
        "Routing & Service Provider: BGP, OSPF, IS-IS, ...\n"
        "Switching & Overlay: ...\n"
        "Security: ...\n"
        "Platforms: ...\n"
        "Cloud & Infrastructure: ...\n"
        "Automation & Observability: ...\n"
        "AI & LLM Integration: Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), "
        "agentic workflows, prompt engineering, MCP, skills, plugins, across cloud (OpenAI, Anthropic) "
        "and local environment (Ollama, LiteLLM, LM Studio), AI-assisted automation and tooling"
    ),

    "jobs": [
        # Exactly 6 entries in this order — the orchestrator expects this layout
        {
            "find": ["Australian Private Networks"],
            "header": "Network & IT Manager — Australian Private Networks (APN) | Melbourne | Apr 2020 – Present",
            "bullets": ["...", "...", "...", "...", "...", "..."],  # 5–7 bullets for APN (richest)
        },
        {"find": ["AINS", "Australia Internet Solutions"], "header": None, "bullets": ["...", "...", "...", "..."]},
        {"find": ["Belong"],  "header": "Network Domain Specialist — Telstra (Belong) | Melbourne | Jan 2017 – Dec 2017", "bullets": ["...", "...", "..."]},
        {"find": ["Whispir"], "header": None, "bullets": ["...", "...", "..."]},
        {
            "find": ["Ericsson"],
            "header": "Network Design / Integration Engineer — Ericsson | Kuwait | Apr 2011 – Apr 2016",
            "bullets": ["...", "...", "..."],
        },
        {"find": ["Mada"], "header": None, "bullets": ["...", "...", "...", "..."]},
    ],
}
```

**`scripts/cover_letter_config.py` structure:**

```python
"""<Company> — <Role Title> — cover letter config."""

OUTPUT_FILENAME = "Malik_Ahmad_Cover_Letter_<Company>_<Abbrev>.docx"

CONFIG = {
    "opening": "...",   # ~95 words: who you are, years of experience, role applying for, why strong candidate

    "sections": [
        {"find": "TECHNICAL LEADERSHIP",    "heading": "<SECTION 1 HEADING>", "body": "..."},  # ~140 words
        {"find": "ARCHITECTURE & DELIVERY", "heading": "<SECTION 2 HEADING>", "body": "..."},  # ~140 words
        {"find": "TECHNICAL DEPTH",         "heading": "TECHNICAL DEPTH",     "body": "..."},  # ~170 words
        {"find": "WHY I ADD VALUE",         "heading": "WHY <COMPANY>",       "body": "..."},  # ~125 words
    ],

    "closing": "...",   # ~45 words: invitation to discuss, brief restatement of fit
}
```

**Inline bold markup** — use `**CompanyName**` in config strings to bold company names in the output. Builder (`set_text()`) parses `**text**` into bold runs. Apply to employer names (`**Ericsson**`, `**Telstra**`, `**Australian Private Networks**`) and target company name throughout cover letter and exec profile. Bold first mention per section, avoid over-bolding.

**Filename abbreviation convention**: take initial caps of each word in the role slug, e.g. `senior-network-engineering-manager` → `SNEM`.

**Source templates** (read-only, do not edit):
- `04-resumes/resume/Resume_v5.docx` — resume template
- `04-resumes/cover-letter/Cover_Letter_v5.docx` — cover letter template

### 9. Run the orchestrator (docx only, no PDF, no capability overview)

From the career repo root:

```bash
python 04-resumes/scripts/build_role.py <company-slug> <role-slug>
```

This produces exactly three docx deliverables in `01-jobs/<stage>/<company>/<role>/generated/`:
- `Malik_Ahmad_Resume_<Company>_<Slug>.docx`
- `Malik_Ahmad_Cover_Letter_<Company>_<Slug>.docx`
- `Malik_Ahmad_Workday_Profile_<Company>_<Slug>.docx` (derived from the resume docx)

No PDF. No capability overview. Do **not** pass `--pdf` or `--include-capability` at this phase.

The legacy `build_resume.py` and `build_cover_letter.py` scripts remain usable for partial rebuilds or debugging, but the orchestrator is the standard Phase 2 path.

### 10. **PHASE 2 GATE — stop and ask for approval**

State clearly to the user:

> Phase 2 complete. The three docx deliverables are in `<generated/ path>`. **Please review the docx layout and content** (open each in Word/Preview to check). Reply "produce PDFs" to convert to PDF via Microsoft Word, or describe any changes to iterate on the configs.

**Do not proceed to Phase 3 until the user explicitly asks for PDFs.**

---

## PHASE 3 — PDF conversion (opt-in, requires explicit user request)

### 11. Convert to PDF via Microsoft Word

Only when the user explicitly asks for PDFs, run:

```bash
python 04-resumes/scripts/build_role.py <company> <role> --pdf
```

This rebuilds the three default docx AND converts each to PDF via Microsoft Word's AppleScript engine (macOS fidelity rule — AGENTS.md forbids LibreOffice, docx2pdf, pandoc, docling for this conversion).

For a single-file PDF conversion (e.g. user approves only the resume), use the shell helper:

```bash
bash 04-resumes/scripts/docx_to_pdf_word.sh <generated/path>/<file>.docx
```

### 12. Opt-in capability overview

Capability overview is **never auto-copied**. If the user explicitly asks for it, run:

```bash
python 04-resumes/scripts/build_role.py <company> <role> --include-capability [--pdf]
```

This copies the generic `04-resumes/capability/Malik_Ahmad_Technology_Capability_Overview_v2.docx` into the role's `generated/` folder with a company-tagged filename (and converts to PDF if `--pdf` is also passed).

---

## Content guidelines (apply in Phase 2 authoring)

- **Narrative balance**: Australian decade (APN, Telstra/Belong, AINS) leads everywhere. Ericsson = foundational context, not headline. Pattern: lead with what you've done in Australia, then "This is underpinned by X years at Ericsson..."
- **Telstra (Belong)**: always use "Telstra (Belong)" not "Belong (Powered by Telstra)". Highlight national scale, hundreds of thousands of subscribers.
- **Certifications**: never list CCIP, CCNP, CCDP, CCDA, JNCIS-ENT, or Ericsson ECA-IPN when CCIE Service Provider is present — diminishes the lead credential. Use "Juniper and Ericsson certifications" in prose.
- **Technical depth**: speak architecturally, not in protocol/model-number lists. 18 years = decision-making layer, not configuration layer.
- **No em dashes in prose** — strong AI-writing tell. Replace with colons (for lists), parentheses (for asides), or sentence breaks (for paired dashes). En dashes in date ranges (`Apr 2020 – Present`) are allowed. Em dashes in structural job headers (e.g. `Network & IT Manager — Australian Private Networks`) match the template and are OK.
- **No tenuous positioning triangles**: do not frame thin employer-client connections (e.g. "I worked at both of Company X's partners") as insider knowledge unless current and substantial. Reads as a stretch; will be probed.
- **Grounded WHY COMPANY**: base it on the delivery model match and what the candidate genuinely does today — not on historical employer adjacency. Specific and honest beats impressive and hollow.
- **Gap handling**: structural gaps (e.g. a must-have tech the candidate hasn't operated) are acknowledged in the assessment file but not surfaced or over-hedged in the resume/cover letter. Let the interview determine the gap's weight.
- **Optical/transport roles**: SDH = transport foundation; DCN = IP/routing (strong fit for CCIE SP); DWDM/OTN commissioning = hands-on gap. For IP/optical convergence products (e.g. Ciena WaveRouter), the IP/MPLS depth is the primary skill — frame the optical foundation as context, not full coverage.
- **Recruiter pre-call messages**: keep simple — confirm the booking, offer resume. Never surface technical gaps or fit concerns to a recruiter; those questions belong with the hiring manager.

---

## Company SCRATCHPAD template

When a new company's SCRATCHPAD does not exist, create it with this structure:

```markdown
# SCRATCHPAD — <Company>

Company-level working memory for <Company> pursuits. Updated per role activity.

<!-- KEEP: updated YYYY-MM-DD -->

---

## Current state

**Active roles: N**
- Role A — fit X/10, stage: ...
- Role B — fit Y/10, stage: ...

**Posture:** Primary target / Selective / De-prioritize (per RADAR)

---

## Roles

| Role | Req | Stage | Next action |
|---|---|---|---|
| [Role name](role-slug/) | REQ-ID | Active / not applied | ... |

---

## Open items

- [ ] Role-specific tasks

---

## Key anchors

| Item | Detail |
|---|---|
| Comp expectation | Likely band, stretch band |
| Shared narrative | Lead credential + Australian decade + capability anchors |
| Primary gap | Structural gap specific to company |

---

## Recent activity

### YYYY-MM-DD — Role X assessed
- Assessment link
- RADAR updated

---

## Next actions

- ...

---

## Memory pointers

- memory-keeper `career` channel keys: ...
- Root SCRATCHPAD: `/path/to/career/SCRATCHPAD.md`
- RADAR: `/path/to/career/01-jobs/RADAR.md`
```

Tier rules:
- Company tier owns: company-specific decisions, sessions, comp data, recruiter contacts, cross-role shared narrative, pursuit posture.
- Root SCRATCHPAD owns: portfolio snapshot (one row per role), repo-wide rules, shared tooling, capability anchors.
- Role folder owns: 17-section assessment, per-role config scripts (Phase 2), generated docs (Phase 2/3), communications (transcripts, retrospectives).

Do not duplicate content across tiers. When migrating content, move both `[x]` completed and `[ ]` open items.

---

## Interview tactics

These tactics apply whenever the user is preparing for or debriefing any recruiter call, HR screen, hiring manager round, or technical loop. They supplement the content guidelines above.

### Salary discussions
- **Flip first, disclose never first**. Prompt the candidate to ask "What band has [company] set for this role?" before disclosing current compensation. Disclose current only if pressed and only after the range is known.
- **Define personal floor before the call**, not during. No walk-away threshold means no real negotiation position.
- **Subsequent rounds**: do not re-disclose. Reference prior conversation: "I shared context with [recruiter name]; happy to discuss overall package."

### Verbal branding
- **Always "CCIE Service Provider"**, never bare "CCIE" in speech or interview prose. Applies across recruiter screens, hiring manager rounds, and technical loops.
- **Deploy prepared buzzwords deliberately**. If prep includes a company vocabulary cheat sheet, the terms must surface in the call. Unused prep is wasted prep.

### Self-rating vigilance
- **Correct recruiter framings that overstate depth**. If a recruiter proposes a self-rating number (e.g. "would you rate yourself 8/10 on X?"), qualify or correct it if the number overstates actual depth. Unchallenged framings get relayed to hiring managers as fact and surface as probe questions in later rounds.
- **Ground ratings in concrete experience**: "strong at A, basics at B, gap at C" rather than a single composite number.

### Delivery compression
- **Answer in 30 to 60 seconds by default**, not 90 to 120. Hiring managers want crisp, not comprehensive.
- **Lead with the answer, then context**, not context then answer.
- **Prepare a 30-second pitch** before every call: current role scale + lead credential + Australian decade + current technical practice.
- **Prepare a 60-second team-structure answer** for leadership roles: exact headcount, exact split (design/ops/project/NOC), promotion timeline for any middle leaders.
- **Prepare 2 to 3 structured questions** to ask before closing. Tactical questions signal preparation better than reactive ones.

### Pre-call cheat sheet structure
When asked to produce a pre-call cheat sheet for a specific role, organize by risk tier:
- **Must-memorize items** (5 max): 30-sec pitch, salary flip script, gap-deflection scripts, one-anchor "Why [Company]" statement, explicit don'ts
- **Safe vocabulary**: company product/platform names with one-line descriptors and gap-flagged risk terms with DO-NOT-CLAIM warnings
- **Tactical questions**: 2-3 prepared questions that signal research and interest

### Post-call discipline
- **Write a retrospective** alongside every interview transcript in `01-jobs/<stage>/<company>/<role>/communications/`. Filename pattern: `<call-type>-retrospective.md` (e.g. `hr-screen-retrospective.md`, `hm-round-retrospective.md`).
- **Retrospective structure**: overall verdict, strengths (with transcript line refs), leaks (with transcript line refs), critical risks for next round, recommended prep actions, key data points captured in table form.
- **Promote session-specific lessons** to repo-wide rules (in career AGENTS.md or root SCRATCHPAD) when they generalize beyond the originating company.

---

## Assessment file template

```markdown
# Job Assessment Note — <Company> — <Role Title>
Date: <YYYY-MM-DD>
Location: <City, State>
Source role: <Role Title>, <Company>
URL: <job URL>

---

## Contents

1. [Executive summary](#1-executive-summary)
2. [What <Company> actually is](#2-what-company-actually-is)
3. [What <Company> is known for](#3-what-company-is-known-for)
4. [What this role really is](#4-what-this-role-really-is)
5. [Key job requirements](#5-key-job-requirements)
6. [Fit against my background](#6-fit-against-my-background)
7. [Main mismatch / risk](#7-main-mismatch--risk)
8. [Salary view](#8-salary-view)
9. [AI / LLM impact on my career](#9-ai--llm-impact-on-my-career)
10. [<Company> vs competitors — career lens](#10-company-vs-competitors--career-lens)
11. [Interpretation of recruiter message](#11-interpretation-of-recruiter-message)
12. [What I should assume before <next step>](#12-what-i-should-assume-before-next-step)
13. [Suggested positioning for the <next step>](#13-suggested-positioning-for-the-next-step)
14. [Questions I should ask](#14-questions-i-should-ask)
15. [My current go / no-go view](#15-my-current-go--no-go-view)
16. [Final assessment](#16-final-assessment)
17. [Personal recommendation](#17-personal-recommendation)

---

## 1) Executive summary

[2–3 sentences: what kind of role is this really, overall fit verdict]

My current overall rating:
- **Role relevance:** X/10
- **Probability of top-band offer:** low / moderate / high
- **Career upside:** [one line]
- **Base salary realism:** likely AUD Xk–AUD Yk, stretch AUD Ak–AUD Bk, **AUD 250k base** [likely/unlikely]

---

## 2) What <Company> actually is

[Plain-English description: what they sell, what they build, market position]

### Plain-English explanation
They build / provide:
- [bullet]
- [bullet]

This means <Company> is closer to:
- [comparable company / category]

than to:
- [what they are NOT]

---

## 3) What <Company> is known for

[Key products, technologies, reputation]

### Important distinction
[Their AI story or tech positioning and what it means for the role]

---

## 4) What this role really is

### Best label
**[One phrase, e.g. "Post-sales customer delivery engineering manager"]**

### Why
[What the role explicitly includes — bullet list]

### Therefore

| Dimension | My read |
|---|---|
| [Dimension] | Low / Medium / High |

### Interpretation
It is **not** mainly: [what it isn't]
It is mainly: [what it is]

---

## 5) Key job requirements

### Core domain
[Technical domain requirements]

### IP/networking layer
[Protocols and technologies, if applicable]

### Leadership / execution
[People, delivery, and stakeholder requirements]

### Nice-to-haves
[Desirable but not essential]

---

## 6) Fit against my background

### Strong fit areas

#### Leadership / team / delivery
[Where background clearly maps]

#### [Domain area]
[Where background clearly maps]

---

## 7) Main mismatch / risk

[Primary gap between role needs and background]

### Risk statement
If <Company> wants [X], then I am a stretch fit.
If <Company> wants [Y], then I am more viable.

---

## 8) Salary view

[Market references for role/level in relevant city]

### Practical estimate for this role
- **Likely base:** AUD Xk–AUD Yk
- **Stretch:** AUD Ak–AUD Bk
- **AUD 250k base:** low / moderate / high probability

### Why AUD 250k base is [likely/unlikely]
[Reasoning: scope, domain fit, scarcity, commercial accountability]

---

## 9) AI / LLM impact on my career

### What happens to my recent AI/LLM passion?
[Would this role accelerate, sideline, or stay adjacent to AI/LLM ambitions]

### Why
[The company's actual AI positioning]

### What that means practically
[Day-to-day reality if joining]

### What it probably would not be
[What AI work this role would NOT offer]

### Conclusion
- **adjacent benefit / direct acceleration / sidelining**
- AI relevance rating: X/10

---

## 10) <Company> vs [Competitor A] vs [Competitor B] — career lens

### For AI/data-centre mindshare
[Ranked list]

### For [other relevant dimension]
[Ranked list]

### Meaning
[What each option offers]

### Career implication for me
[What this company helps vs what others may offer better]

---

## 11) Interpretation of recruiter message

[What the outreach emphasized and what that signals]
[What this confirms about the role's real nature]

---

## 12) What I should assume before <next step>

### Likely reality
[What they will test / probe]

### Likely concern from their side
"[The gating question they likely have about my fit]"

---

## 13) Suggested positioning for the <next step>

### Core positioning
[How to frame the background for this specific role]

### Important caution
[What not to overclaim]

[Better approach: honest framing strategy]

---

## 14) Questions I should ask

1. Is this role primarily [X] or does it also carry [Y]?
2. What percentage of the role is: [breakdown]
3. How critical is [key domain depth] versus [broader strength]?
4. Is the team mainly: [options]
5. Does the role own: [scope items]
6. What is the geographic scope?
7. How much exposure does the role have to AI/automation/[relevant theme]?
8. What is the compensation range for the role?

---

## 15) My current go / no-go view

### Reasons to continue
[Bulleted]

### Reasons to be cautious
[Bulleted]

### Current decision posture
**[One sentence: proceed / hold / pass + framing]**

---

## 16) Final assessment

### Best short summary
[2–3 sentences: what the company is, what the role really is, fit summary, key risk, salary verdict]

---

## 17) Personal recommendation

My recommendation:
- [action item]
- [what to test]
- only pursue seriously if:
  - [condition 1]
  - [condition 2]
  - [condition 3]
```

---

## Formatting rules

- **Currency**: always `AUD Xk` format (e.g. `AUD 190k`, `AUD 220k–AUD 250k`) — dollar signs break math rendering in VS Code preview
- **TOC**: always include after the header block, anchor links lowercase with hyphens
- **Heading levels**: `##` for numbered sections, `###` for subsections, `####` for sub-subsections
- **Tables**: use for dimension ratings and competitor comparisons
- **Bold**: key verdicts, credentials, and role descriptors — not every term
- **No citations**: do not include `[oai_citation:...]` or inline source markers

## Career repo path

```
/Volumes/Data/_ai/_project/project_stuff/me/career/
├── 01-jobs/
│   ├── RADAR.md                     ← single-pane tracker; update on every stage change
│   ├── _template/
│   │   └── job-assessment-template.md   ← canonical 17-section template; copy and fill
│   ├── 00-jobspy-outcomes/
│   │   ├── TRACKER.md               ← aggregate cross-run view; rebuild after every new run
│   │   └── <YYYYMMDD>-<location>/   ← per-run archive
│   ├── 01-active/
│   │   └── <company>/
│   │       └── <role-slug>/
│   │           ├── <company>-<role-slug>.md     ← assessment file (Phase 1)
│   │           ├── scripts/                     ← config scripts (Phase 2)
│   │           │   ├── resume_config.py
│   │           │   └── cover_letter_config.py
│   │           └── generated/                   ← built docx + optional PDF (Phase 2/3)
│   ├── 02-applied/
│   ├── 03-interview/
│   ├── 04-rejected/
│   └── 05-archived/
├── 02-capability/
│   └── core_strengths.md             ← live capability source of truth; read for current anchors
├── 03-positioning/
└── 04-resumes/
    ├── resume/Resume_v5.docx
    ├── cover-letter/Cover_Letter_v5.docx
    ├── capability/Malik_Ahmad_Technology_Capability_Overview_v2.docx  ← opt-in only
    └── scripts/
        ├── build_role.py             ← Phase 2/3 orchestrator
        ├── build_resume.py           ← legacy per-doc, still usable
        ├── build_cover_letter.py     ← legacy per-doc, still usable
        ├── build_workday_docx.py     ← Workday profile derivation
        ├── pdf_export.py             ← Word AppleScript PDF engine
        ├── docx_to_pdf_word.sh       ← standalone PDF helper
        ├── docx_builder.py           ← library
        ├── CONFIG_CONTRACT.md        ← authoring contract (authoritative)
        └── index.md                  ← resume index
```
