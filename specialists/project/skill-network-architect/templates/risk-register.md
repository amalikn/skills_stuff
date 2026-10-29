---
Title: Risk register template
Category: template
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: Living register of design and delivery risks with scored likelihood and impact, trigger, response, owner, residual score and review dates.
---

# <scope> risk register

Based on: arc42 section 11 "Risks and Technical Debt" (https://docs.arc42.org/section-11/). Scoring scale is local to this pack.

## How to use

- A risk is an uncertain event with a consequence for a requirement; a known defect is an issue (track it as an action).
- Write each as "If <cause>, then <event>, causing <effect on REQ>".
- Score Likelihood (L) and Impact (I) 1-5 using the scale below; Score = L x I.
- Choose a response: avoid, reduce, transfer, accept (accept needs a named owner and an expiry date).
- Every risk has a trigger: an observable signal that it is happening now.
- Review open risks at each design revision and before each change wave.

| Score | Likelihood (in the review horizon) | Impact                                                          |
| ----- | ---------------------------------- | --------------------------------------------------------------- |
| 1     | rare, < 5%                         | no user effect                                                  |
| 2     | unlikely, 5-25%                    | brief degradation, one site or host                             |
| 3     | possible, 25-50%                   | outage of one site or service, within RTO                       |
| 4     | likely, 50-80%                     | multi-site outage or RTO missed                                 |
| 5     | almost certain, > 80%              | fleet-wide outage, data loss beyond RPO, safety or legal breach |

## 1. Register

| ID | Risk statement (if / then / causing) | REQ affected | L | I | Score | Trigger (observable) | Response | Mitigation actions | Owner | Residual L x I | Review date | Status | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RSK-01 | If <secondary path shares duct>, | REQ-01 | 3 | 4 | 12 | both links down | reduce | survey path; order | <role> | 1 x 4 | <date> | open | UNVERIFIED |
|  |   then <one cut takes both>, causing |  |  |  |  |   within 60 s |  |   diverse carrier |  |  |  |  |  |
|  |   <site outage beyond RTO> |  |  |  |  |  |  |  |  |  |  |  |  |
| RSK-02 | If <vendor EOL before refresh>, then | REQ-07 |  |  |  | EOL notice published |  |  |  |  |  |  |  |
|  |   <no security fixes>, causing |  |  |  |  |  |  |  |  |  |  |  |  |
|  |   <REQ-07 breach> |  |  |  |  |  |  |  |  |  |  |  |  |
| RSK-03 | If <single operator holds the | REQ-04 |  |  |  |  |  |  |  |  |  |  |  |
|  |   procedure>, then <recovery waits>, |  |  |  |  |  |  |  |  |  |  |  |  |
|  |   causing <RTO missed out of hours> |  |  |  |  |  |  |  |  |  |  |  |  |

## 2. Accepted risks

| ID  | Reason for acceptance | Accepted by (role) | Conditions | Expires / re-review |
| --- | --------------------- | ------------------ | ---------- | ------------------- |
|     |                       |                    |            |                     |

## 3. Closed risks

| ID  | Closed date | How (mitigated / did not occur / superseded) | Evidence |
| --- | ----------- | -------------------------------------------- | -------- |
|     |             |                                              |          |

## 4. Review state

| Revision | State    | Date | Reviewer (role) | Notes |
| -------- | -------- | ---- | --------------- | ----- |
| r1       | proposed |      |                 |       |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
