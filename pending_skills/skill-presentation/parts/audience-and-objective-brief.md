# Audience and objective brief

## Scope

The brief is written before any slide, page or sheet. It records who the deliverable is for, what they must do or believe afterwards, what they already think, and the one sentence the deliverable
stands on. If the audience or the decision is unknown, the agent asks; it does not draft. Existing public skills treat this lightly: Anthropic's `doc-coauthoring` asks five meta-questions and tests
the draft on a context-free reader; a coach skill blocks if audience or purpose is unknown; none maps audience and objective to a form or requires the four lenses. This reference is that missing front
end.

## Contents of this reference

- [The brief](#the-brief)
- [The questions](#the-questions)
- [Audience types](#audience-types)
- [Handling a sceptical stakeholder](#handling-a-sceptical-stakeholder)
- [The reader test](#the-reader-test)
- [Failure modes and fixes](#failure-modes-and-fixes)

## The brief

Copy `templates/brief.md` and fill every field; a field the agent cannot fill is a question to the operator.

| #   | Field             | What it holds                                                                                            |
| --- | ----------------- | -------------------------------------------------------------------------------------------------------- |
| 1   | Objective         | The one thing the audience should do or believe afterwards, and by when                                  |
| 2   | Ask or decision   | The exact request and its options, in one sentence each                                                  |
| 3   | Audience          | Who decides, who influences, who reads it later; their roles, power and interest, what they already know |
| 4   | Stance            | Supportive, neutral or sceptical, and the strongest objection they hold                                  |
| 5   | Stakes            | What is at stake for them, not for the presenter                                                         |
| 6   | Governing thought | The one-sentence answer, then the situation, complication and question it answers                        |
| 7   | Evidence          | The three proofs that answer their objections, each with an evidence label                               |
| 8   | Lens plan         | Which of the four lenses lead, which sit underneath, and the known gaps                                  |
| 9   | Constraints       | Time, setting (live or read alone), prior material, tone rules, words to avoid                           |
| 10  | Form and length   | The form chosen with the reason (see choose-the-form.md)                                                 |
| 11  | Follow-up         | Who owns the next step and how success is measured                                                       |

## The questions

Ask in this order and stop when the objective, the audience and the decision are clear:

1. What decision or action should exist after this, and by when? (Objective, ask.)
2. Who decides, who influences, who will read it without you in the room? (Audience.)
3. What do they believe today, and what is their strongest objection or fear? (Stance.)
4. What is at stake for them if nothing changes? (Stakes.)
5. In one sentence, what is the answer? If it cannot be said, keep thinking. (Governing thought.)
6. Which three facts would change their mind, and how sure are we of each? (Evidence.)
7. Which of business, technical, financial and management does this audience weigh most, and which do we have no evidence for yet? (Lens plan.)
8. Will they read it alone or discuss it live, and how long do they have? (Form and length.)
9. What must not be said, and which words do they not use? (Constraints and tone.)

## Audience types

| Audience              | Usually cares about                         | Usually lacks     | Lead with                                                      |
| --------------------- | ------------------------------------------- | ----------------- | -------------------------------------------------------------- |
| Executive sponsor     | Outcome, cost, risk, a decision             | Technical context | The answer, the cost view, the ask                             |
| Sceptical stakeholder | Whether the work is needed and cheap enough | Trust in the plan | Their stated requirements, what is unknown, the plan and dates |
| Technical lead        | Correctness, risk, dependencies             | Time              | The design, the evidence, the open technical questions         |
| Operations team       | What changes for them, what to do           | Detail of why     | What changes, how to do it, who to call                        |
| Customer              | Benefit, price, reliability                 | Product internals | Benefit, price, proof                                          |
| Board                 | A resolution, risk, resourcing              | Detail            | A clear resolution, options, the risk                          |

Grid for planning: map power and interest (high and low) per stakeholder; tailor the depth and the channel, and name who reads it later.

## Handling a sceptical stakeholder

The audience may be right that something is missing. Concede what is unknown, show the requirement-to-step-to-date traceability, state the gap with an owner and a date, and ask for the help needed. Do
not argue who is technically right and do not defend the design before the requirements; start from the requirements and show where the work serves them. Perception matters: answer it with documented
requirements, not with argument.

## The reader test

Before sending, give the draft to a reader who has none of the context (a fresh agent session with no history, or a colleague outside the work) and ask them to state back the ask, the answer and the
three reasons. If they cannot, the deliverable fails; fix the structure, not the wording.

## Failure modes and fixes

| Failure                          | Fix                                                               |
| -------------------------------- | ----------------------------------------------------------------- |
| Defensive over-explaining        | Lead with the answer, then answer their strongest objection first |
| Technical depth first            | Outcome and stake first; detail in an appendix                    |
| Jargon the audience does not use | Name the function and the outcome in their terms                  |
| Status without outcomes          | Report the change, its impact and the next decision               |
| No decision asked                | End with one explicit request, an owner and a date                |
| More is better                   | Restrict length; long attachments avoid choosing what matters     |
| Tilted to one lens               | Run lens_coverage and fill or mark each gap                       |
