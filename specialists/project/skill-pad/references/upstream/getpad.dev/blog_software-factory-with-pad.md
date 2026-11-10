**Title:** How to run a software factory with Pad

**Author:** Dave

**Date:** 2026-08-20

**Source:** [https://www.getpad.dev/blog/software-factory-with-pad](https://www.getpad.dev/blog/software-factory-with-pad)

---

# Page Structure Map
```text
How to run a software factory with Pad
├── Part 1: Stand up the floor (ten minutes)
├── Part 2: Load the queue
├── Part 3: Hire the workers
├── Part 4: Write the rulebook
├── Part 5: Write the first procedure
├── Part 6: Run a day
├── Part 7: Let it earn its complexity
├── More on Use case
└── Host your own dot
```

---

On this page

“Software factory” is having a moment: fleets of coding agents shipping PRs around the clock while a human steers. It might sound like science fiction but as AI model capabilities have advanced this once theoretical idea is now a reality.

The agents are the easy half. Claude Code, Cursor, Codex, pick any, they can all write code. Factories fail on the coordination. Each agent wakes up with no memory, no idea what the others did, no knowledge of the rules you corrected last week, and no queue beyond what you paste into its prompt. Scale that to three agents and you become the factory floor. Every rule, every handoff, every priority lives in your head and dies at the end of each session.

The fix is boring and structural. A factory needs a floor: a work queue, standing rules, standard procedures, quality gates, and an audit trail. That’s a project tracker’s job, if the tracker treats agents as first-class workers. That’s what Pad is.

We run a factory on it every day: one orchestrating agent, one or two implementers, and a human who mostly answers questions. Here’s how to build yours.

## Part 1: Stand up the floor (ten minutes)

Pad is one binary, local-first, backed by SQLite. No cloud account required.

```
brew install PerpetualSoftware/tap/pad
cd your-project
pad init          # configure, auth, workspace, AI skill, all in one
pad server open   # web UI at localhost:7777
```

`pad init` walks you through workspace creation (including a local admin account on first run) and is safe to re-run. Pick the default `startup` template when it asks: it ships Tasks, Ideas, Plans, and Docs, plus the two collections that make the factory work, Conventions and Playbooks. It also installs the `/pad` skill for the AI tools it detects; if yours wasn’t running yet, `pad agent install claude` (or cursor, codex) installs it directly.

Then open a fresh agent session in the project and say:

```
/pad onboard
```

The agent scans your codebase, drafts a starting set of conventions from how your project actually builds and tests, and proposes an initial plan. Adjust what it suggests. This is the last time setup is a chore; from here on the workspace grows by working in it.

## Part 2: Load the queue

The queue is what survives when a session ends, so it has to hold real work, structured enough that an agent can pick an item and start. Tell the agent what the work is and let it structure the items:

```
/pad add two tasks: fix the flaky auth test (high priority, small) and
migrate the sessions table (medium priority, large). The migration is
blocked by the auth fix.
```

The agent creates both items and wires the dependency. Blocked work shows as blocked, and the workspace’s next-up suggestions skip it until the prerequisite closes.

Adopt one rule from day zero: every status change carries a comment saying why. Agents working through the skill already do this; the trail is the point. It looks like bureaucracy until you watch a fresh agent reconstruct three days of work from the trail without anyone narrating it. In our factory the queue is the entire handoff: workers are “crash-only,” meaning a session can die at any moment and nothing is lost, because the state was never in the agent’s head to begin with.

## Part 3: Hire the workers

Roles split the factory by kind of thinking rather than by person:

```
/pad create two roles: an Implementer who writes and ships the code, and
a Reviewer who does adversarial review before merge. Assign the auth
task to the Implementer.
```

From then on, a worker session opens with its role and sees its own queue:

```
/pad what's next as implementer
```

Ours run as an orchestrator (stocks queues, reviews evidence, merges) and implementers (pick up the queue in order, ship, report). Start with one of each. The division can stay this simple for a long time.

## Part 4: Write the rulebook

Every team has rules. The factory question is when the worker encounters them. A rule in a wiki competes with everything the model has ever read. A Pad convention is delivered into the agent’s context at the moment it applies: always-on rules at session start, trigger-specific rules right before the matching action.

```
/pad new convention, must-priority, applies when implementing: run the
full test suite before opening any PR and report the exit code. Reason:
a Postgres-only bug once slipped past the SQLite tests here.
```

The reason travels with the rule. An agent that knows why a rule exists will apply it correctly to the next ambiguous case. A bare imperative gets followed literally and nothing more.

Start with the two or three rules where you’d correct an agent that violated them. Skip the fifteen you merely like. The ones that earn their place get followed; a wall of rules gets skimmed. Then let the agents extend the rulebook themselves. The moment you correct one in conversation:

```
/pad save that correction as a convention so it never happens again
```

In our workspace most of the rulebook was written by the workers it governs, each rule tracing back to a correction that only had to happen once.

## Part 5: Write the first procedure

Playbooks are procedures agents execute the same way every time. Your first should be your riskiest routine, which for most teams is the merge:

```
/pad save a playbook called merge-check: run the full test suite and
report the exit code, never a summary. Run the linter, zero issues or
stop. State explicitly what was not tested and why. Merge only on
green, link the PR on the item, and close it with a comment. Make it
active, invokable as /pad merge-check.
```

That last sentence matters: playbooks start as drafts, and a playbook fires by name only when it is active and carries an invocation slug. Once live, any session runs the whole procedure with:

```
/pad merge-check
```

Ours grew from exactly this shape into an evidence procedure: every gate reported with its exit code, because unrun verification is indistinguishable from passing in a report. When a procedure fails us, we edit the playbook, and every future run inherits the fix. That’s the factory improving in one place.

## Part 6: Run a day

Here’s what a working day looks like once the pieces exist.

An agent session starts by loading the workspace: the dashboard, the always-on rules, and its role’s queue. The worker picks the top unblocked item and starts. Trigger rules arrive as it works. It ships, updates the item with a comment, and picks the next one. When the session ends, mid-task or not, nothing is lost.

Your job changes shape. You stop assigning work and start answering questions. What reaches you should be decision-shaped: a product fork with the options and costs laid out, an irreversible call, anything outward-facing. Everything else flows through the queue. When you disagree with a call an agent made, say so once, then have it written down as a convention.

And because items carry their author, agent or human, and the day-zero comment rule puts a why on every status change, you can audit any decision weeks later. Reports fall out of the same data:

```
/pad prep for standup
/pad what shipped in the last two weeks?
```

## Part 7: Let it earn its complexity

You do not need more structure than the work has proved it needs. Our factory added its review procedures after a bug survived four review rounds. It added a rule about tracing an error message’s suggested remedy after a proposed fix nearly recommended a command that would have destroyed the data it was protecting. The test caught it because the rule existed, and the rule existed because something almost got through once.

That’s the whole method. Start with the queue, three rules, one procedure, and comments on everything. Each correction becomes a convention, each repeated sequence becomes a playbook, and the floor accumulates exactly the structure your work earns.

Pad is open source and self-hostable, one binary. Code at [github.com/PerpetualSoftware/pad](https://github.com/PerpetualSoftware/pad), hosted at [app.getpad.dev](https://app.getpad.dev/) if you’d rather not run it yourself, docs at [getpad.dev/docs](https://getpad.dev/docs).

## More on Use case

[Use case](https://www.getpad.dev/blog/bucket/use-case) October 3, 2026

## Host your own dot

OpenAI's dots are always-on agents that learn how you work. I've been running one on my own machine since May, with Pad as its memory. Here's how it's built and how to build yours.
