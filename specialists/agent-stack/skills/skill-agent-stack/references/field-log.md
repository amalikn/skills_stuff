# Field log — why it exists and what it can prove

Read this when interpreting the field log, or when deciding whether to record an entry.

## What it is for

Every evaluation this stack has run tests whether routing agrees with a corpus. That is **necessary and not sufficient**: a route can be perfectly corpus-correct and still not make the work better,
and no corpus can detect that, because the corpus is the thing being agreed with. Only real use can.

## Field ownership, and why it is split

- **`--followed` and `--overrode` belong to whoever did the work.** Only they know what was actually used.
- **`--helped` is operator-only.** An agent must never self-assess whether its own routing helped: it is the one field where the recorder has an interest in the answer. Absent is the honest default,
  and the report says so rather than showing a blank column that reads as missing data.
- **Omit `--overrode` when you followed the route.** A prose "none" counts as a change and inflates the one statistic the log exists to produce — silently, and in the flattering direction, since every
  clean route would add to it. Observed on the first real entry ever logged.

## How to read it

Observational, self-reported, and confounded by task difficulty and by whatever you were going to do anyway. **It cannot establish causation.** What it can do is surface a pattern too consistent to be
noise: the same owner overridden the same way repeatedly is a routing defect, while one override is a preference. The report flags any owner overridden three or more times and prints its own caveat
below n=10.

## What is captured, and what is deliberately not

| Field                                       | Kind               | Why it is here                                                                                                              |
| ------------------------------------------- | ------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| `route_mode`, `owner`, `personas`, `skills` | fact               | the route itself; `route_mode` is the dominant cost lever in one word                                                       |
| `gates`                                     | fact               | the ONLY way to see over-assertion in real use — the eval corpus has expected values to compare against, the field has none |
| `closure_changed`                           | fact               | free, from `close_route.py --explain`; the direct measure of whether the repair does anything outside the harness           |
| `dispatched`                                | fact               | a count, and what the cost analysis turns on                                                                                |
| `tokens_estimated`                          | estimate           | unverifiable by construction; believe `dispatched` when they disagree                                                       |
| `followed`, `overrode`                      | fact               | only the doer knows what was used; `overrode` is the load-bearing field                                                     |
| `helped`, `gates_useful`                    | operator judgement | never self-assessed by an agent                                                                                             |

**Deliberately absent**, because each would cost capture friction and buy little:

- **Duration.** An agent cannot measure its own wall-clock reliably, and `dispatched` already proxies cost with a number that is a fact.
- **Domain or task tags.** Derivable from `project` and the task text; asking for them invites the agent to fit the tag to the route it chose, which is the error [rule
  0006](../../../.archcore/rules/0006-required-personas-is-ownership.md) names.
- **Rework.** A genuinely strong signal — did the operator have to redo it — but it is only knowable later, so it belongs to a follow-up entry rather than the original one. Worth adding when the log
  is large enough for the question to be answerable.
- **Anything the repo already knows.** The commit, the diff, the files touched. Recording them here duplicates git and goes stale.

**Every added field is friction, and friction kills capture.** The log had four entries when these were chosen; the bar for a fifth field is that it answers a question the existing ones cannot.
