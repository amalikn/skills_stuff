# Gate model — why gates work the way they do

Read this when a gate decision is contested, when you are tempted to close a gate with a plausible neighbour, or when changing the gate contract.

## A gate is an obligation on the ROUTE, not an instruction to add a persona

`default_persona` names who would carry the capability *if a persona were needed*. It is not an instruction that one is. Gate-driven persona inflation is a routing failure in its own right, and the
`direct-adversarial` eval family exists to catch it.

A gate already satisfied is met: if `critic-munger` is already the primary owner, `critic_required` is satisfied — a second challenger adds nothing.

## Why `supporting` never discharges a gate

A supporting capability is incidental to that provider's purpose. Treating it as sufficient is how ordinary analysis quietly starts counting as independent challenge, which destroys the one property
the critic gate exists to provide.

**Check the declaration, not the resemblance.** The commonest failure is closing a gate with an adjacent capability:

- `financial-unit-economics` does not provide `research` — it analyses assumptions you already hold.
- `deep-analysis` does not provide `independent-challenge` — it examines what is in front of it.
- `security-audit` and `senior-qa` are validation, not challenge.

On the 2026-09-01 baseline this single mistake accounted for **every one of the 22 gate failures**: the gate was judged correctly, then closed with something adjacent or with nothing at all.

## Why no gate's persona is unconditionally mandatory

An earlier revision made `critic_required` summon `critic-munger` always. It was rejected on evidence: it would force a persona onto "check the vendor docs for feature X", where a CTO plus a research
skill suffices. Escalation is now per-gate and tag-driven, which is why reporting the task's characteristics matters more than it looks.

## Why closure is code, not instruction

Stating closure as a prompt instruction moved **nothing** across three different models (baseline v3, a valid negative result). Running it as a program moved the corpus from **34/60 to 47/60** with
zero regressions. Where a rule is a lookup against a finite catalogue, a program does it exactly and a model does it sometimes.

Every published figure for this router was produced with closure in the loop, including 84% on the unseen holdout. The same holdout without it scored **40–50%** on three different models.

## Gate flags are currently advisory in real use

Measured across every stored run: predicted-positive rate **1.00 on all four gates** in integrated routing, while the same model judging gates in isolation produces a real classifier (PPR ≈ base rate)
on two independent arms. So the definitions are learnable; judging them *while* constructing a route destroys the signal.

The collapse is **not costing routing accuracy** — over-assertion measured 30% failure against a 17% baseline (n=10, no signal), while under-assertion is fatal at 14/14. Production makes only the
harmless error. It costs tokens, team size, and the operator's trust in the flag.

**Therefore: never trade gate precision for recall.** That swaps a free error for a fatal one. See [rule 0012](../../../.archcore/rules/0012-gate-flags-are-advisory-until-localised.md).
