**Title:** Claude isn't getting dumber. Your project is leaving the room.

**Author:** Dave

**Date:** 2026-05-05

**Source:** [https://www.getpad.dev/blog/claude-isnt-getting-dumber](https://www.getpad.dev/blog/claude-isnt-getting-dumber)

---

# Page Structure Map
```text
Claude isn't getting dumber. Your project is leaving the room.
├── The model isn’t worse. The room is darker.
├── The fixes people are inventing are patches on the symptom
├── What actually fixes it: state outside the transcript
├── What that looks like in practice
├── The honest caveat
└── Try it
```

---

I was three hours into a session with Claude Code when it invented a file. Not a fabricated function or an imaginary library; those I’m used to. This was a whole file path that didn’t exist, in a directory we’d talked about at the start of the session, named something plausible enough that I almost just opened it. When I pointed it out, the agent apologized, asked which file I’d actually been editing, and then a few minutes later forgot most of the convention we’d agreed on at minute four, including the part that mattered.

I’ve seen this pattern dozens of times, and judging by my feed, so has half of r/ClaudeCode. The posts go up every week, all with the same shape: Claude is getting worse, Anthropic is nerfing it, the 4.7 release is somehow dumber than the 4.6 it replaced, something must have changed. I read those posts carefully, because I want them to be wrong, and because the people writing them are describing something I have absolutely felt myself. But I think they’re diagnosing it wrong, and the wrong diagnosis is leading to a worse fix than the one we already have.

## The model isn’t worse. The room is darker.

The part of this that took me a while to sit with is that the weights you started the session with and the weights you have at hour three are the same weights. The model didn’t get downgraded mid-conversation, and Anthropic didn’t quietly swap a checkpoint while you were getting coffee. What changed is what the model could see clearly.

Long-context language models don’t have flat, even attention across their context window. Liu et al.’s 2023 paper *“Lost in the Middle”* showed it cleanly: information stored in the middle of a long context is retrieved less reliably than information at the start or the end. Real sessions add a second wound on top of that, because Claude Code (and most agent harnesses) will periodically *compact* the conversation, which is a polite word for *summarize away*. The compaction is necessary, since otherwise you’d hit the token wall, but the summary is lossy. The decisions you made together at minute four, things like *use Zod for validation*, *never touch the worker pool*, *the canonical filename is `foo` not `foos`*, do not survive that compaction intact. They become a paragraph in a system message, if they survive at all.

The agent that returns from a `/compact` is not a worse model. It’s the same model looking at a smaller, blurrier description of what happened so far, and it’s doing exactly what a smart person would do given a blurrier description, which is to fill in the gaps with plausible guesses. That’s where the invented file comes from, along with the half-forgotten convention, the duplicated function, and the suddenly-contradicted architectural decision. None of those failures are the model getting dumber; all of them are the project leaving the room.

This isn’t a defense Anthropic wrote and asked me to publish. It’s a defense that anyone who has ever instrumented an LLM application has run into. There’s even [an issue in Anthropic’s own repo](https://github.com/anthropics/claude-code/issues/34685) where Claude itself, at 48% of a 1M-token window, told the user *“I’m deep enough in this context that I’m not being effective”* and recommended starting fresh, well before the advertised limit. The honest read is that effective context is a fraction of advertised context, and once you cross the line, the room gets dark fast.

## The fixes people are inventing are patches on the symptom

The community is not sitting still about this. Read the dev.to posts and the Medium tutorials and you’ll find a small cottage industry of workarounds: 3-file systems for keeping Claude on track, lightweight session managers, `CLAUDE.md` scaffolds, aggressive `/compact` discipline, ritualized context refreshes every thirty minutes. Some of them are clever, and most of them work for a while.

The flaw they share is that they live inside the very thing that’s degrading. A `CLAUDE.md` is just more text in the system prompt, text that costs tokens on every API call and that the model is asked to attend to while its attention is being stretched across a 100k-token transcript. A markdown file titled *“Decisions we made today”* gets summarized away by the same compaction that ate the original decisions. A 3-file system rotates the problem around, but the problem stays inside the chat window. You cannot solve a context-degradation problem with more context.

## What actually fixes it: state outside the transcript

The structural answer is older than LLMs, and it goes like this: don’t try to remember everything; query a system that already knows.

That’s what Pad is. A small, fast, queryable project state store (tasks, plans, decisions, conventions, dependencies) sitting next to your codebase as a single SQLite database. Your agent doesn’t have to recall what you decided three hours ago, because it can ask:

```
pad item show TASK-5
pad project dashboard
pad item list conventions --field status=active
```

And get back fresh, exact, unsummarized answers. Not the agent’s summary of its summary of what was once said in a chat, but the current truth.

The conventions you set at the start of a project don’t drift out of attention, because they’re items the agent re-reads before performing work. The plan you wrote on Monday isn’t compressed into a paragraph by Friday’s `/compact`, because it’s still there, structured, with its child tasks and their statuses. The decision you made at minute four is a comment on `TASK-12`, queryable by anyone (agent or human) at any context percentage. The agent stops trying to be a memory and goes back to being a reasoner.

## What that looks like in practice

A small dialogue from a real session at 67% context:

> **Me:** Pick up where we left off. What’s next?
> 
> **Claude:** *Running `pad project next`…* The next task is **TASK-1138**, *Document the IDEA-1 onboarding entry point*, under **PLAN-1131** (*IDEA-1 onboarding for new accounts*). Before I start, let me re-read the active conventions… *running `pad item list conventions --field trigger=on-implement --field status=active`* … got it. I’ll keep the change PR-sized per **CONVE-2** and run `make install` after any backend change per **CONVE-1**.

Without Pad, I’d have spent five messages re-explaining what TASK-1138 was, which plan it lived under, and which conventions applied, and a `/compact` halfway through would have eaten my re-explanation anyway. With Pad, the agent re-grounded itself in two queries and got back to work. The model didn’t have to remember; it just had to read.

## The honest caveat

None of this makes Claude infallible. Long sessions still get fuzzy, and the agent will occasionally make a tactical mistake that a fresh session wouldn’t. There’s no architecture in 2026 that makes a 200k-token transcript feel as crisp as a 5k one.

What this does change is that the *project* stops disappearing. Most of what people are reporting as “the model is getting worse” (the duplicated functions, the forgotten conventions, the hallucinated file paths) is the project disappearing, not the model.

If you take one thing from this post, let it be this: the next time your agent invents a file at hour three, don’t blame the weights, and don’t write a Reddit post about how Anthropic broke something. Look at where your project lives. If it lives in the chat, it has been compressed by now. If it lives in something the agent can re-read, the model is fine; it has just been working in the dark.

## Try it

The fastest way to put this to the test is Pad Cloud with our [remote MCP server](https://www.getpad.dev/blog/remote-mcp-launch). Create a workspace at [app.getpad.dev/register](https://app.getpad.dev/register), then paste a single URL into Claude Desktop, Claude.ai, Cursor, or Windsurf:

```
https://mcp.getpad.dev
```

Sign in once, and your agent has access to your tasks, plans, conventions, and decisions, on every device that runs an MCP-capable client. No install, no API keys, no terminal. Per-client setup steps live at [getpad.dev/mcp/remote](https://getpad.dev/mcp/remote).

If you’d rather keep your project on your own machine, Pad is Apache 2.0 and ships as a single self-hosted binary:

```
brew install PerpetualSoftware/tap/pad
pad init
```

Either path, open a long Claude Code session against it and see if hour three feels different. If it doesn’t, [tell me on GitHub](https://github.com/PerpetualSoftware/pad). The strongest critiques end up in the next post.
