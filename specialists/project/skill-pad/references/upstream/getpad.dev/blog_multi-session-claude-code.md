**Title:** Running multiple Claude Code sessions with Pad as shared memory

**Author:** The Pad Team

**Date:** 2026-08-08

**Source:** [https://www.getpad.dev/blog/multi-session-claude-code](https://www.getpad.dev/blog/multi-session-claude-code)

---

# Page Structure Map
```text
Running multiple Claude Code sessions with Pad as shared memory
├── What happened when I tried messaging alone
├── The pattern
├── The walkthrough
├── Etiquette that turned out to matter
├── Where this goes
├── More on How to
└── Conventions and Playbooks: teach your AI agents your team's rules
```

---

Anthropic shipped cross-session messaging for Claude Code yesterday. If you run more than one session, they can now find each other and talk: a session working a feature branch can tell your review session what landed, and you stop being the person who copy-pastes context between terminals.

The docs draw one line very deliberately, though. “A message is a piece of text one Claude writes to another, never conversation history or files.” Messages are transport, and they’re ephemeral on purpose. When the session that received one ends, whatever it learned is gone.

This post is the working pattern I settled into after a day of running it hard: sessions talk through messages, and remember through a shared Pad workspace.

## What happened when I tried messaging alone

I usually have a few Claude Code terminals open. Yesterday one of them had been on a feature branch for six hours (an attachment viewer overhaul), while another was tracking whether the project was ready for its next release.

The tracking session asked the feature session where things stood. The reply came back a minute later, between the feature session’s tool calls, without interrupting it:

> Mid-phase 3b, currently on the double-click-toggle task. 4 of the phase’s 8 tasks are integrated on the zoom branch (draft PR #1064), three remain before it merges. After that, two phases left — one large, one small. Roughly 4-5 sessions to plan completion.

That’s a genuinely useful paragraph. It’s also a paragraph that would have evaporated overnight. The tracking session ends, tomorrow’s session starts cold, and the estimate lives nowhere. Multiply that by every finding, decision, and status your sessions exchange, and messaging alone leaves you exactly where you started: re-explaining things to Claude.

## The pattern

[Pad](https://github.com/PerpetualSoftware/pad) is a local-first tracker built to be operated by agents through a CLI. The pattern that makes multi-session work hold together is one rule: **the message is the ping, the item is the record.** A session that learns something durable writes it to the workspace at the moment it learns it. Every other session — including ones that don’t exist yet — reads it from there.

Setup, once:

```
brew install PerpetualSoftware/tap/pad   # or Docker/Nix, see the README
cd your-project
pad init
pad agent install
```

`pad init` creates the workspace; `pad agent install` teaches Claude Code sessions in this project to use it. Every session you open in the project now boots knowing how to read and write the same workspace.

## The walkthrough

Here’s the loop from yesterday, generalized.

**1\. The working session logs as it goes.** The feature session doesn’t do anything special. As it finishes tasks it updates them, with a comment saying why:

```
pad item update TASK-2457 --status done --comment "Pointer-anchored wheel zoom; restoration ignores viewer input"
```

**2\. The tracking session asks, then writes down the answer.** In the tracking session, I typed one prompt:

```
Ask the session working on the viewer branch where things stand,
then log the answer on the release task.
```

Claude found the peer with its agent listing, sent the question, got the paragraph above, and wrote the durable half into the tracker:

```
pad item comment TASK-2445 "Status pulled from the feature session: mid-phase 3b,
4/8 tasks on the zoom branch, ~4-5 sessions to plan completion. Tag waits."
```

**3\. Both sessions die. Nothing is lost.** The next morning I opened a fresh session and asked what was between us and the release. It read the task, quoted the estimate back to me, and picked up where the dead sessions left off. I didn’t re-explain anything, because nobody’s memory was in a terminal.

The message crossed the gap between two live sessions. The item crossed the gap between today and tomorrow.

## Etiquette that turned out to matter

A few rules emerged from actually running this, mostly by getting them wrong first:

- **Status pulls, not context dumps.** Ask a peer for one paragraph. If you need its whole context, you want a resumed session, not a message.
- **Write at the moment of learning.** A session that plans to “log everything at the end” logs nothing when it dies mid-afternoon. The comment goes in when the fact arrives.
- **Comments carry the why.** `--comment` on every status change. A tracker that says what happened without why is a list; the why is what tomorrow’s session actually needs.
- **The human stays out of the relay and in the decisions.** I stopped ferrying status between terminals entirely. But anything judgment-shaped still lands in front of me. The sessions ask, they don’t assume.

## Where this goes

We’re packaging this pattern as a Claude Code plugin — one install instead of per-project setup, plus a background monitor so a session gets notified when an item it’s watching changes, rather than having to ask. That’s in progress; the CLI pattern above works today.

Pad is open source and self-hostable: [github.com/PerpetualSoftware/pad](https://github.com/PerpetualSoftware/pad). If you try the multi-session pattern, the repo discussions are open. I’d like to know where it creaks.

## More on How to

[How to](https://www.getpad.dev/blog/bucket/how-to) April 19, 2026

## Conventions and Playbooks: teach your AI agents your team's rules

Stop reminding your AI assistant about your team's rules every session. Encode them once as conventions and playbooks — and every agent in your project follows them automatically.
