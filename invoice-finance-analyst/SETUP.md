# Setup — Invoice Finance Analyst

## Contents

- [Prerequisites](#prerequisites)
- [venv location](#venv-location)
- [Standard pipeline](#standard-pipeline)
  - [Step 1 — Validate and suggest column mapping (first run with a new CSV)](#step-1-validate-and-suggest-column-mapping-first-run-with-a-new-csv)
  - [Step 2 — Load CSVs to parquet](#step-2-load-csvs-to-parquet)
  - [Step 3 — Run reconciliation (Phase 1B)](#step-3-run-reconciliation-phase-1b)
  - [Step 4 — Run rate card and margin analysis (Phase 2)](#step-4-run-rate-card-and-margin-analysis-phase-2)
  - [Step 5 — Run trend analysis (Phase 3, optional — requires prior period CSVs)](#step-5-run-trend-analysis-phase-3-optional-requires-prior-period-csvs)
  - [Step 6 — Generate LLM analyst report (Phase 4)](#step-6-generate-llm-analyst-report-phase-4)
- [Running tests](#running-tests)
- [CLI flag reference](#cli-flag-reference)
- [Invoking the skill in Claude Code](#invoking-the-skill-in-claude-code)
- [Invoking the skill in Codex](#invoking-the-skill-in-codex)
- [Local LLM usage](#local-llm-usage)
- [Runtime state](#runtime-state)

---

## Prerequisites

- Python 3.14.4: `/opt/homebrew/opt/python@3.14/bin/python3.14`
- pandas, openpyxl (for Excel output), pytest (for tests)

## venv location

Per skills_stuff venv routing policy, the venv lives outside this source folder:

```
/Volumes/Data/_ai/_skills/skills-working-cache/invoice-finance-analyst/venv/
```

Create:
```bash
/opt/homebrew/opt/python@3.14/bin/python3.14 -m venv \
  /Volumes/Data/_ai/_skills/skills-working-cache/invoice-finance-analyst/venv
```

Activate:
```bash
source /Volumes/Data/_ai/_skills/skills-working-cache/invoice-finance-analyst/venv/bin/activate
```

Install dependencies:
```bash
pip install pandas pyarrow openpyxl pytest pyyaml tabulate openai
```

## Standard pipeline

### Step 1 — Validate and suggest column mapping (first run with a new CSV)

```bash
python scripts/validate_inputs.py --csv invoice.csv --suggest-mapping --source-type supplier_invoice
# Edit the printed YAML, save as mapping_supplier_invoice.yaml, then:
python scripts/validate_inputs.py --csv invoice.csv --mapping mapping_supplier_invoice.yaml
```

### Step 2 — Load CSVs to parquet

```bash
python scripts/load_inputs.py --csv invoice.csv   --mapping mapping_supplier_invoice.yaml --name invoice
python scripts/load_inputs.py --csv sales.csv     --mapping mapping_sales_billing.yaml    --name sales_billing
python scripts/load_inputs.py --csv rate_card.csv --mapping mapping_rate_card.yaml        --name rate_card
# Optional:
python scripts/load_inputs.py --csv service_map.csv --mapping mapping_service_map.yaml   --name service_map
```

Parquets written to `db/` with snappy compression. Current file + 2 most-recent archives kept.

### Step 3 — Run reconciliation (Phase 1B)

```bash
python scripts/invoice_analysis_skeleton.py
# → 9 parquet tables in db/ + 9 markdown files in output/<run_id>/
```

### Step 4 — Run rate card and margin analysis (Phase 2)

```bash
python scripts/rate_card_analysis.py
# → 6 parquet tables in db/ + 6 markdown files in output/phase2_<run_id>/
```

### Step 5 — Run trend analysis (Phase 3, optional — requires prior period CSVs)

```bash
# Load prior period first
python scripts/load_inputs.py --csv prior_invoice.csv --mapping mapping_supplier_invoice.yaml --name prior_invoice
python scripts/load_inputs.py --csv prior_sales.csv   --mapping mapping_sales_billing.yaml   --name prior_sales_billing

python scripts/trend_analysis.py
# → 7 parquet tables in db/ + 7 markdown files in output/phase3_<run_id>/
```

### Step 6 — Generate LLM analyst report (Phase 4)

```bash
# OpenAI (default — requires OPENAI_API_KEY)
python scripts/llm_analyst.py

# DeepSeek
OPENAI_BASE_URL=https://api.deepseek.com OPENAI_API_KEY=sk-... \
    python scripts/llm_analyst.py --model deepseek-chat

# Ollama (local, no key needed)
OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama \
    python scripts/llm_analyst.py --model llama3.2

# → output/phase4_<run_id>/analyst_report.md
```

## Running tests

**Always use the venv-explicit command** — bare `pytest tests/` uses ambient Python and will fail (missing tabulate, pyarrow, etc.):

```bash
/Volumes/Data/_ai/_skills/skills-working-cache/invoice-finance-analyst/venv/bin/pytest tests/
# 219 tests — 5 modules (validate_inputs, reconciliation, rate_card_analysis, trend_analysis, llm_analyst)
```

Or activate the venv first:
```bash
source /Volumes/Data/_ai/_skills/skills-working-cache/invoice-finance-analyst/venv/bin/activate
pytest tests/
```

## CLI flag reference

All scripts default to `db/` for parquet inputs and `output/<run_id>/` for outputs unless overridden.

### validate_inputs.py

| Flag | Default | Description |
|---|---|---|
| `--csv` | *(required)* | Path to source CSV file |
| `--mapping` | — | Path to mapping.yaml |
| `--suggest-mapping` | false | Print suggested YAML mapping and exit |
| `--source-type` | `supplier_invoice` | Schema to validate against |
| `--json` | false | Output result as JSON |

### load_inputs.py

| Flag | Default | Description |
|---|---|---|
| `--csv` | *(required)* | Path to source CSV |
| `--mapping` | — | Path to mapping.yaml |
| `--name` | CSV filename stem | Parquet output stem name |
| `--db` | `db/` | Override db/ directory path |
| `--quiet` | false | Suppress console output |

### invoice_analysis_skeleton.py

| Flag | Default | Description |
|---|---|---|
| `--invoice` | `db/invoice.parquet` | Path to invoice parquet |
| `--sales` | `db/sales_billing.parquet` | Path to sales parquet |
| `--output-dir` | `output/<run_id>/` | Override output directory |

### rate_card_analysis.py

| Flag | Default | Description |
|---|---|---|
| `--matched` | `db/matched_lines.parquet` | Path to matched_lines parquet |
| `--rate-card` | `db/rate_card.parquet` | Path to rate_card parquet |
| `--output-dir` | `output/phase2_<run_id>/` | Override output directory |

### trend_analysis.py

| Flag | Default | Description |
|---|---|---|
| `--invoice` | `db/invoice.parquet` | Current period invoice |
| `--prior-invoice` | `db/prior_invoice.parquet` | Prior period invoice |
| `--sales` | `db/sales_billing.parquet` | Current period sales |
| `--prior-sales` | `db/prior_sales_billing.parquet` | Prior period sales |
| `--matched` | `db/matched_lines.parquet` | Matched lines |
| `--output-dir` | `output/phase3_<run_id>/` | Override output directory |

### llm_analyst.py

| Flag | Env var override | Default | Description |
|---|---|---|---|
| `--model` | `INVOICE_MODEL` | `gpt-4o-mini` | Model name (e.g. deepseek-chat, llama3.2) |
| `--base-url` | `OPENAI_BASE_URL` | OpenAI | Provider API base URL |
| `--api-key` | `OPENAI_API_KEY` | — | Provider API key |
| `--output-dir` | — | `output/phase4_<run_id>/` | Override output directory |

---

## Invoking the skill in Claude Code

```
Use the internal-invoice-analysis skill.

Analyze only the supplied CSV files. Do not use external financial, market,
inflation, CPI, benchmark, or internet data.

Files:
- invoices: [path]
- sales: [path]
- rate_card: [path]  (optional)
```

## Invoking the skill in Codex

Same prompt pattern as Claude Code. The skill is agent-agnostic — install SKILL.md to the relevant skills path for each agent.

Install path for Claude Code:
```
~/.claude/skills/internal-invoice-analysis/SKILL.md
```

Install path for Codex:
```
~/.codex/skills/internal-invoice-analysis/SKILL.md
```

## Local LLM usage

For local LLM agents that support skill/system-prompt injection:
- Inject `SKILL.md` as the system prompt.
- Run `scripts/validate_inputs.py` and `scripts/invoice_analysis_skeleton.py` first to produce calculated outputs.
- Feed the calculated markdown summary tables to the LLM, not raw unbounded CSVs.

## Runtime state

Ephemeral runtime state (logs, pid files) goes under:
```
/Volumes/Data/_ai/_skills/skills-runtime/invoice-finance-analyst/
```
