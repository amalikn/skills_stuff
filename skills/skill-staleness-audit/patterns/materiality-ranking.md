# Materiality ranking

<!-- claim-scan:examples reason="names filenames as examples of a class, not as references" -->

How to rank findings, and why ranking **before** fixing changes the outcome rather than merely the order.

## Contents

- [The three bands](#the-three-bands)
- [Why rank before fixing](#why-rank-before-fixing)
- [Latent versus realised](#latent-versus-realised)
- [Deciding the band](#deciding-the-band)
- [Worked examples](#worked-examples)

---

## The three bands

| Band | Meaning | Test |
|---|---|---|
| **M** | Could cost money or mislead a third party | Would acting on this move cash, or does it appear in something sent outside the project? |
| **H** | Enforcement hole | Is there a check that *cannot* fail, or a guard with a blind spot? |
| **G** | Governance drift | Stale counts, dates, indexes, routing — wrong, but nobody loses anything by it |

**H sits above G deliberately.** An enforcement hole is not a defect in the corpus; it is a defect in the thing that was supposed to find defects, so it silently multiplies. The gate-phrase guard that
matched only one word order was band H, and it had been concealing two band-M defects for a full day.

## Why rank before fixing

Working in file order is the default and it is wrong, for three reasons:

1. **The expensive findings get buried.** In the audited project, a stale historical figure in `docs/03` sorted ahead of a cash-flow generator in `scripts/` — alphabetically and in every directory
   listing. The first was history. The second was printing a superseded gate into a licence application.
2. **Audits get interrupted.** If the run stops at 60%, ranking decides whether the remaining 40% is cosmetic or catastrophic. This is the entire argument, and it only works if the ranking happened
   first.
3. **It forces the materiality question early**, while you still have the evidence in front of you. Asked later, it degrades into "how hard is this to fix", which is a different question with a
   different answer.

## Latent versus realised

A band-M finding is not automatically a realised loss, and conflating the two destroys the report's credibility in both directions — it either cries wolf or buries a live problem.

State plainly which it is:

> **No filed figure was wrong.** On both kei presets the dollar limb binds under the old and new gate alike, so the verdicts are identical — verified by regeneration. The exposure was **latent**: the
> dollar limb only stops binding above $16,667 landed, so on any larger vehicle the old line would have printed CLEARS for a candidate that fails.

That paragraph does three things at once: it refuses to overstate, it proves the claim by re-running rather than reasoning, and it names the exact condition under which the defect becomes real. A
reader can act on it.

**Never round a latent defect up to a realised one to make the audit look valuable.** The next reader calibrates on you.

## Deciding the band

Work down; first match wins.

1. Does it appear in a document that leaves the project — a filing, an application, a quote, a client report? → **M**
2. Would acting on it move money — a bid ceiling, a price, a purchase verdict, a budget? → **M**
3. Does it feed a decision gate, even indirectly through an input? → **M**
4. Is it a check, guard, or validation that cannot fail or has a blind spot? → **H**
5. Is it a registry, catalog or enforcement list maintained by hand? → **H** (they drift exactly like the claims they police)
6. Otherwise → **G**

**When genuinely torn between M and G, choose M.** The cost of over-ranking is a paragraph of the operator's attention; the cost of under-ranking is the thing you were hired to prevent.

## Worked examples

| Finding | Band | Reasoning |
|---|---|---|
| Cash-flow generator prints a superseded gate into a licence-application working paper | **M** | Leaves the project; latent wrong verdict above $16,667 landed |
| Business plan states the purchase gates as a half-set | **M** | Filed with a licensing authority; a half-set reads as complete |
| Max-bid back-solved against a flat target the gate outgrew | **M** | The number an operator carries into a live auction |
| Class verdict in YAML still `RECOMMENDED` after reversal | **M** | Tools return it; it is a purchase recommendation |
| Preset carries a purchase price the evidence disproved | **M** | Feeds every downstream figure |
| Gate-phrase guard matches only one word order | **H** | Concealed two band-M defects for a day |
| Count check scans four hand-listed files | **H** | Passed clean while five surfaces went unexamined |
| Source capture reformatted by a hook | **H** | Evidence integrity; nothing could detect a substantive edit |
| Project asserts 39 / 57 checks when the answer is 56 | **G** | Costs nothing directly — but see below |
| `docs/README` snapshot date three days stale | **G** | Misleading, not costly |
| Routing row points cap question at a superseded review | **G** | Sends a reader to the wrong document; recoverable |

**The count example is worth dwelling on**, because it is the one most often waved through. It is correctly band G — no money moves. But the reasoning for fixing it is not "tidiness": a reader who
notices that 39 ≠ 57 learns that the project's stated figures cannot be trusted, and **that doubt does not stay confined to the count**. In a corpus whose entire method is "the documents agree,
therefore the figures are reliable", a visibly self-contradictory number is corrosive out of all proportion to its size.

Rank it G. Fix it anyway. Say why in the report.
