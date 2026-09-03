# Field log — why it exists and what it can prove

Read this when interpreting the field log, or when deciding whether to record an entry.

## What it is for

Every evaluation this stack has run tests whether routing agrees with a corpus. That is **necessary and not sufficient**: a route can be perfectly corpus-correct and still not make the work better, and
no corpus can detect that, because the corpus is the thing being agreed with. Only real use can.

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
