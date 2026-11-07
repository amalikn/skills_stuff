---
Title: Composing an engine from many languages
Category: reference
Status: current
Authority: local-supplement
Scope: How YAML, a configuration tool, Python, shell, templates, records and flow maps are joined into one safe engine; the seams between them, not the parts
Last reviewed: 2026-11-02
Summary: >-
  The thinking behind a multi-language change engine: give each language the one job it is best at, make every seam a small data contract, and check
  each seam offline. Read with design-patterns.md, which holds the parts; this file holds how they interlock.
---

# Composing an engine from many languages

The operator asked for this on 2026-11-02: capture the out-of-the-box thinking and the interaction of the pieces, not the project. `design-patterns.md` holds each piece as a pattern. A catalogue of
pieces does not say how they fit, so this file does what a crosscutting-concepts section does in an architecture description: one place for what spans every building block. The worked source is the
smc_change Ansible role at local-knowledge-ansible e2f760e; nothing here needs that domain.

How to read it: [the idea](#the-idea), then [who does what](#who-does-what), then [the seams](#the-seams). To build one, go to [build your own](#build-your-own). Numbers like P-09 are patterns in [design-patterns.md](design-patterns.md).

## Contents

- [The idea](#the-idea)
- [Who does what](#who-does-what)
- [The seams](#the-seams)
- [One change, end to end](#one-change-end-to-end)
- [A parser with no parser](#a-parser-with-no-parser)
- [Seven moves that make it work](#seven-moves-that-make-it-work)
- [Build your own](#build-your-own)
- [When not to](#when-not-to)
- [Learned](#learned)

## The idea

Most automation grows one script per change, each with its own backup, verify and rollback bugs. The engine turns that inside out: **safety is code, written once; a change is data, written many
times.** Three further decisions follow, and they are what makes it unusual:

1. **Each language does one job.** YAML states, the orchestrator sequences, Python judges, shell touches the system, templates reshape, CSV reports. Nothing does two jobs.
2. **Data crosses every boundary as JSON.** No language calls another's functions, so each side can be tested alone and replaced alone.
3. **Every seam has a check that runs without a target.** A mistake is found on the controller, in seconds, not on a box at the far end of a satellite link.

## Who does what

| Layer         | Written in                       | Its one job                                    | Must never                           | Why this language                                         |
| ------------- | -------------------------------- | ---------------------------------------------- | ------------------------------------ | --------------------------------------------------------- |
| Change spec   | YAML                             | State what, where, how to undo, how to prove   | Hold logic or shell over a few lines | A reviewer reads one file; a diff is the whole change     |
| Orchestrator  | Ansible tasks                    | Sequence stages, connect, run, fail, retry     | Know a change, an action type or a   | Inventory, connections, serial batches and failure        |
|               |                                  |                                                |   check type                         |   handling come free                                      |
| Normaliser    | Jinja2 template                  | Reduce the spec to one form                    | Touch a target                       | It runs inside the orchestrator, per host, with           |
|               |                                  |                                                |                                      |   no install                                              |
| Action type   | One YAML task file, plus its     | How to make one kind of change                 | Be called by name from the engine    | A new type is two new files and no edit                   |
|               |   undo file                      |                                                |                                      |                                                           |
| Target reader | Python, piped                    | Read, judge and word a check                   | Write to the target                  | Rich logic that leaves no file behind                     |
| Target writer | Short shell, or a shipped helper | Do the risky thing                             | Decide whether it should             | It is what is really on the box; `dash` is everywhere     |
| Controller    | Python                           | Classify recovery, match pools, build trackers | Reach a target                       | Pure functions on JSON, unit-tested in milliseconds       |
|   logic       |                                  |                                                |                                      |                                                           |
| Records       | JSON                             | What happened, per run                         | Be edited                            | One writer, many readers                                  |
| Views         | CSV, summary lines               | Show state                                     | Be a source                          | Rebuilt from records (P-49)                               |
| Flow map      | YAML, rendered to draw.io        | Say what happens and why, for people           | Be trusted unchecked                 | Held to the code by stamps ([P-54](design-patterns.md))   |
|               |                                  |   and agents                                   |                                      |                                                           |

The test for a new piece of logic: which column does it belong in? If the answer is "the orchestrator, with a long `when`", it is probably a Python judge or a spec key.

## The seams

This table is the core of the design. Each row is a place two languages meet: what crosses, in what form, and what catches a break.

| From → to                 | Carrier                                     | Shape                                  | Offline check                                                                     |
| ------------------------- | ------------------------------------------- | -------------------------------------- | --------------------------------------------------------------------------------- |
| Spec → engine             | `include_vars` into one name                | YAML mapping                           | `assert` at load: types known, names resolve, shape valid; the run stops before   |
|                           |                                             |                                        |   any target                                                                      |
| Engine → normaliser       | A lazy variable holding a template lookup   | JSON text, `from_json`                 | A hash proves a rewrite leaves the target unchanged (`target-hash`)               |
| Engine → target reader    | `python3 -` with stdin = source, env        | Source text in, one JSON object out    | The joined program is linted, and tests feed it fixtures (P-09, P-52)             |
|                           |   = config                                  |                                        |                                                                                   |
| Target reader → engine    | stdout, `from_json`                         | `{healthy, gates, lines, plan}`        | Generic names: the engine reads keys it never had to know                         |
| Spec → target writer      | A `file` lookup after the values are set    | A shell script holding no value        | `shellcheck -s sh`, because the target's shell is dash                            |
| Engine → action type      | `include_tasks: actions/{{ type }}.yml`     | Loop variable                          | Type list asserted at load; an undo file must exist                               |
| Engine → controller logic | `delegate_to: localhost` with a script      | Files on disk                          | Plain unit tests; no connection                                                   |
| Run → recovery            | A write-ahead journal, atomic replace       | JSON with a code fingerprint           | Fixture journals for each phase (P-03, P-11)                                      |
| Records → views           | Rebuilt by the last play             | CSV                                    | Test on sample records; a failure prints and never fails the run                  |
| Code → flow map           | `code:` references                          | `path[:symbol]` plus a                 | `trace_sync.py`: suspect steps and uncited files (P-54)                           |
|                           |                                             |   stored fingerprint                   |                                                                                   |

Why JSON and not shared code: an environment variable and stdout exist in every language, need no install, and are visible in a log. A seam you can print is a seam you can debug.

## One change, end to end

Generic names; the sequence is the real one.

1. **Spec.** An author writes actions, facts, conditions, checks. No code ships for a new change.
2. **Load.** The engine reads the spec and refuses a bad one on the controller.
3. **Normalise.** A `loop` becomes plain actions, per host, so everything after sees one form.
4. **Partition.** One controller-only play reads the ledgers and splits targets into done and to do (P-04, P-05): a finished target costs no connection.
5. **Read facts.** One read-only call. Conditions are judged here, once (P-47).
6. **Probe.** The joined reader runs on the target; healthy decides the guard, and the plan says what would change.
7. **Journal, back up, act.** The journal is written first (P-03). Each action type runs, and `action_run` logs what it did with nothing in the spec (P-51).
8. **Restart, reboot if the policy says.**
9. **Probe again, judge the gates.** The same reader, now given the before-output as `base`, so a gate compares and never guesses.
10. **Clean up, record, rebuild views.** Nothing is left on the target; the record goes to the controller; trackers rebuild.

Modes reuse this list: check stops after 6, verify runs 6 and 9, rollback runs the undo files in reverse. Modes are not code paths, they are which stages run.

## A parser with no parser

There is no custom Ansible plugin. What looks like a parser is three small things inside the tool, and that is the out-of-the-box part: the orchestrator's own template engine is used as an interpreter
for a small language.

- **The grammar** is a spec shape, enforced by `assert`.
- **The compiler** is a template that expands sugar (`loop`) into plain actions.
- **The interpreter** is a template that walks facts and conditions and returns JSON.

```jinja
{#- templates/spec_actions.j2: rendered per host through a lazy variable, so host values stay that host's -#}
{%- set out = [] -%}
{%- for a in smc_change_spec.actions | default([]) -%}
  {%- if a.loop is defined -%}
    {%- set base = a | dict2items | rejectattr('key', 'eq', 'loop') | items2dict -%}
    {%- for it in a.loop -%}
      {%- set _ = out.append(base | combine(it)) -%}
    {%- endfor -%}
  {%- else -%}
    {%- set _ = out.append(a) -%}
  {%- endif -%}
{%- endfor -%}
{{ out | to_json }}
```

```yaml
# defaults/main.yml: a variable that is a template, not a value. Why not set_fact: that would fix the first host's values for all.
smc_change_actions: "{{ lookup('ansible.builtin.template', role_path ~ '/templates/spec_actions.j2') | from_json }}"
```

The language a spec author sees has one idea, named so it can be read:

```yaml
facts:
  avr_version: python3 -c '...'                    # a read-only command; its stdout is the value
conditions:
  flash_wanted: "{{ rct_avr_flash | default(false) | bool }}"   # over host variables
  avr_at_214: {fact: avr_version, equals: '2.14'}   # a test of one fact: equals, in or match
actions:
  - type: copy
    when: [flash_wanted, not avr_at_214]            # names, never expressions
```

Why a template and not an action plugin: a plugin runs on the controller and would do this cleanly (Ansible's developer guide), but it adds a Python file the tool must be told about, and its logic
stops being readable beside the tasks that use it. The trade-off is real: Jinja is a poor language for logic. So the rule is that a template only reshapes and tests; **anything that needs a function
goes to Python over a seam.** A logic block that returns JSON because a Jinja block can only return text is the limit of what belongs there. Past about 40 lines, write the plugin.

## Seven moves that make it work

These are the ideas worth taking to a project with no devices at all.

1. **Keep the engine ignorant.** The engine names no type. `99_main.py` loops over a registry; `apply.yml` includes a file named by data. If a word from a change appears in the engine, the design has
   slipped.
2. **Normalise once, at the seam.** Sugar is expanded in one place and everything downstream sees one form, so numbering, plan, conditions and rollback never each learn `loop` (P-50).
3. **Ship source, not files.** Piping a program to `python3 -` writes nothing, needs no cleanup, and cannot leave a stale copy. Config goes in by env, the result out by stdout.
4. **Say what the data can prove, and derive the rest.** The engine finds git work trees named in a command and reports the commits, with nothing in the spec (P-51). Every field an author need not
   write is a field that cannot be wrong.
5. **Check what actually runs.** Lint the joined program, not the parts: the parts use names defined in another file. Check shell as dash. Test the spec's own text (P-52).
6. **Keep promises apart from checks.** `resume_safe` is the author's promise, defaulting to false; `proves` is false before and true after, so it never counts as health. A default that is safe when
   an author forgets is worth more than a rule that says to remember.
7. **Write a failure into the design.** A refused host is a recorded result, not an error. Every run ends in a named state, and a view can say `passed` but nothing ran, because an outcome column tells
   them apart.

## Build your own

The order matters: each step keeps working while the next is added.

1. **Write two real changes by hand** first, unlike each other. The engine is what they share; designing it from one change shapes it to that change (P-17).
2. **Fix the stage list.** Reorder it on paper until each stage only uses what earlier stages read. This list is the hardest thing to change later.
3. **Spec and load check.** Define the shape; refuse a bad spec before touching a target.
4. **The reader with a registry.** One check, then a second in its own file with no engine edit. That second file is the proof the seam is right.
5. **One action type and its undo.** Write the undo first.
6. **Records and the journal** before any second target.
7. **Partition and ledgers** when one target works.
8. **Flow map with stamps** once the stages stop moving, so every later change is reviewed.

Each language brings its own rules: see [the Ansible file](../languages/ansible.md), [Python](../languages/python.md), [shell](../languages/shell.md) and [YAML](../languages/yaml-json-toml.md).

## When not to

Two or three one-off changes do not earn an engine: write the script. Past about a dozen similar changes on many targets, the safety repays itself. A team without the discipline to keep the engine
ignorant gets a framework and still has the per-change scripts, now hidden inside it.

## Learned

> **Learned 2026-11-02** · engine design, any language · VERIFIED_PRIMARY · Source: local-knowledge-ansible `ansible-wifi/roles/smc_change` e2f760e, arc42 section 8 (docs.arc42.org/section-8), Fowler "Writing Software Patterns" · Falsifier: a project that reuses the engine's parts and finds the seam table does not describe how they fit
> A pattern catalogue records pieces and loses how they interlock. A system built from many languages is captured as: a who-does-what table, a seam table with the check for each seam, a walk of one
> run, and links to the patterns for each piece. Fowler's advice holds: why as well as how, a name worth keeping, and code examples that show rather than define.

> **Learned 2026-11-07** · language per environment on a device · VERIFIED_PRIMARY (spike: initramfs hooks in POSIX sh, the on-box agent in
> Python, boot entries as config) / proposal (the compiled watcher) · Source: apn smc-resiliency `.archcore/rules/language-per-environment.rule.md`
> · Falsifier: an initramfs or firmware stage that runs the after-boot language
> On a device the stages pick the language, not the author: firmware and boot loader take config only; the initramfs takes POSIX sh (no
> Python, no libraries); early boot is systemd units; after boot the agent is Python with the standard library; a short sh does the risky
> write; a watcher that must act when memory is exhausted is a case for a small static compiled binary (Go or Rust) that locks itself in
> memory, since an interpreter that pages in or forks can stall under the pressure it watches (a 30 s shell poll missed a filling RAM
> copy-on-write; 5 s plus a rate projection caught it).
