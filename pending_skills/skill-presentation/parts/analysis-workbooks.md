# Analysis, profitability and scenario workbooks

## Scope

The operator's analysis workbooks (carrier and fibre profitability, cost cutting, site and wear analyses) follow a settled convention. This reference states it so a new workbook, a scenario or a refresh matches
the existing ones, and covers recalculation, error scanning and archiving. General spreadsheet mechanics are in spreadsheets.md.

## Contents of this reference

- [The convention](#the-convention)
- [Sheet layout](#sheet-layout)
- [Scenarios and what-ifs](#scenarios-and-what-ifs)
- [Files, names and archiving](#files-names-and-archiving)
- [Build, recalculate, scan](#build-recalculate-scan)
- [Audience](#audience)

## The convention

(From the profitability projects' workbooks and generator scripts, read 2026-11-12.)

1. **Basis in the name.** A workbook states which basis it is built on (for example base direct costs only, or enriched with the shared infrastructure pools) in its file name and on the sheet.
2. **One timestamped file per run:** `<slug>-<period>-<basis>-<YYYYMMDD_hhmm>.xlsx`; the period (month or quarter) is in the name.
3. **Snake_case data columns** (`speed_tier`, `service_count`, `revenue_total`); one row per group, one sheet per period where several periods exist.
4. **A top block** with the title, the period and the headline figures.
5. **An Exclusions and Assumptions block** (one labelled assumption per row, near the top): what is excluded, what is held constant in a what-if (for example the shared costs), the pricing basis, the date of the data.
6. **A column glossary:** every derived column has a note in the form `[FORMULA] = <definition>` with its meaning and sign (for example the profit delta, where positive means improvement under the scenario).
7. **Costs split** into direct costs and shared pools (backhaul, internet, data centre), each as a share of revenue.
8. **Formulas, not pasted totals** for derived columns where the workbook is meant to be read and tweaked; values only where the generator writes a snapshot, and then the glossary says so.
9. **One canonical file** is named in the project's AGENTS.md; an older sibling is explicitly not canonical.

## Sheet layout

Title and period (top left); headline figures; Exclusions and Assumptions; the data table with frozen header row and widths set; the column glossary below or on its own sheet; a summary sheet first when the workbook has
more than one table. See `templates/analysis-workbook-notes.md`.

## Scenarios and what-ifs

A scenario workbook holds the baseline, the hypothetical and the delta side by side (for example the current rate card, a new rate card, and the delta profit), with the assumptions block saying what moves and what is
held constant. A three-way comparison (baseline, new pricing, new pricing plus negotiated cost reductions) uses proportional scaling stated in the assumptions. Label the what-if in the file name and the sheet title.

## Files, names and archiving

Dated outputs follow the operator's archive rule (added 2026-06-05): during every sweep, move superseded files with an older `_YYYYMMDD_hhmm` on the same slug (md, xlsx, csv) into an `archive/` folder beside them,
keep only the latest of each report type in the active folder, update the reports README and the routing notes, and add a CHANGELOG entry. Do not archive static anchor files, audit and reconciliation files,
unique-slug files or anything already in an archive folder. `archive_dated.py` plans the moves and writes only with `--apply`; it never deletes.

## Build, recalculate, scan

Build with a script that reads the data file (never retype numbers). Recalculate headlessly and scan for `#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A` and `#NAME?` using the recalculation JSON, not the exit code (see
spreadsheets.md). Spot-check two or three formulas by hand: a clean recalculation does not prove the ranges are right. Open the file once in Excel and look at it.

## Audience

Finance and commercial readers: lead with the headline and the basis; the four lenses apply (the business reading, the financial effect, the technical driver, the decision); the assumptions block is for the
sceptical reader, so keep it honest and short. A mind map of the same result (mind-maps.md) is the executive view.
