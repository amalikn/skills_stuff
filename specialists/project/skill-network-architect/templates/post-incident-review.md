---
Title: Post-incident review template
Category: template
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: Blameless post-incident review with impact, detection, timeline, contributing factors, what went well, and actions with owners and dates.
---

# PIR-<nnn>: <incident title>

Worked example: `skill-systems-architect/examples/filled/post-incident-review.md` (filled for a fictional remote-site operator; lives in the systems pack only).

Based on: Google SRE book, chapter 15 "Postmortem Culture: Learning from Failure" (https://sre.google/sre-book/postmortem-culture/) and its example postmortem
(https://sre.google/sre-book/example-postmortem/).

## How to use

- Write one when the agreed triggers are met:
  - user-visible outage or degradation beyond threshold
  - any data loss
  - a manual intervention (rollback, reroute)
  - resolution time beyond threshold
  - a monitoring failure.
- Agree the triggers before incidents happen.
- Blameless: describe actions and the information available at the time, never fault a person.
- Ask what made the action reasonable then and what would have made a safer action easy.
- Use UTC or one stated timezone throughout.
- Separate fact from hypothesis; a cause that was not reproduced or observed stays a hypothesis.

## 1. Summary

| Field                  | Value                                                                                         |
| ---------------------- | --------------------------------------------------------------------------------------------- |
| Incident ID / severity | <INC-nnn> / <sev>                                                                             |
| Status                 | draft / in review / complete, actions in progress / closed                                    |
| Authors / reviewers    | <roles>                                                                                       |
| Summary                | *One or two sentences: what failed, for whom, for how long.*                                  |
| Impact                 | *users or sites affected, duration, transactions lost, data lost (RPO), contract effect; units* |
| Trigger                | *the event that set it off*                                                                   |
| Detection              | *how and when we knew; was it a user report or an alert?*                                     |
| Resolution             | *what restored service*                                                                       |

## 2. Timeline

| Time (TZ) | Event                           | Source (log, alert, chat) | Actor (role) |
| --------- | ------------------------------- | ------------------------- | ------------ |
| <hh:mm>   | first user-visible symptom      | <probe>                   |              |
| <hh:mm>   | alert fired / page acknowledged |                           |              |
| <hh:mm>   | mitigation started              |                           |              |
| <hh:mm>   | service restored (measured how) |                           |              |
| <hh:mm>   | incident closed                 |                           |              |

Durations: time to detect <n> min; time to mitigate <n> min; time to restore <n> min.

```text
CAUSAL CHAIN: read left to right; the latent condition existed before the trigger

+------------------+   +-----------------+   +-------------------+   +----------------+
| change / trigger |-->| component state |-->| dependency effect |-->| user symptom   |
+------------------+   +-----------------+   +-------------------+   +----------------+
                                ^
                                |
                     +---------------------+
                     | latent condition    |
                     | since <date>        |
                     +---------------------+
```

## 3. Contributing factors

*There is rarely a single root cause. List the conditions that together allowed the incident, each with evidence and label. In a worked or*
*training example, label invented facts USER_STATED and say so in a footnote.*

| Factor | Type (latent condition, trigger, detection gap, recovery gap, process, design) | Evidence | Label            |
| ------ | ------------------------------------------------------------------------------ | -------- | ---------------- |
|        |                                                                                |          | VERIFIED_PRIMARY |

## 4. What went well, what went poorly, where we got lucky

- Went well: *...*
- Went poorly: *...*
- Got lucky: *conditions that limited impact by chance; each is a latent risk.*

## 5. Actions

| ID   | Action | Type (prevent, mitigate, detect, process) | Factor addressed | Owner  | Due          | Tracking | Status |
| ---- | ------ | ----------------------------------------- | ---------------- | ------ | ------------ | -------- | ------ |
| A-01 |        | detect                                    |                  | <role> | <YYYY-MM-DD> | <ticket> | open   |

*Prefer actions that change the system over actions that ask people to be more careful.*

## 6. Follow-up and review state

- Design documents, ADRs, failure-mode rows or risks updated: *links.*
- Review meeting date and attendees (roles):

| Revision | State    | Date | Reviewer (role) | Notes |
| -------- | -------- | ---- | --------------- | ----- |
| r1       | proposed |      |                 |       |
