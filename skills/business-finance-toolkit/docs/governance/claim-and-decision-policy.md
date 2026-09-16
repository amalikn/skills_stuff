# Claim, evidence, and decision policy

## Claim states

| State | Meaning | Decision use |
|---|---|---|
| `MISSING` | Required question has no usable answer. | Blocks when critical. |
| `PROPOSED` | Hypothesis or assumption awaiting evidence. | Never a verified fact. |
| `VERIFIED` | Supported by one or more recorded sources. | Can support a decision. |
| `SUPERSEDED` | Earlier information replaced by a newer record. | Do not rely on it. |

## Evidence labels

- `USER_STATED`: user-supplied context; preserve it, but do not elevate it automatically.
- `UNVERIFIED`: working assumption or unconfirmed claim.
- `VERIFIED_PRIMARY`: authoritative instrument, regulator, publisher, contract, or first-party dataset was opened and recorded.
- `VERIFIED_SECONDARY`: official explanatory material or otherwise reliable contextual evidence; do not use for load-bearing statutory figures when a primary source exists.

## Required source record

Record title, URL, publisher where known, retrieval date, publication/in-force date where relevant, and a concise operative excerpt or observation. Re-check dynamic sources before a material decision.

## Gate rules

1. A critical claim that is not actionable blocks the pilot gate.
2. All actionable critical claims without a named human approval yield `READY_FOR_REVIEW`.
3. Only a human approver can produce `APPROVED`.
4. A decision memo must distinguish facts, assumptions, calculation outputs, risks, and recommendations.
5. A run manifest must identify the input hash, calculator version, claims, and artifacts used.

## Human approval rules

Skills may research, calculate, draft, and flag gaps. They may not place orders, file forms, publish listings, send external communications, or commit funds without an explicit separate approval and an authorised integration.
