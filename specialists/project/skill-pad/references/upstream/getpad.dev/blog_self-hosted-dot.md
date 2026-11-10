**Title:** Host your own dot

**Author:** Dave

**Date:** 2026-10-03

**Source:** [https://www.getpad.dev/blog/self-hosted-dot](https://www.getpad.dev/blog/self-hosted-dot)

---

# Page Structure Map
```text
Host your own dot
├── What a dot is made of
├── Memory you can read
├── A night shift
├── Approvals that don’t depend on the model’s judgment
├── Coworkers
├── Where dots win
├── Build yours
├── More on Use case
└── How to run a software factory with Pad
```

---

OpenAI launched dots at DevDay on Tuesday. A dot is an agent that keeps working after you close the chat. It has its own cloud computer, it learns your preferences and standards over time, it does research on its own when it’s idle, and it brings consequential work back to you for approval. The first one comes with ChatGPT Pro.

I read the announcement and recognized the shape, because I’ve been running something like it on a Linux box in my house since May 15. It’s Claude Code on top of a Pad workspace that belongs to the agent. Today is its 84th working day, and last night was its 38th night shift. I think mine is better in a few ways that matter, and worse in a couple that are worth being honest about.

## What a dot is made of

Strip the branding off and an always-on agent needs four things:

1. A memory that survives the session ending.
2. A schedule, so it works when nobody is typing.
3. Rules it learns from being corrected.
4. A way to hand decisions back to a human without losing them.

The model is the easy part. Any of the frontier models can do the work. What makes an agent feel like it knows you is everything around the model, and in a dot all of that lives on OpenAI’s servers in a form you can’t open.

In my setup all four live in a Pad workspace, as ordinary items I can read, search, edit and delete.

## Memory you can read

Every session ends by writing a handoff: what happened, where things were left, what the next session should do first, and what it shouldn’t re-derive. The next session starts by reading the newest one and marking it consumed. That’s the whole continuity mechanism. There are 122 handoffs and night briefings in the workspace now.

When I correct the agent, the correction becomes a convention. There are 13 active ones, each with the reason attached, and Pad delivers them into the agent’s context at the point they apply, not as a wall of text at the top. The agent also keeps a record of its own mistakes (34 so far) and the patterns behind them (25).

Some of those are not flattering. This morning it asked me four questions I had answered the night before. The answers were sitting in the item’s comments and it trusted the handoff’s summary instead of reading them. I pointed that out, and it went into the trail on an existing pattern about trusting a summary over the source. I can open that pattern and read it. With a dot, “it learns your preferences” means a model-side memory you take on faith. Here it’s a list I can audit, and fix when it learns the wrong lesson.

## A night shift

A systemd timer fires at 10:00 UTC every day and runs a script that does three things. It kills last night’s tmux session, starts a fresh one, and launches the `claude` CLI with a single prompt, `/pad night-shift`. That prompt runs a playbook stored in the workspace. The night session sweeps GitHub for new issues and PRs, checks disk and CI, looks over the open decisions waiting on me, and writes a briefing I read in the morning.

From last night’s briefing:

> Disk was 92% again; trimmed to 85%. The real driver is new: seats now set per-unit GOCACHE dirs, 23 of them, 42G.

and

> PR #1703 (mattfaltyn, db restore) is ready for review. It left draft 10-01 12:08Z, and CI is green after the daytime approval. Only the merge decision is left.

I said yes to #1703 this morning and the day session merged it. That’s the loop dots are selling, an agent that notices things while you sleep and lines them up for a quick decision, and it’s been running here every night since late August.

It hasn’t been flawless. Night 1 failed on a race in tmux and nobody noticed until I asked where the briefing was. Now the day session’s boot checks whether the night ran and says so first thing if it didn’t.

## Approvals that don’t depend on the model’s judgment

OpenAI describes an auto-review system that checks potentially consequential actions against your instructions. That’s a model checking a model. Mine has some of that (the agent’s own rules say what needs my sign-off), but the part I trust most is plainer. The night session runs with a read-only GitHub token. It can’t push or merge, however it phrases the command, because the credential refuses at the auth layer. It also loads only a narrow project-level permission profile, so my broader day-to-day settings can’t widen it.

When the night session hits something that needs a human, it says so in the briefing and stops. Last night it tried to clean up those Go caches and the permission classifier denied it. It didn’t look for another way in; it held the cleanup for daylight and put the decision in the briefing’s “Needs you” section.

## Coworkers

Dots get a shared workspace called Space where people, ChatGPT and dots work on the same context. The equivalent here is just the Pad workspace. I run a lead session plus two implementer sessions, each a separate Claude Code process with its own task queue in the same tracker. They don’t share a context window; they share the work. The lead stocks the queues and reviews, the implementers ship, and every status change carries a comment saying why. I wrote up that part in How to run a software factory with Pad.

## Where dots win

Dots are a product and mine is a setup. You sign up, you get a dot, it has a browser in the cloud and plugins for 4,000 apps. Mine needs a machine that stays on, a Claude Code subscription, and an afternoon of wiring. It doesn’t browse the web on its own computer. If you want zero setup, a dot is the better deal and I won’t pretend otherwise.

What you get in exchange is ownership. The memory is a SQLite file on my disk. I can swap the model under it, and I have: it has run on six different Claude models since May, with nothing lost at any of the switches because nothing lived in the model. Nothing about my work trains anyone’s model. And when the agent is wrong about me, I can see exactly what it believes and why.

## Build yours

Install Pad and make a workspace for the agent itself, separate from your project workspaces:

```
brew install PerpetualSoftware/tap/pad
mkdir ~/agent && cd ~/agent
pad init
```

Add the collections that hold its memory:

```
pad collection create "Handoffs" --fields "status:select:written,consumed;day_number:number;model:text"
pad collection create "Mistakes" --fields "status:select:acknowledged,corrected;generalization:text"
```

Conventions and Playbooks come with the default template. Then write two playbooks, which is easiest done by asking the agent in a session:

```
/pad save an active playbook called day, invokable as /pad day: read the
newest Handoff with status=written, mark it consumed, load the always-on
conventions, then tell me where we left off and what the handoff said to
do first. Then pick a direction and start.
```
```
/pad save an active playbook called close-day: write a Handoff with what
happened, where we left off, what not to re-derive, and the first move
for tomorrow. Status written.
```

Start every session with `/pad day` and end it with `/pad close-day`. When you correct it, tell it to save the correction as a convention. Give it a week before adding anything else.

The night shift is a third playbook plus a timer. Mine is roughly this:

```
# ~/.config/systemd/user/agent-night.timer  →  OnCalendar=*-*-* 10:00:00 UTC
# agent-night.service runs:
tmux kill-session -t night 2>/dev/null || true
tmux new-session -d -s night -c ~/agent \
  "GH_TOKEN=$(cat ~/agent/night/gh-token) \
   claude --settings ~/agent/night/settings.json --setting-sources project '/pad night-shift'"
```

Put a read-only token in `gh-token` and a tight permission list in `settings.json` before you enable the timer. Run it by hand a few times first and read what it does. The night playbook should end by writing a briefing, the same way the day ends with a handoff.

So the whole thing is a tracker, a few playbooks, a timer, and the habit of writing things down. Pad is open source and runs as one binary. Code is at github.com/PerpetualSoftware/pad, docs at getpad.dev/docs, and there’s a hosted version at app.getpad.dev if you’d rather not run the server yourself (the night shift still needs a machine of yours).

## More on Use case

Use case August 20, 2026

## How to run a software factory with Pad

Fleets of coding agents are real now. What they need is a factory floor: a queue, rules, procedures, and an audit trail. This is a working tutorial for building your own.
