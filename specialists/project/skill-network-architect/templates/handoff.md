---
Title: Bidirectional handoff template
Category: template
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: Request and response envelope between architects and specialist skills, with evidence, contract, stop conditions and review state.
---

# Handoff <REQ-ID>: <one-line request>

## How to use

- Use for every request sent to or received from the peer architect or a specialist skill (nautobot, openwisp, drawio, coder, smc, cambium, mikrotik).
- The sender fills sections 1-3; the receiver fills section 4 and returns the same request ID.
- An acknowledgment is not acceptance evidence.
- Do not send secrets or access details; reference where an authorized operator can obtain them.

## 1. Envelope

| Field                                    | Value                                                                      |
| ---------------------------------------- | -------------------------------------------------------------------------- |
| Request ID / parent ID / revision        | <REQ-ID> / <parent> / r<n>                                                 |
| Sender / recipient / coordinator         | <skill or role> / <skill or role> / <skill or role>                        |
| Mode                                     | discovery / design / review / incident / migration / automation / capacity |
| Objective                                | *The decision or artifact needed, in one sentence.*                        |
| Service scope / exclusions               | <service, site-code list> / *what the receiver must not touch*             |
| Existing authorization                   | *read-only / lab only / named targets; quote the approval*                 |
| Deadline (only if real) / runtime budget | <date> / <n> min of tool time                                              |

## 2. Evidence supplied

| Artifact           | Path or ID | Revision / timestamp | Units / population | Label            |
| ------------------ | ---------- | -------------------- | ------------------ | ---------------- |
| <inventory export> | <path>     | <YYYY-MM-DD hh:mm>   | <n> devices        | VERIFIED_PRIMARY |

- Known facts: *with label.*
- Assumptions: *each marked USER_STATED or UNVERIFIED.*
- Unknowns that block the request: *and the test that would resolve each.*

## 3. Contract

| Item                              | Value                                                                   |
| --------------------------------- | ----------------------------------------------------------------------- |
| Requested output                  | *ADR, review findings, command output, rendered diagram, code with tests* |
| Inputs owned by sender            |                                                                         |
| Outputs owned by receiver         |                                                                         |
| Interfaces and field writers      | IF-<nnn>; *which side writes which field*                               |
| Acceptance checks                 | *measurable; how the sender will verify the response*                   |
| Stop conditions                   | *e.g. target count exceeds n, write needed, unexpected device state*    |
| Response location / next reviewer | <path or thread> / <role>                                               |

## 4. Receiver response

| Item                                   | Value                                                 |
| -------------------------------------- | ----------------------------------------------------- |
| Scope accepted / narrowed (why)        |                                                       |
| Evidence gathered (path, time, label)  |                                                       |
| Decision or artifacts (path, revision) |                                                       |
| Validation performed and actual result | *static / model / lab / canary / production: say which* |
| Residual risks, missing facts          |                                                       |
| Downstream effects on other owners     |                                                       |
| Next action and owner                  |                                                       |

## 5. Review state

| Revision | State    | Date | Reviewer (role) | Notes |
| -------- | -------- | ---- | --------------- | ----- |
| r1       | proposed |      |                 |       |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
