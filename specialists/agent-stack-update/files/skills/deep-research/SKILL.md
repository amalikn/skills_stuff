---
name: deep-research
description: Conduct enterprise-grade research with multi-source synthesis, citation tracking, and verification. Use when user needs comprehensive analysis requiring 10+ sources, verified claims, or comparison of approaches. Triggers include "deep research", "comprehensive analysis", "research report", "compare X vs Y", or "analyze trends". Do NOT use for simple lookups, debugging, or questions answerable with 1-2 searches.
---

# Deep Research

<!-- STATIC CONTEXT BLOCK START - Optimized for prompt caching -->
<!-- All static instructions, methodology, and templates below this line -->
<!-- Dynamic content (user queries, results) added after this block -->

## Core System Instructions

**Purpose:** Deliver citation-backed, verified research reports through 8-phase pipeline (Scope → Plan → Retrieve → Triangulate → Synthesize → Critique → Refine → Package) with source credibility scoring and progressive context management.

**Context Strategy:** This skill uses 2025 context engineering best practices:
- Static instructions cached (this section)
- Progressive disclosure (load references only when needed)
- Avoid "loss in the middle" (critical info at start/end, not buried)
- Explicit section markers for context navigation

---

## Decision Tree (Execute First)

```
Request Analysis
├─ Simple lookup? → STOP: Use WebSearch, not this skill
├─ Debugging? → STOP: Use standard tools, not this skill
└─ Complex analysis needed? → CONTINUE

Mode Selection
├─ Initial exploration? → quick (3 phases, 2-5 min)
├─ Standard research? → standard (6 phases, 5-10 min) [DEFAULT]
├─ Critical decision? → deep (8 phases, 10-20 min)
└─ Comprehensive review? → ultradeep (8+ phases, 20-45 min)

Execution Loop (per phase)
├─ Load phase instructions from [methodology](./reference/methodology.md#phase-N)
├─ Execute phase tasks
├─ Spawn parallel agents if applicable
└─ Update progress

Validation Gate
├─ Run `python scripts/validate_report.py --report [path]`
├─ Pass? → Deliver
└─ Fail? → Fix (max 2 attempts) → Still fails? → Escalate
```

---

## Workflow (Clarify → Plan → Act → Verify → Report)

**AUTONOMY PRINCIPLE:** This skill operates independently. Infer assumptions from query context. Only stop for critical errors or incomprehensible queries.

### 1. Clarify (Rarely Needed - Prefer Autonomy)

**DEFAULT: Proceed autonomously. Derive assumptions from query signals.**

**ONLY ask if CRITICALLY ambiguous:**
- Query is incomprehensible (e.g., "research the thing")
- Contradictory requirements (e.g., "quick 50-source ultradeep analysis")

**When in doubt: PROCEED with standard mode. User will redirect if incorrect.**

**Default assumptions:**
- Technical query → Assume technical audience
- Comparison query → Assume balanced perspective needed
- Trend query → Assume recent 1-2 years unless specified
- Standard mode is default for most queries

---

### 2. Plan

**Mode selection criteria:**
- **Quick** (2-5 min): Exploration, broad overview, time-sensitive
- **Standard** (5-10 min): Most use cases, balanced depth/speed [DEFAULT]
- **Deep** (10-20 min): Important decisions, need thorough verification
- **UltraDeep** (20-45 min): Critical analysis, maximum rigor

**Announce plan and execute:**
- Briefly state: selected mode, estimated time, number of sources
- Example: "Starting standard mode research (5-10 min, 15-30 sources)"
- Proceed without waiting for approval

---

### 3. Act (Phase Execution)

**All modes execute:**
- Phase 1: SCOPE - Define boundaries ([method](./reference/methodology.md#phase-1-scope))
- Phase 3: RETRIEVE - Parallel search execution (5-10 concurrent searches + agents) ([method](./reference/methodology.md#phase-3-retrieve---parallel-information-gathering))
- Phase 8: PACKAGE - Generate report using [template](./templates/report_template.md)

**Standard/Deep/UltraDeep execute:**
- Phase 2: PLAN - Strategy formulation
- Phase 4: TRIANGULATE - Verify 3+ sources per claim
- Phase 4.5: OUTLINE REFINEMENT - Adapt structure based on evidence (WebWeaver 2025) ([method](./reference/methodology.md#phase-45-outline-refinement---dynamic-evolution-webweaver-2025))
- Phase 5: SYNTHESIZE - Generate novel insights

**Deep/UltraDeep execute:**
- Phase 6: CRITIQUE - Red-team analysis
- Phase 7: REFINE - Address gaps

**Critical: Avoid "Loss in the Middle"**
- Place key findings at START and END of sections, not buried
- Use explicit headers and markers
- Structure: Summary → Details → Conclusion (not Details sandwiched)

**Progressive Context Loading:**
- Load [methodology](./reference/methodology.md) sections on-demand
- Load [template](./templates/report_template.md) only for Phase 8
- Do not inline everything - reference external files

**Anti-Hallucination Protocol (CRITICAL):**
- **Source grounding**: Every factual claim MUST cite a specific source immediately [N]
- **Clear boundaries**: Distinguish between FACTS (from sources) and SYNTHESIS (your analysis)
- **Explicit markers**: Use "According to [1]..." or "[1] reports..." for source-grounded statements
- **No speculation without labeling**: Mark inferences as "This suggests..." not "Research shows..."
- **Verify before citing**: If unsure whether source actually says X, do NOT fabricate citation
- **When uncertain**: Say "No sources found for X" rather than inventing references

**Parallel Execution Requirements (CRITICAL for Speed):**

**Phase 3 RETRIEVE - Mandatory Parallel Search:**
1. **Decompose query** into 5-10 independent search angles before ANY searches
2. **Launch ALL searches in single message** with multiple tool calls (NOT sequential)
3. **Quality threshold monitoring** for FFS pattern:
   - Track source count and avg credibility score
   - Proceed when threshold reached (mode-specific, see methodology)
   - Continue background searches for additional depth
4. **Spawn 3-5 parallel agents** using Task tool for deep-dive investigations

**Example correct execution:**
```
[Single message with 8+ parallel tool calls]
WebSearch #1: Core topic semantic
WebSearch #2: Technical keywords
WebSearch #3: Recent 2024-2025 filtered
WebSearch #4: Academic domains
WebSearch #5: Critical analysis
WebSearch #6: Industry trends
Task agent #1: Academic paper analysis
Task agent #2: Technical documentation deep dive
```

**❌ WRONG (sequential execution):**
```
WebSearch #1 → wait for results → WebSearch #2 → wait → WebSearch #3...
```

**✅ RIGHT (parallel execution):**
```
All searches + agents launched simultaneously in one message
```

---

### 4. Verify (Always Execute)

**Step 1: Citation Verification (Catches Fabricated Sources)**

```bash
python scripts/verify_citations.py --report [path]
```

**Checks:**
- DOI resolution (verifies citation actually exists)
- Title/year matching (detects mismatched metadata)
- Flags suspicious entries (2024+ without DOI, no URL, failed verification)

**If suspicious citations found:**
- Review flagged entries manually
- Remove or replace fabricated sources
- Re-run until clean

**Step 2: Structure & Quality Validation**

```bash
python scripts/validate_report.py --report [path]
```

**8 automated checks:**
1. Executive summary length (50-250 words)
2. Required sections present (+ recommended: Claims table, Counterevidence)
3. Citations formatted [1], [2], [3]
4. Bibliography matches citations
5. No placeholder text (TBD, TODO)
6. Word count reasonable (500-10000)
7. Minimum 10 sources
8. No broken internal links

**If fails:**
- Attempt 1: Auto-fix formatting/links
- Attempt 2: Manual review + correction
- After 2 failures: **STOP** → Report issues → Ask user

---

### 5. Report

**CRITICAL: Generate COMPREHENSIVE, DETAILED markdown reports**

**File and State Policy (Agent Stack Adaptation):**

- Default to returning the research result in the current interaction. Create files only when the operator requests an artifact or the active project workflow requires one.
- When files are requested, write inside the current project/workspace or another operator-approved destination. Do not default to `~/Documents` or `~/.claude/research_output`.
- Do not create hidden tracking state, continuation state, or cross-project research memory unless the project explicitly owns that state.
- Do not automatically open browsers, viewers, PDFs, or HTML.
- Generate Markdown by default. Generate HTML/PDF only when requested or required by the task.
- Use the report template when useful, but adapt structure to the operator's requested deliverable rather than forcing every format.

**File Naming Convention (when artifacts are requested):**
- Prefer `research_report_[YYYYMMDD]_[topic_slug].md` or the project's own naming convention.
- Keep all generated formats together in the operator-approved project/output directory.

**Length Requirements (UNLIMITED with Progressive Assembly):**
- Quick mode: 2,000+ words (baseline quality threshold)
- Standard mode: 4,000+ words (comprehensive analysis)
- Deep mode: 6,000+ words (thorough investigation)
- UltraDeep mode: 10,000-50,000+ words (NO UPPER LIMIT - as comprehensive as evidence warrants)

**How Unlimited Length Works:**
Progressive file assembly allows ANY report length by generating section-by-section.
Each section is written to file immediately (avoiding output token limits).
Complex topics with many findings? Generate 20, 30, 50+ findings - no constraint!

**Content Requirements:**
- Use [template](./templates/report_template.md) as exact structure
- Generate each section to APPROPRIATE depth (determined by evidence, not word targets)
- Include specific data, statistics, dates, numbers (not vague statements)
- Multiple paragraphs per finding with evidence (as many as needed)
- Each section gets focused generation attention
- DO NOT write summaries - write FULL analysis

**Writing Standards:**
- **Narrative-driven**: Write in flowing prose. Each finding tells a story with beginning (context), middle (evidence), end (implications)
- **Precision**: Every word deliberately chosen, carries intention
- **Economy**: No fluff, eliminate fancy grammar, unnecessary modifiers
- **Clarity**: Exact numbers embedded in sentences ("The study demonstrated a 23% reduction in mortality"), not isolated in bullets
- **Directness**: State findings without embellishment
- **High signal-to-noise**: Dense information, respect reader's time

**Bullet Point Policy (Anti-Fatigue Enforcement):**
- Use bullets SPARINGLY: Only for distinct lists (product names, company roster, enumerated steps)
- NEVER use bullets as primary content delivery - they fragment thinking
- Each findings section requires substantive prose paragraphs (3-5+ paragraphs minimum)
- Example: Instead of "• Market size: $2.4B" write "The global market reached $2.4 billion in 2023, driven by increasing consumer demand and regulatory tailwinds [1]."

**Anti-Fatigue Quality Check (Apply to EVERY Section):**
Before considering a section complete, verify:
- [ ] **Paragraph count**: ≥3 paragraphs for major sections (## headings)
- [ ] **Prose-first**: <20% of content is bullet points (≥80% must be flowing prose)
- [ ] **No placeholders**: Zero instances of "Content continues", "Due to length", "[Sections X-Y]"
- [ ] **Evidence-rich**: Specific data points, statistics, quotes (not vague statements)
- [ ] **Citation density**: Major claims cited within same sentence

**If ANY check fails:** Regenerate the section before moving to next.

**Source Attribution Standards (Critical for Preventing Fabrication):**
- **Immediate citation**: Every factual claim followed by [N] citation in same sentence
- **Quote sources directly**: Use "According to [1]..." or "[1] reports..." for factual statements
- **Distinguish fact from synthesis**:
  - ✅ GOOD: "Mortality decreased 23% (p<0.01) in the treatment group [1]."
  - ❌ BAD: "Studies show mortality improved significantly."
- **No vague attributions**:
  - ❌ NEVER: "Research suggests...", "Studies show...", "Experts believe..."
  - ✅ ALWAYS: "Smith et al. (2024) found..." [1], "According to FDA data..." [2]
- **Label speculation explicitly**:
  - ✅ GOOD: "This suggests a potential mechanism..." (analysis, not fact)
  - ❌ BAD: "The mechanism is..." (presented as fact without citation)
- **Admit uncertainty**:
  - ✅ GOOD: "No sources found addressing X directly."
  - ❌ BAD: Fabricating a citation to fill the gap
- **Template pattern**: "[Specific claim with numbers/data] [Citation]. [Analysis/implication]."

**Deliver to user:**
1. Executive summary (inline in chat)
2. Organized folder path (e.g., "All files saved to: ~/Documents/Psilocybin_Research_20251104/")
3. Confirmation of all three formats generated:
   - Markdown (source)
   - HTML (McKinsey-style, opened in browser)
   - PDF (professional print, opened in viewer)
4. Source quality assessment summary (source count)
5. Next steps (if relevant)

**Generation Workflow: Progressive File Assembly (Unlimited Length)**

**Phase 8.1: Setup**
```bash
# Extract topic slug from research question
# Create folder: ~/Documents/[TopicName]_Research_[YYYYMMDD]/
mkdir -p ~/Documents/[folder_name]

# Create initial markdown file with frontmatter
# File path: [folder]/research_report_[YYYYMMDD]_[slug].md
```

**Phase 8.2: Progressive Section Generation**

**CRITICAL STRATEGY:** Generate and write each section individually to file using Write/Edit tools.
This allows unlimited report length while keeping each generation manageable.

**OUTPUT TOKEN LIMIT SAFEGUARD (CRITICAL - Claude Code Default: 32K):**

Claude Code default limit: 32,000 output tokens (≈24,000 words total per skill execution)
This is a HARD LIMIT and cannot be changed within the skill.

**What this means:**
- Total output (your text + all tool call content) must be <32,000 tokens
- 32,000 tokens ≈ 24,000 words max
- Leave safety margin: Target ≤20,000 words total output

**Realistic report sizes per mode:**
- Quick mode: 2,000-4,000 words ✅ (well under limit)
- Standard mode: 4,000-8,000 words ✅ (comfortably under limit)
- Deep mode: 8,000-15,000 words ✅ (achievable with care)
- UltraDeep mode: 15,000-20,000 words ⚠️ (at limit, monitor closely)

**For reports >20,000 words:**
User must run skill multiple times:
- Run 1: "Generate Part 1 (sections 1-6)" → saves to part1.md
- Run 2: "Generate Part 2 (sections 7-12)" → saves to part2.md
- User manually combines or asks Claude to merge files

**Auto-Continuation Strategy (TRUE Unlimited Length):**

When report exceeds 18,000 words in single run:
1. Generate sections 1-10 (stay under 18K words)
2. Save continuation state file with context preservation
3. Spawn continuation agent via Task tool
4. Continuation agent: Reads state → Generates next batch → Spawns next agent if needed
5. Chain continues recursively until complete

This achieves UNLIMITED length while respecting 32K limit per agent

**Initialize Citation Tracking:**
```
citations_used = []  # Maintain this list in working memory throughout
```

**Section Generation Loop:**

**Pattern:** Generate section content → Use Write/Edit tool with that content → Move to next section
Each Write/Edit call contains ONE section (≤2,000 words per call)

1. **Executive Summary** (200-400 words)
   - Generate section content
   - Tool: Write(file, content=frontmatter + Executive Summary)
   - Track citations used
   - Progress: "✓ Executive Summary"

2. **Introduction** (400-800 words)
   - Generate section content
   - Tool: Edit(file, old=last_line, new=old + Introduction section)
   - Track citations used
   - Progress: "✓ Introduction"

3. **Finding 1** (600-2,000 words)
   - Generate complete finding
   - Tool: Edit(file, append Finding 1)
   - Track citations used
   - Progress: "✓ Finding 1"

4. **Finding 2** (600-2,000 words)
   - Generate complete finding
   - Tool: Edit(file, append Finding 2)
   - Track citations used
   - Progress: "✓ Finding 2"

... Continue for ALL findings (each finding = one Edit tool call, ≤2,000 words)

**CRITICAL:** If you have 10 findings × 1,500 words each = 15,000 words of findings
This is OKAY because each Edit call is only 1,500 words (under 2,000 word limit per tool call)
The FILE grows to 15,000 words, but no single tool call exceeds limits

4. **Synthesis & Insights**
   - Generate: Novel insights beyond source statements (as long as needed for synthesis)
   - Tool: Edit (append to file)
   - Track: Extract citations, append to citations_used
   - Progress: "Generated Synthesis ✓"

5. **Limitations & Caveats**
   - Generate: Counterevidence, gaps, uncertainties (appropriate depth)
   - Tool: Edit (append to file)
   - Track: Extract citations, append to citations_used
   - Progress: "Generated Limitations ✓"

6. **Recommendations**
   - Generate: Immediate actions, next steps, research needs (appropriate depth)
   - Tool: Edit (append to file)
   - Track: Extract citations, append to citations_used
   - Progress: "Generated Recommendations ✓"

7. **Bibliography (CRITICAL - ALL Citations)**
   - Generate: COMPLETE bibliography with EVERY citation from citations_used list
   - Format: [1], [2], [3]... [N] - each citation gets full entry
   - Verification: Check citations_used list - if list contains [1] through [73], generate all 73 entries
   - NO ranges ([1-50]), NO placeholders ("Additional citations"), NO truncation
   - Tool: Edit (append to file)
   - Progress: "Generated Bibliography ✓ (N citations)"

8. **Methodology Appendix**
   - Generate: Research process, verification approach (appropriate depth)
   - Tool: Edit (append to file)
   - Progress: "Generated Methodology ✓"

**Phase 8.3: Bounded Continuation Policy (Agent Stack Adaptation)**

Do not spawn continuation agents or create hidden continuation state automatically. If the requested report is too large for one pass:

1. Complete the highest-value coherent portion first.
2. Preserve citation numbering and an explicit section-completion checklist in the visible/project-owned artifact when one exists.
3. Continue within the current execution only while the runtime permits and useful completion is still possible.
4. If further continuation requires another run or operator decision, stop cleanly and report exactly what remains.
5. Never create a daemon, background task, recursive agent chain, or `~/.claude/research_output/continuation_state_*` file.

**Phase 8.4: Quality Across Large Reports**

For multi-part assembly, maintain the same research question, evidence standard, citation sequence, terminology, and narrative structure. Before adding a section, review the preceding relevant material and verify that new claims are sourced and non-duplicative.

**Generate HTML (McKinsey Style)**
1. Read McKinsey template from `./templates/mckinsey_report_template.html`
2. Extract 3-4 key quantitative metrics from findings for dashboard
3. **Use Python script for MD to HTML conversion:**

   ```bash
   cd ~/.claude/skills/deep-research
   python scripts/md_to_html.py [markdown_report_path]
   ```

   The script returns two parts:
   - **Part A ({{CONTENT}}):** All sections except Bibliography, properly converted to HTML
   - **Part B ({{BIBLIOGRAPHY}}):** Bibliography section only, formatted as HTML

   **CRITICAL:** The script handles ALL conversion automatically:
   - Headers: ## → `<div class="section"><h2 class="section-title">`, ### → `<h3 class="subsection-title">`
   - Lists: Markdown bullets → `<ul><li>` with proper nesting
   - Tables: Markdown tables → `<table>` with thead/tbody
   - Paragraphs: Text wrapped in `<p>` tags
   - Bold/italic: **text** → `<strong>`, *text* → `<em>`
   - Citations: [N] preserved for tooltip conversion in step 4

4. **Add Citation Tooltips (Attribution Gradients):**
   For each [N] citation in {{CONTENT}} (not bibliography), optionally add interactive tooltips:
   ```html
   <span class="citation">[N]
     <span class="citation-tooltip">
       <div class="tooltip-title">[Source Title]</div>
       <div class="tooltip-source">[Author/Publisher]</div>
       <div class="tooltip-claim">
         <div class="tooltip-claim-label">Supports Claim:</div>
         [Extract sentence with this citation]
       </div>
     </span>
   </span>
   ```
   NOTE: This step is optional for speed. Basic [N] citations are sufficient.

5. Replace placeholders in template:
   - {{TITLE}} - Report title (extract from first ## heading in MD)
   - {{DATE}} - Generation date (YYYY-MM-DD format)
   - {{SOURCE_COUNT}} - Number of unique sources
   - {{METRICS_DASHBOARD}} - Metrics HTML from step 2
   - {{CONTENT}} - HTML from Part A (script output)
   - {{BIBLIOGRAPHY}} - HTML from Part B (script output)

6. **CRITICAL: NO EMOJIS** - Remove any emoji characters from final HTML

7. Save to: `[folder]/research_report_[YYYYMMDD]_[slug].html`

8. **Verify HTML (MANDATORY):**
   ```bash
   python scripts/verify_html.py --html [html_path] --md [md_path]
   ```
   - Check passes: Proceed to step 9
   - Check fails: Fix errors and re-run verification

9. Open in browser: `open [html_path]`

**Generate PDF**
1. Use Task tool with general-purpose agent
2. Invoke generating-pdf skill with markdown as input
3. Save to: `[folder]/research_report_[YYYYMMDD]_[slug].pdf`
4. PDF will auto-open when complete

---

## Output Contract

**Format:** Comprehensive markdown report following [template](./templates/report_template.md) EXACTLY

**Required sections (all must be detailed):**
- Executive Summary (2-3 concise paragraphs, 50-250 words)
- Introduction (2-3 paragraphs: question, scope, methodology, assumptions)
- Main Analysis (4-8 findings, each 300-500 words with citations [1], [2], [3])
- Synthesis & Insights (500-1000 words: patterns, novel insights, implications)
- Limitations & Caveats (2-3 paragraphs: gaps, assumptions, uncertainties)
- Recommendations (3-5 immediate actions, 3-5 next steps, 3-5 further research)
- **Bibliography (CRITICAL - see rules below)**
- Methodology Appendix (2-3 paragraphs: process, sources, verification)

**Bibliography Requirements (ZERO TOLERANCE - Report is UNUSABLE without complete bibliography):**
- ✅ MUST include EVERY citation [N] used in report body (if report has [1]-[50], write all 50 entries)
- ✅ Format: [N] Author/Org (Year). "Title". Publication. URL (Retrieved: Date)
- ✅ Each entry on its own line, complete with all metadata
- ❌ NO placeholders: NEVER use "[8-75] Additional citations", "...continue...", "etc.", "[Continue with sources...]"
- ❌ NO ranges: Write [3], [4], [5]... individually, NOT "[3-50]"
- ❌ NO truncation: If 30 sources cited, write all 30 entries in full
- ⚠️ Validation WILL FAIL if bibliography contains placeholders or missing citations
- ⚠️ Report is GARBAGE without complete bibliography - no way to verify claims

**Strictly Prohibited:**
- Placeholder text (TBD, TODO, [citation needed])
- Uncited major claims
- Broken links
- Missing required sections
- **Short summaries instead of detailed analysis**
- **Vague statements without specific evidence**

**Writing Standards (Critical):**
- **Narrative-driven**: Write in flowing prose with complete sentences that build understanding progressively
- **Precision**: Choose each word deliberately - every word must carry intention
- **Economy**: Eliminate fluff, unnecessary adjectives, fancy grammar
- **Clarity**: Use precise technical terms, avoid ambiguity. Embed exact numbers in sentences, not bullets
- **Directness**: State findings clearly without embellishment
- **Signal-to-noise**: High information density, respect reader's time
- **Bullet discipline**: Use bullets only for distinct lists (products, companies, steps). Default to prose paragraphs
- **Examples of precision**:
  - Bad: "significantly improved outcomes" → Good: "reduced mortality 23% (p<0.01)"
  - Bad: "several studies suggest" → Good: "5 RCTs (n=1,847) show"
  - Bad: "potentially beneficial" → Good: "increased biomarker X by 15%"
  - Bad: "• Market: $2.4B" → Good: "The market reached $2.4 billion in 2023, driven by consumer demand [1]."

**Quality gates (enforced by validator):**
- Minimum 2,000 words (standard mode)
- Average credibility score >60/100
- 3+ sources per major claim
- Clear facts vs. analysis distinction
- All sections present and detailed

---

## Error Handling & Stop Rules

**Stop immediately if:**
- 2 validation failures on same error → Pause, report, ask user
- <5 sources after exhaustive search → Report limitation, request direction
- User interrupts/changes scope → Confirm new direction

**Graceful degradation:**
- 5-10 sources → Note in limitations, proceed with extra verification
- Time constraint reached → Package partial results, document gaps
- High-priority critique issue → Address immediately

**Error format:**
```
⚠️ Issue: [Description]
📊 Context: [What was attempted]
🔍 Tried: [Resolution attempts]
💡 Options:
   1. [Option 1]
   2. [Option 2]
   3. [Option 3]
```

---

## Quality Standards (Always Enforce)

Every report must:
- 10+ sources (document if fewer)
- 3+ sources per major claim
- Executive summary <250 words
- Full citations with URLs
- Credibility assessment
- Limitations section
- Methodology documented
- No placeholders

**Priority:** Thoroughness over speed. Quality > speed.

---

## Inputs & Assumptions

**Required:**
- Research question (string)

**Optional:**
- Mode (quick/standard/deep/ultradeep)
- Time constraints
- Required perspectives/sources
- Output format

**Assumptions:**
- User requires verified, citation-backed information
- 10-50 sources available on topic
- Time investment: 5-45 minutes

---

## When to Use / NOT Use

**Use when:**
- Comprehensive analysis (10+ sources needed)
- Comparing technologies/approaches/strategies
- State-of-the-art reviews
- Multi-perspective investigation
- Technical decisions
- Market/trend analysis

**Do NOT use:**
- Simple lookups (use WebSearch)
- Debugging (use standard tools)
- 1-2 search answers
- Time-sensitive quick answers

---

## Scripts (Offline, Python stdlib only)

**Location:** `./scripts/`

- **research_engine.py** - Orchestration engine
- **validate_report.py** - Quality validation (8 checks)
- **citation_manager.py** - Citation tracking
- **source_evaluator.py** - Credibility scoring (0-100)

**No external dependencies required.**

---

## Progressive References (Load On-Demand)

**Do not inline these - reference only:**
- [Complete Methodology](./reference/methodology.md) - 8-phase details
- [Report Template](./templates/report_template.md) - Output structure
- [Quick Start](./QUICK_START.md) - Fast reference
- [Competitive Analysis](./COMPETITIVE_ANALYSIS.md) - vs OpenAI/Gemini

**Context Management:** Load files on-demand for current phase only. Do not preload all content.

---

<!-- STATIC CONTEXT BLOCK END -->
<!-- ⚡ Above content is cacheable (>1024 tokens, static) -->
<!-- 📝 Below: Dynamic content (user queries, retrieved data, generated reports) -->
<!-- This structure enables 85% latency reduction via prompt caching -->

---

## Dynamic Execution Zone

**User Query Processing:**
[User research question will be inserted here during execution]

**Retrieved Information:**
[Search results and sources will be accumulated here]

**Generated Analysis:**
[Findings, synthesis, and report content generated here]

**Note:** This section remains empty in the skill definition. Content populated during runtime only.

## Runtime / Environment

For Agent Stack-owned Python helper scripts, prefer the repository root `mise` + `.venv` environment (see `../../RUNTIME.md` from this skill directory). Do not assume globally installed Python packages and do not install global dependencies silently. If this skill has skill-local requirements, install them into an approved isolated environment and keep consumer-project dependencies under that project's control.

