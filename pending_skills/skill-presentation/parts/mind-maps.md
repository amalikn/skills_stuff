# Mind maps: markmap markdown for a one-glance view

## Scope

A mind map is a deliverable form of this skill: a one-glance executive view of a decision, a plan or a data breakdown, kept as plain markdown so it is readable without a tool and renders as an interactive map
in a markmap viewer. The operator builds two kinds: **data mind maps** generated from a table (profit and loss by speed tier or product, scenario comparisons, an enriched view with cost pools) and **plan mind maps**
written by hand (the target of a project, its questions and work plan, progress). This reference gives the form, the rules and how to generate and review one.

## Contents of this reference

- [The markmap form](#the-markmap-form)
- [Data mind map](#data-mind-map)
- [Plan mind map](#plan-mind-map)
- [The four-lens mind map](#the-four-lens-mind-map)
- [Generating from data](#generating-from-data)
- [Rules](#rules)
- [Rendering and review](#rendering-and-review)

## The markmap form

Headings are the branches and bullets are the leaves: `#` the root, `##` the main branches, `###` to `#####` deeper nodes, `-` bullets for evidence. Bold marks the figure that matters. A map is one file,
`<slug>-YYYYMMDD_hhmm.md`, in the project's `docs/reports/mindmaps/`.

## Data mind map

Shape (from the operator's enriched profitability maps, read 2026-11-12):

1. `#` one line that states the headline: the margin, the profit per month and a status icon.
2. A blockquote with the base facts (services, revenue, profit) and the cost basis (what is included: direct costs and the shared infrastructure pools).
3. A legend line: the icon for at or above the portfolio average, the icon for below a stated threshold.
4. `---` between blocks; `##` sections with a status icon: Snapshot, Strong performers (at or above average), then the groups below the threshold.
5. One `#####` node per group: icon, group name, its margin, and the difference to the portfolio average in points; under it bullets with the count, revenue, cost split as a share of revenue, and the bolded profit.

The headline and the legend carry the answer; the nodes are the evidence. Figures come from the data file, never typed; the basis and the month are named in the map.

## Plan mind map

Hand-written, same markmap form: `#` the project, `##` the problem (with the headline figures), `##` the questions the audience asked (numbered `###`), `##` the work plan (numbered `###`), bullets as evidence, bold for the
headline figure. Keep to what the audience asked and what is being done; no narration of meetings.

## The four-lens mind map

For any initiative or decision (see lenses-and-translation.md): the root is the decision or ask; the four branches are Business, Technical, Financial, Management. Under each branch, one line per item in the
translation chain; an unknown is a leaf marked `GAP: <reason and owner>` and never an empty branch. Start from `templates/lens-mindmap.md`. It is the quickest way to show that all four views are covered, and a
reviewer can see a missing branch at a glance.

## Generating from data

`mindmap_render.py` (promoted from the profitability projects' generic generator): reads a table (parquet or csv), detects the column schema of the project, groups by one or more dimensions, computes the portfolio
average and the difference in points, and writes the markmap to the mind map folder and stdout. Plan by default; `--apply` writes. Inputs and the basis are stated on the command line; the output name carries the stamp.
Run the archive step (analysis-workbooks.md, archiving) after a new version is written.

## Rules

- The map states its basis, month and as-at date; every number traces to the data file.
- Status icons always come with the legend and the threshold; colour or icon is never the only signal for a figure (also write the margin).
- No invented values; an unknown is a `GAP` leaf.
- One map answers one question; split a second question into a second map.
- Superseded versions move to `archive/` beside the folder during a sweep; only the latest of each map stays active.

## Rendering and review

Open the markdown in a markmap viewer (a VS Code extension or the markmap command line; neither was verified in this research) and look at it: is the headline readable at a glance, are the strongest and weakest groups
findable in three seconds, do any nodes wrap badly. Review the plain markdown too, since that is what is committed. Fix the generator, not the output.
