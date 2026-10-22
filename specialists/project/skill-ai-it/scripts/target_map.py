#!/usr/bin/env python3
"""The target map: `target-map.yaml` is a project's source of truth for its goals, its targets and where each stands; a tracker is rendered from it.

Operator, 2026-09-27: progress against a plan's steps was tracked nowhere in one place, so a tracker was built; then "that file
should be the source of truth and markdown is generated based on that", under the name `target-map.yaml`, beside
`context-map.yaml`: the context map says where things are, the target map where the project is going and how far it has got.
Piloted in one project from 2026-09-27 and promoted into skill-ai-it on 2026-10-21 (operator: "the target map is promoted into
skill-ai-it first, then adopted in smc-resiliency for the stages"). Nothing below knows about any project; every project-shaped
choice is data in the map.

The schema is SCHEMA below: every field with its level, `mandatory` (the check fails without it), `recommended` (the check
warns), `optional` (never reported) or `rejected` (refused; the check fails if it appears), each with its reason; some are
conditional ("mandatory when started"). `--schema` prints it as markdown. A project whose targets live in documents lists them
under `sources:` (each with an id and its heading pattern) and each target names its `source`; such a target carries only
verdicts. A source's criteria are a numbered list under a criteria heading, or one checklist line (`- **Completion
checklist:** [x] a · [ ] b`). A target without a source is written inline (name, exit condition, criteria text). One map may mix
several sources and inline targets. `embed` renders the summary table into another page between markers as well.

Reads the map, its source documents, the roadmap and the change log (with its rotated parts in docs/history/). Writes only with
`--write`: the tracker at `render_to` and each `embed` block (nothing outside the markers); with `--sync --write`, appends
targets to the map. A project's governance check calls `evaluate()` and fails when a rendered file differs, so neither can be
hand-edited out of step. Runtime: well under a second on a 50-target map (files only, no network).

`--init` prints a starter map (source mode: one `not started` target per plan heading, every criterion `not run`; inline mode
without a plan: one placeholder target); `--sync` appends a `not started` target for every source heading the map lacks, as
text, so comments survive. Both leave `TODO` where only a person can decide, and the check fails while one is left.

Usage (run with the project's venv; `--project-root` defaults to the current folder):
    python3 target_map.py --project-root .            # validate and report drift; writes nothing; exit 1 on a problem
    python3 target_map.py --project-root . --write    # validate, then render the tracker and embeds in place
    python3 target_map.py --schema                    # print the field reference
    python3 target_map.py --project-root . --init [--source PLAN.md --heading REGEX --label Step --changelog CHANGELOG.md] > target-map.yaml
    python3 target_map.py --project-root . --sync [--write]
    python3 target_map.py --project-root . --show [ID]
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from table_wrap import WRAP_WIDTH, wrap_table  # the shared hook-compatible table wrapper (2026-10-22)

MAP_FILE = "target-map.yaml"

TARGET_STATES = ("not started", "groundwork", "in progress", "exit met", "done")
CRITERION_STATES = ("pass", "partly", "pending", "not run")
OWNERS = ("operator", "agent", "both", "none")
#: Statuses that assert something happened, so they carry evidence and the date it was last checked.
ASSERTED = ("pass", "partly", "pending")
WRAP = 200
#: Markers around an `embed` block; a page holds each exactly once and keeps its own text outside them.
EMBED_BEGIN = "<!-- BEGIN GENERATED: target-map (edit target-map.yaml, then `just target-map`) -->"
EMBED_END = "<!-- END GENERATED: target-map -->"


# ---------------------------------------------------------------------------------------------------------------- records


def parse_moment(value: object) -> dt.datetime | None:
    """A review moment: `YYYY-MM-DD HH:MM`, or a bare date, read as the END of that day (the whole day counts as reviewed)."""
    if value in (None, ""):
        return None
    if isinstance(value, dt.datetime):
        return value
    if isinstance(value, dt.date):
        return dt.datetime.combine(value, dt.time(23, 59))
    text = str(value).strip()
    try:
        return dt.datetime.strptime(text, "%Y-%m-%d %H:%M")
    except ValueError:
        return dt.datetime.combine(dt.date.fromisoformat(text), dt.time(23, 59))


@dataclass
class Evidence:
    """A repo-relative `path` (must exist) or a free-text `ref` such as a CHANGELOG entry id."""

    label: str = ""
    path: str = ""
    ref: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> Evidence:
        """Build the record from its parsed YAML mapping.

        Args:
            d: the mapping as YAML parsed it.

        Returns:
            The Evidence record.
        """
        return cls(label=str(d.get("label", "")), path=str(d.get("path", "")), ref=str(d.get("ref", "")))


@dataclass
class Action:
    """A blocker or next action: who owns it (`owner`, one of OWNERS) and what it is (`text`)."""

    owner: str
    text: str

    @classmethod
    def from_dict(cls, d: dict | None) -> Action:
        """Build the record from its parsed YAML mapping.

        Args:
            d: the mapping as YAML parsed it (None or empty for an absent block).

        Returns:
            The Action record.
        """
        d = d or {}
        return cls(owner=str(d.get("owner", "none")), text=str(d.get("text", "")))


@dataclass
class Criterion:
    """One acceptance criterion's verdict: its number, status, the date last verified, a note and its evidence (text only when inline)."""

    n: int
    status: str
    text: str = ""
    verified: dt.date | None = None
    note: str = ""
    evidence: list[Evidence] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> Criterion:
        """Build the record from its parsed YAML mapping.

        Args:
            d: the mapping as YAML parsed it.

        Returns:
            The Criterion record.
        """
        v = d.get("verified")
        return cls(n=int(d["n"]), status=str(d.get("status", "")), note=str(d.get("note", "")), text=str(d.get("text", "")).strip(),
                   verified=v if isinstance(v, dt.date) else (dt.date.fromisoformat(str(v)) if v else None),
                   evidence=[Evidence.from_dict(e) for e in d.get("evidence", [])])


@dataclass
class Target:
    """One target as the map holds it: verdicts and state; name, exit condition and criteria text only when it has no source."""

    id: str
    goal: str
    state: str
    exit_met: bool
    mention: str
    summary: str
    blocker: Action
    next: Action
    evidence: list[Evidence] = field(default_factory=list)
    as_built_intro: str = ""
    as_built_diagram: str = ""
    criteria: list[Criterion] = field(default_factory=list)
    name: str = ""
    exit_condition: str = ""
    source: str = ""
    ref: str = ""
    reviewed: dt.datetime | None = None

    @property
    def key(self) -> str:
        """The target's id inside its source: `ref` when two sources share ids, else the map id."""
        return self.ref or self.id

    @classmethod
    def from_dict(cls, d: dict) -> Target:
        """Build the record from its parsed YAML mapping.

        Args:
            d: the mapping as YAML parsed it.

        Returns:
            The Target record.
        """
        built = d.get("as_built") or {}
        return cls(id=str(d["id"]), goal=str(d.get("goal", "")), state=str(d.get("state", "")),
                   exit_met=bool(d.get("exit_met", False)), mention=str(d.get("mention", "")),
                   source=str(d.get("source", "")), ref=str(d.get("ref", "")), reviewed=parse_moment(d.get("reviewed")),
                   name=str(d.get("name", "")).strip(), exit_condition=" ".join(str(d.get("exit_condition", "")).split()),
                   summary=str(d.get("summary", "")).strip(), blocker=Action.from_dict(d.get("blocker")),
                   next=Action.from_dict(d.get("next")), evidence=[Evidence.from_dict(e) for e in d.get("evidence", [])],
                   as_built_intro=str(built.get("intro", "")).strip(), as_built_diagram=str(built.get("diagram", "")).rstrip(),
                   criteria=[Criterion.from_dict(c) for c in d.get("criteria", [])])


@dataclass
class Goal:
    """Why the project exists: an id targets point at, a name and a statement."""

    id: str
    name: str
    statement: str

    @classmethod
    def from_dict(cls, d: dict) -> Goal:
        """Build the record from its parsed YAML mapping.

        Args:
            d: the mapping as YAML parsed it.

        Returns:
            The Goal record.
        """
        return cls(id=str(d["id"]), name=str(d.get("name", "")), statement=str(d.get("statement", "")).strip())


@dataclass
class Source:
    """A document targets are defined in, and the headings that mark them. A map may list several; a target names one by id."""

    id: str
    path: str
    target_heading: str
    exit_section: str = ""
    criteria_section: str = ""
    label: str = ""
    exit_line: str = ""
    checklist_line: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> Source:
        """Build the record from its parsed YAML mapping.

        Args:
            d: the mapping as YAML parsed it.

        Returns:
            The Source record.
        """
        return cls(id=str(d["id"]), path=str(d["path"]), target_heading=str(d["target_heading"]), label=str(d.get("label", "")),
                   exit_section=str(d.get("exit_section", "")), criteria_section=str(d.get("criteria_section", "")),
                   exit_line=str(d.get("exit_line", "")), checklist_line=str(d.get("checklist_line", "")))


@dataclass
class Changelog:
    """The project's change log, and the heading pattern of one entry (a regex with a `stamp` group). Entries are what the
    project logs as done; an entry that names a target after the target was last reviewed means the map is behind."""

    path: str
    entry_heading: str
    stamp_format: str = "%Y%m%d_%H%M"
    started_only: bool = False

    @classmethod
    def from_dict(cls, d: dict | None) -> Changelog | None:
        """Build the record from its parsed YAML mapping.

        Args:
            d: the mapping as YAML parsed it (None or empty for an absent block).

        Returns:
            The Changelog record.
        """
        if not d:
            return None
        return cls(path=str(d["path"]), entry_heading=str(d["entry_heading"]), stamp_format=str(d.get("stamp_format", "%Y%m%d_%H%M")),
                   started_only=bool(d.get("started_only", False)))


@dataclass
class Embed:
    """A page that carries the summary table between the target-map markers, beside its own hand-written text."""

    path: str
    heading: str = ""
    wrap_width: int = WRAP_WIDTH

    @classmethod
    def from_dict(cls, d: dict) -> Embed:
        """Build the record from its parsed YAML mapping.

        Args:
            d: the mapping as YAML parsed it.

        Returns:
            The Embed record.
        """
        return cls(path=str(d["path"]), heading=str(d.get("heading", "")), wrap_width=int(d.get("wrap_width", WRAP_WIDTH) or 0))


@dataclass
class TargetMap:
    """The whole map: its sources, goals and targets, where it renders and how its words read."""

    title: str
    sources: list[Source]
    render_to: str
    updated: dt.date
    stale_after_days: int
    goals: list[Goal]
    targets: list[Target]
    current_state_intro: str = ""
    current_state_diagram: str = ""
    label_target: str = "Target"
    label_section: str = "Targets"
    roadmap_file: str = ""
    changelog: Changelog | None = None
    embeds: list[Embed] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> TargetMap:
        """Build the record from its parsed YAML mapping.

        Args:
            d: the mapping as YAML parsed it.

        Returns:
            The TargetMap record.
        """
        cur = d.get("current_state") or {}
        labels = d.get("labels") or {}
        up = d.get("updated")
        return cls(title=str(d.get("title", "")), sources=[Source.from_dict(x) for x in d.get("sources") or []], render_to=str(d.get("render_to", "")),
                   label_target=str(labels.get("target", "Target")), label_section=str(labels.get("section", "Targets")),
                   roadmap_file=str(d.get("roadmap_file", "")), changelog=Changelog.from_dict(d.get("changelog")),
                   embeds=[Embed.from_dict(e) for e in d.get("embed") or []],
                   updated=up if isinstance(up, dt.date) else dt.date.fromisoformat(str(up)),
                   stale_after_days=int(d.get("stale_after_days", 7)),
                   goals=[Goal.from_dict(g) for g in d.get("goals", [])],
                   targets=[Target.from_dict(t) for t in d.get("targets", [])],
                   current_state_intro=str(cur.get("intro", "")).strip(), current_state_diagram=str(cur.get("diagram", "")).rstrip())

    @classmethod
    def load(cls, path: Path) -> TargetMap:
        """Read and build the map from a file.

        Args:
            path: the target-map.yaml file.

        Returns:
            The TargetMap record.
        """
        return cls.from_dict(yaml.safe_load(path.read_text(encoding="utf-8")))


@dataclass
class Definition:
    """A target's name, exit condition and criteria text: read from the source document, or taken from the map inline."""

    id: str
    name: str
    exit_condition: str
    given: str
    criteria: dict[int, str]
    ticked: frozenset[int] = frozenset()


# ---------------------------------------------------------------------------------------------------------------- readers


class SourceReader:
    """Reads target definitions from a markdown document, using the headings the map's `source` block names.

    `target_heading` is a regex with `id` and `name` groups matched per line; a target runs to the next such heading. Inside
    it, the exit and criteria sections run from their `#` heading to the next heading of any level. The one non-obvious
    choice: a criterion's indented continuation lines are joined, so a wrapped criterion is one row, and its trailing `;`
    or `.` is dropped and its first letter raised, as a table cell reads. Text before the first numbered item is the
    criteria's precondition ("Given ...").

    A plan that writes each target as bold-lead bullets instead (`- **Target:** ...`, `- **Completion checklist:** [x] a · [ ] b`)
    names those leads in `exit_line` and `checklist_line`: the lead line and its indented continuation lines are read, each
    `[ ]` or `[x]` item is a criterion numbered in order, and an item stops at its first full stop, so trailing prose such as
    "Results: [report](...)" is not taken into the last item (2026-10-21, smc-resiliency's stage plans). An `[x]` is recorded as
    ticked, so the validator can warn when the map's verdict disagrees.
    """

    def __init__(self, text: str, source: Source) -> None:
        """Hold one source document and its heading rules.

        Args:
            text: the document's markdown.
            source: the map's source block naming the heading pattern and section titles.
        """
        self.text, self.source = text, source

    def definitions(self) -> dict[str, Definition]:
        """Read every target the document defines.

        Returns:
            Definitions keyed by the id the heading pattern captured, in document order.
        """
        head = re.compile(self.source.target_heading, re.M)
        heads = list(head.finditer(self.text))
        out: dict[str, Definition] = {}
        for i, m in enumerate(heads):
            end = heads[i + 1].start() if i + 1 < len(heads) else len(self.text)
            body = self.text[m.end():end]
            given, criteria = self._criteria(self._section(body, self.source.criteria_section))
            exit_text = " ".join(l.lstrip("> ").strip() for l in self._section(body, self.source.exit_section).splitlines() if l.strip())
            ticked: frozenset[int] = frozenset()
            if self.source.exit_line and not exit_text:
                exit_text = self._lead(body, self.source.exit_line)
            if self.source.checklist_line and not criteria:
                criteria, ticked = self._checklist(self._lead(body, self.source.checklist_line))
            tid = m.group("id").strip()
            out[tid] = Definition(id=tid, name=m.group("name").strip(), exit_condition=exit_text, given=given, criteria=criteria, ticked=ticked)
        return out

    @staticmethod
    def _section(body: str, title: str) -> str:
        """The text under a heading titled `title`, to the next heading of any level.

        Args:
            body: one target's text.
            title: the heading title; empty means none.

        Returns:
            The section text, or "" when absent.
        """
        if not title:
            return ""
        m = re.search(rf"^#+ {re.escape(title)}\s*\n(.*?)(?=^#|\Z)", body, re.M | re.S)
        return m.group(1) if m else ""

    @staticmethod
    def _lead(body: str, title: str) -> str:
        """The text of a bold-lead line (`- **Title:** text` or `**Title:** text`) with its indented continuation lines, joined.

        Args:
            body: one target's text.
            title: the bold lead without its colon.

        Returns:
            The joined text after the lead, or "" when the target has no such line.
        """
        m = re.search(rf"^(?:- )?\*\*{re.escape(title)}:\*\*(.*(?:\n[ \t]+\S.*)*)", body, re.M)
        return " ".join(m.group(1).split()) if m else ""

    @staticmethod
    def _checklist(text: str) -> tuple[dict[int, str], frozenset[int]]:
        """Split a one-line checklist into numbered criteria.

        Args:
            text: the checklist text, e.g. `[x] key made (2026-10-20) · [ ] bootloader recorded.`

        Returns:
            (criteria by number from 1, the numbers ticked `[x]`).
        """
        parts = re.split(r"\[([ xX])\]", text)
        items: dict[int, str] = {}
        ticked: set[int] = set()
        for n, (mark, item) in enumerate(zip(parts[1::2], parts[2::2]), 1):
            item = re.split(r"\.(?:\s|$)", item.strip().rstrip("·").strip(), maxsplit=1)[0]
            items[n] = tidy(item)
            if mark in "xX":
                ticked.add(n)
        return items, frozenset(ticked)

    @staticmethod
    def _criteria(block: str) -> tuple[str, dict[int, str]]:
        """Read a numbered criteria list and the precondition text before it.

        Args:
            block: the criteria section's text.

        Returns:
            (the precondition without its colon, criteria text by number).
        """
        given: list[str] = []
        items: dict[int, list[str]] = {}
        current: int | None = None
        for line in block.splitlines():
            m = re.match(r"^(\d+)\. (.*)$", line)
            if m:
                current = int(m.group(1))
                items[current] = [m.group(2).strip()]
            elif current is not None and line.startswith((" ", "\t")) and line.strip():
                items[current].append(line.strip())
            elif current is None and line.strip():
                given.append(line.strip())
        return " ".join(given).rstrip(":"), {n: tidy(" ".join(parts)) for n, parts in items.items()}


def tidy(text: str) -> str:
    """A criterion as a table cell reads: one line, no trailing `;` or `.`, first letter raised.

    Args:
        text: the criterion as written.

    Returns:
        The tidied text.
    """
    s = " ".join(text.split()).rstrip(";.").strip()
    return s[:1].upper() + s[1:]


def resolve(tmap: TargetMap, source_defs: dict[str, dict[str, Definition]]) -> dict[str, Definition]:
    """Each target's definition, keyed by map id: from its source by `key`, or written inline when it has no source.

    A target whose source or key cannot be found is left out; TargetMapValidator reports it, the renderer shows `?`.

    Args:
        tmap: the map.
        source_defs: definitions read from each source, keyed by source id.

    Returns:
        Definitions keyed by map target id.
    """
    out: dict[str, Definition] = {}
    for t in tmap.targets:
        if t.source:
            d = source_defs.get(t.source, {}).get(t.key)
            if d:
                out[t.id] = d
        else:
            out[t.id] = Definition(id=t.id, name=t.name, exit_condition=t.exit_condition, given="",
                                   criteria={c.n: tidy(c.text) for c in t.criteria if c.text})
    return out


#: joins the live change log and its archives so the entry parser can split them again
ARCHIVE_BOUNDARY = "\n<!-- target_map: archive boundary -->\n"


def changelog_entries(text: str, cl: Changelog) -> list[tuple[dt.datetime, str, str]]:
    """(stamp, heading, body) per change-log entry; an entry runs to the next heading the pattern matches. The Contents list
    is not an entry, because only lines the heading pattern matches start one.

    Args:
        text: one change-log file's text.
        cl: the map's changelog block (heading pattern and stamp format).

    Returns:
        One (stamp, heading line, body) tuple per entry whose stamp parses.
    """
    heads = [m for m in re.finditer(cl.entry_heading, text, re.M)]
    out = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        line_end = text.find("\n", m.start())
        heading = text[m.start():line_end if line_end != -1 else end]
        try:
            stamp = dt.datetime.strptime(m.group("stamp"), cl.stamp_format)
        except ValueError:
            continue
        out.append((stamp, heading, text[m.end():end]))
    return out


# ---------------------------------------------------------------------------------------------------------------- schema

MANDATORY, RECOMMENDED, OPTIONAL, REJECTED = "mandatory", "recommended", "optional", "rejected"
LEVELS = (MANDATORY, RECOMMENDED, OPTIONAL, REJECTED)


@dataclass(frozen=True)
class Field:
    """One schema field: its level, what it holds, and why it sits at that level (every level has a reason, rejected included)."""

    level: str
    meaning: str
    reason: str


#: Every field the map may carry, and every field deliberately refused, each with a level and the reason for it. Data, not
#: code: SchemaCheck enforces it and `--schema` prints it, so the reference cannot drift from the rules. A level followed by
#: "when ..." is conditional: optional in general, mandatory (or recommended) under the condition, which TargetMapValidator
#: enforces. A rejected field fails the check with its reason, so a refused idea is not re-added by the next author.
SCHEMA: dict[str, dict[str, Field]] = {
    "map": {
        "schema": Field(MANDATORY, "schema version; 1", "a later change to the format must be detectable, not guessed"),
        "title": Field(MANDATORY, "title of the rendered tracker", "the rendered file needs a heading and front matter"),
        "render_to": Field(MANDATORY, "repo-relative path of the rendered markdown", "the check compares this file byte for byte"),
        "updated": Field(MANDATORY, "date the map was last reviewed as a whole", "a reader must see how old the picture is"),
        "goals": Field(MANDATORY, "why the project exists; at least one", "a target without a goal is work nobody can justify"),
        "targets": Field(MANDATORY, "the targets, in rendered order; at least one", "they are what the map tracks"),
        "roadmap_file": Field(RECOMMENDED, "the project's roadmap", "ties each started target to a milestone line, so the roadmap cannot fall silent"),
        "changelog": Field(RECOMMENDED, "{path, entry_heading, stamp_format}: the project's change log",
                           "work is logged there; an entry naming a target after its last review is how a stale map is caught"),
        "current_state": Field(RECOMMENDED, "a diagram of what exists now", "plans draw the target; readers also need what is actually built"),
        "sources": Field(OPTIONAL, "documents the targets are defined in; a list, one entry per document",
                         "targets defined in a plan are read from it (one fact, one place); a project may have several plans, or none"),
        "stale_after_days": Field(OPTIONAL, "days a `pending` criterion may go unverified; default 7", "the default suits a weekly rhythm"),
        "labels": Field(OPTIONAL, "words the renderer uses; default `Target` and `Targets`", "projects call targets steps, phases or milestones"),
        "embed": Field(OPTIONAL, "pages that also carry the summary table between the target-map markers: [{path, heading}]",
                       "a page people read first (a plan tracker) can show where each target stands without a second, hand-kept table"),
        "percent_complete": Field(REJECTED, "an overall percentage", "a percentage invites guessing; progress is the criteria's statuses"),
        "source": Field(REJECTED, "a single source document", "replaced by `sources`, a list, because a map may draw targets from several documents"),
        "history": Field(REJECTED, "a log of past states", "history is git and CHANGELOG.md; the map holds the current state only"),
    },
    "source": {
        "id": Field(MANDATORY, "short identifier; targets name their source by it", "joins a target to the document that defines it"),
        "path": Field(MANDATORY, "repo-relative path of the defining document", "nothing can be read without it"),
        "label": Field(RECOMMENDED, "link text for the document", "file names read poorly in prose"),
        "target_heading": Field(MANDATORY, "regex, one line per target, with named groups `id` and `name`",
                                "documents differ in heading style; the pattern is data so the reader stays generic"),
        "exit_section": Field(RECOMMENDED + " unless exit_line", "heading title of each target's exit condition",
                              "without it (or exit_line) the tracker cannot quote the exit condition"),
        "criteria_section": Field(RECOMMENDED + " unless checklist_line", "heading title of each target's numbered criteria",
                                  "without it (or checklist_line) criteria cannot be counted against the source"),
        "exit_line": Field(OPTIONAL, "bold lead of a one-line exit condition (`- **Target:** ...`), read when no exit_section is found",
                           "some plans write a target as bold-lead bullets, not sub-headings"),
        "checklist_line": Field(OPTIONAL, "bold lead of a one-line checklist (`- **Completion checklist:** [x] a · [ ] b`); each item is a criterion",
                                "some plans keep criteria as one checklist line; read in order, numbered from 1"),
    },
    "changelog": {
        "path": Field(MANDATORY, "repo-relative path of the change log", "nothing can be read without it"),
        "entry_heading": Field(MANDATORY, "regex matching one entry's heading, with a named group `stamp`",
                               "change logs differ in heading style; the pattern is data so the reader stays generic"),
        "stamp_format": Field(OPTIONAL, "strptime format of `stamp`; default %Y%m%d_%H%M", "the default is the workspace's timestamp suffix"),
        "started_only": Field(OPTIONAL, "true: the change-log rule applies only to started targets; default false",
                              "a plan's later stages are named in the log long before they start; reviewing them for every mention is noise "
                              "(operator, 2026-10-21, smc-resiliency)"),
    },
    "embed": {
        "path": Field(MANDATORY, "repo-relative page holding the target-map markers once", "nothing can be written without it"),
        "heading": Field(OPTIONAL, "a sentence printed above the table inside the block", "a page may want to say where the table comes from"),
        "wrap_width": Field(OPTIONAL, "the table's column budget, wrapped as the markdown hook does; default 200, 0 for one line per row",
                            "a generated table must match the hook's wrapping or the hook and the render keep undoing each other (2026-10-22)"),
    },
    "labels": {
        "target": Field(OPTIONAL, "singular name of a target, e.g. Step, Milestone, Phase", "the default reads correctly everywhere"),
        "section": Field(OPTIONAL, "heading of the per-target section", "the default reads correctly everywhere"),
    },
    "current_state": {
        "diagram": Field(MANDATORY, "fenced verbatim when rendered", "a current_state without a diagram says nothing"),
        "intro": Field(RECOMMENDED, "what the diagram shows and when it was checked", "a diagram without a date cannot be trusted"),
    },
    "goal": {
        "id": Field(MANDATORY, "short identifier, referenced by targets", "targets point at goals by it"),
        "name": Field(MANDATORY, "a few words", "the goals table needs a label"),
        "statement": Field(MANDATORY, "one or two sentences; cite where it comes from", "a goal is its statement"),
    },
    "target": {
        "id": Field(MANDATORY, "unique in the map; matches the source heading's `id` unless `ref` is set", "joins the map to its source and the roadmap"),
        "goal": Field(MANDATORY, "a goal id", "every target serves a goal"),
        "state": Field(MANDATORY, "one of " + ", ".join(TARGET_STATES), "a closed vocabulary keeps states comparable across targets and projects"),
        "exit_met": Field(MANDATORY, "true only when the exit condition is met; agrees with state",
                          "the one yes/no a reader needs first; checked against state so they cannot disagree"),
        "criteria": Field(MANDATORY, "one entry per acceptance criterion; `[]` only when the target's source defines none",
                          "progress is measured criterion by criterion, never by feel"),
        "summary": Field(RECOMMENDED, "where it stands, in a few sentences", "numbers alone do not say what is odd or at risk"),
        "blocker": Field(RECOMMENDED, "what stops it: {owner, text}", "an unowned blocker is not worked"),
        "next": Field(RECOMMENDED + " when started", "the next action: {owner, text}",
                      "a started target without a next action drifts; before it starts the next action is often only to wait"),
        "as_built": Field(RECOMMENDED + " when started", "{intro, diagram}: what exists, marked against the plan",
                          "the plan's diagram shows intent; once work starts, readers need the difference"),
        "evidence": Field(MANDATORY + " when started", "[{label, path | ref}], unless every asserted criterion carries its own",
                          "a started target with no evidence is a claim"),
        "mention": Field(MANDATORY + " when changelog is set, or when started and roadmap_file is set",
                         "the phrase that names this target in the roadmap and the change log, e.g. `Step 4`",
                         "one phrase joins the map to where work is announced (roadmap) and recorded (change log)"),
        "reviewed": Field(MANDATORY + " when changelog is set", "when the target was last reviewed: YYYY-MM-DD HH:MM, or a date (end of day)",
                          "a change-log entry naming the target after this moment fails the check until the target is reviewed again"),
        "source": Field(OPTIONAL, "id of the source this target is defined in; absent means inline",
                        "lets one map mix targets from several documents with inline ones"),
        "ref": Field(OPTIONAL, "the target's id inside its source, when it differs from `id`",
                     "two sources may both define a Step 1; map ids must stay unique"),
        "name": Field(MANDATORY + " when no source", "the target's name; not restated when the target has a source", "one fact, one place"),
        "exit_condition": Field(MANDATORY + " when no source", "not restated when the target has a source",
                                "a target without an exit condition cannot be finished; one fact, one place"),
        "percent_complete": Field(REJECTED, "a per-target percentage", "a percentage invites guessing; criteria statuses carry progress"),
        "rag": Field(REJECTED, "a red/amber/green colour", "restates state and exit_met with less information"),
        "priority": Field(REJECTED, "a priority rank", "order is the rendered order (the plan's sequence); a second ranking would compete with it"),
        "tasks": Field(REJECTED, "task-level work items", "tasks belong in the backlog (governance backlog-md policy); the map stops at criteria"),
    },
    "criterion": {
        "n": Field(MANDATORY, "the criterion's number", "joins the verdict to its text"),
        "status": Field(MANDATORY, "one of " + ", ".join(CRITERION_STATES), "a closed vocabulary keeps verdicts comparable"),
        "verified": Field(MANDATORY + " when pass, partly or pending", "date last checked (YYYY-MM-DD)",
                          "an asserted verdict without a date cannot be judged stale"),
        "evidence": Field(MANDATORY + " when pass, partly or pending", "[{label, path | ref}]", "an asserted verdict without evidence is a claim"),
        "note": Field(MANDATORY + " when partly", "what is shown and what is not; recommended otherwise", "`partly` means nothing unless the gap is named"),
        "text": Field(MANDATORY + " when no source", "the criterion; not restated when the target has a source", "one fact, one place"),
        "owner": Field(REJECTED, "a per-criterion owner", "ownership sits on the target's blocker and next action; per criterion it fragments"),
    },
    "evidence": {
        "path": Field(MANDATORY + " unless ref", "repo-relative path that must exist", "a path can be checked; the check does"),
        "ref": Field(MANDATORY + " unless path", "free text, e.g. a CHANGELOG entry id", "some evidence is not a file"),
        "label": Field(RECOMMENDED, "link text; defaults to the file name", "file names read poorly in prose"),
    },
    "action": {
        "owner": Field(MANDATORY, "one of " + ", ".join(OWNERS), "a filterable owner answers \"what is waiting on me\""),
        "text": Field(MANDATORY, "what, in a sentence; may be empty when owner is none", "an owner with nothing to do is noise"),
    },
}


class SchemaCheck:
    """Checks the raw YAML against SCHEMA before any record is built: missing mandatory fields and unknown fields are problems,
    missing recommended fields are warnings. Conditional levels ("... when ...") are left to TargetMapValidator, which
    knows the conditions."""

    #: (kind, field) pairs where a present empty list is a value, not a gap: a target whose source defines no criteria.
    EMPTY_OK = frozenset({("target", "criteria")})

    def __init__(self, raw: dict) -> None:
        """Hold the parsed map.

        Args:
            raw: the YAML document as parsed.
        """
        self.raw = raw
        self.problems: list[str] = []
        self.warnings: list[str] = []

    def run(self) -> SchemaCheck:
        """Check every object in the map against its SCHEMA entry.

        Returns:
            self, with `problems` and `warnings` filled.
        """
        self._object("map", self.raw, "map")
        for key, kind in (("labels", "labels"), ("current_state", "current_state"), ("changelog", "changelog")):
            if isinstance(self.raw.get(key), dict):
                self._object(kind, self.raw[key], key)
        for src in self._list("sources"):
            self._object("source", src, f"source {src.get('id', '?')}")
        for emb in self._list("embed"):
            self._object("embed", emb, f"embed {emb.get('path', '?')}")
        for g in self._list("goals"):
            self._object("goal", g, f"goal {g.get('id', '?')}")
        for t in self._list("targets"):
            tag = f"target {t.get('id', '?')}"
            self._object("target", t, tag)
            for key in ("blocker", "next"):
                if isinstance(t.get(key), dict):
                    self._object("action", t[key], f"{tag} {key}")
            for e in t.get("evidence") or []:
                self._object("evidence", e, f"{tag} evidence")
            for c in t.get("criteria") or []:
                ctag = f"{tag} criterion {c.get('n', '?')}"
                self._object("criterion", c, ctag)
                for e in c.get("evidence") or []:
                    self._object("evidence", e, f"{ctag} evidence")
        return self

    def _list(self, key: str) -> list[dict]:
        """The mappings in a top-level list field.

        Args:
            key: the map field.

        Returns:
            Its mapping items; [] (and a problem) when the field is not a list.
        """
        value = self.raw.get(key)
        if value is not None and not isinstance(value, list):
            self.problems.append(f"map: `{key}` must be a list")
            return []
        return [v for v in value or [] if isinstance(v, dict)]

    def _object(self, kind: str, obj: dict, tag: str) -> None:
        """Check one object's fields against SCHEMA[kind]; adds to problems and warnings.

        Args:
            kind: the SCHEMA kind (map, source, target, ...).
            obj: the object's mapping.
            tag: how messages name the object.
        """
        spec = SCHEMA[kind]
        for key in obj:
            if key not in spec:
                self.problems.append(f"{tag}: unknown field `{key}` (see --schema)")
            elif spec[key].level == REJECTED:
                self.problems.append(f"{tag}: field `{key}` is rejected: {spec[key].reason}")
        for key, f in spec.items():
            level = f.level
            if level == REJECTED or (key in obj and obj[key] not in (None, "", [])):
                continue
            if (kind, key) in self.EMPTY_OK and obj.get(key) == []:
                continue
            if level == MANDATORY:
                self.problems.append(f"{tag}: mandatory field `{key}` is missing")
            elif level == RECOMMENDED:
                self.warnings.append(f"{tag}: recommended field `{key}` is missing")


def schema_markdown() -> str:
    """SCHEMA as markdown tables, one per object kind: the field reference for the standard and for `--schema`.

    Returns:
        The markdown text.
    """
    out = [f"# {MAP_FILE} fields (schema 1)", "",
           "`mandatory`: the check fails without it. `recommended`: the check warns without it. `optional`: never reported. "
           "`rejected`: considered and refused; the check fails if it appears. A level with \"when ...\" applies only under that "
           "condition; otherwise the field is optional. Every field carries the reason for its level.", ""]
    for kind, spec in SCHEMA.items():
        out += [f"## {kind}", "", "| Field | Level | Meaning | Reason |", "| --- | --- | --- | --- |"]
        out += [f"| `{k}` | {f.level} | {f.meaning} | {f.reason} |" for k, f in spec.items()]
        out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------------------------- rules


class TargetMapValidator:
    """The rules SCHEMA cannot state alone: vocabularies, agreement between fields, conditional levels, the source document
    and the roadmap. `today` is injected so staleness is testable."""

    def __init__(self, tmap: TargetMap, source_defs: dict[str, dict[str, Definition]], roadmap: str | None, root: Path,
                 today: dt.date, changelog: str | None = None) -> None:
        """Hold the map and everything it is checked against.

        Args:
            tmap: the map.
            source_defs: definitions read from each source, keyed by source id.
            roadmap: the roadmap's text, or None when absent.
            root: the project root, for evidence paths.
            today: the date staleness is judged against.
            changelog: the change log and its archives joined by ARCHIVE_BOUNDARY, or None when absent.
        """
        self.m, self.source_defs, self.roadmap, self.root, self.today = tmap, source_defs, roadmap, root, today
        self.changelog = changelog
        self.warnings: list[str] = []

    def problems(self) -> list[str]:
        """Every rule breach; warnings collect on `self.warnings` as a side effect.

        Returns:
            The problems, each one line.
        """
        out: list[str] = []
        ids = [t.id for t in self.m.targets]
        if len(set(ids)) != len(ids):
            out.append("target ids are not unique")
        source_ids = [src.id for src in self.m.sources]
        if len(set(source_ids)) != len(source_ids):
            out.append("source ids are not unique")
        for src in self.m.sources:
            for have, alt, name in ((src.exit_section, src.exit_line, "exit_section"), (src.criteria_section, src.checklist_line, "criteria_section")):
                if not have and not alt:
                    self.warnings.append(f"source {src.id}: recommended field `{name}` is missing")
            tracked = {t.key for t in self.m.targets if t.source == src.id}
            defined = set(self.source_defs.get(src.id, {}))
            if src.id in self.source_defs and not defined:
                out.append(f"source {src.id}: `target_heading` matched nothing in {src.path}")
            for key in sorted(defined - tracked):
                out.append(f"source {src.id} defines `{key}` but no target tracks it")
        goal_ids = {g.id for g in self.m.goals}
        for g in self.m.goals:
            if not any(t.goal == g.id for t in self.m.targets):
                out.append(f"goal {g.id} has no target")
        if self.m.roadmap_file and self.roadmap is None:
            out.append(f"roadmap_file `{self.m.roadmap_file}` does not exist")
        if (self.today - self.m.updated).days > self.m.stale_after_days:
            out.append(f"map `updated` {self.m.updated} is over {self.m.stale_after_days} days old; review the whole map and set it")
        out += self._changelog_rule()
        named = self._roadmap_leads()
        for t in self.m.targets:
            out += self._target(t, goal_ids, named)
        return out

    def _changelog_rule(self) -> list[str]:
        """An entry stamped after a target's `reviewed` moment that names the target means the map has not caught up.

        Matching is by the target's `mention` as a whole phrase, so `Step 5` does not match `Step 50`; an entry that
        describes the work without the phrase is not caught (the known limit of this rule). With `started_only`, a target
        still `not started` is exempt: its name turns up in plans long before work on it does.

        Returns:
            One problem per target behind its change log, plus any that cannot be judged.
        """
        if not self.m.changelog:
            return []
        if self.changelog is None:
            return [f"changelog `{self.m.changelog.path}` does not exist"]
        out: list[str] = []
        # each file is parsed on its own: joined, the live log's last entry ran on into an archive's index (2026-10-10)
        entries = [e for part in self.changelog.split(ARCHIVE_BOUNDARY) for e in changelog_entries(part, self.m.changelog)]
        if not entries:
            out.append(f"changelog: `entry_heading` matched nothing in {self.m.changelog.path}")
        for t in self.m.targets:
            if not t.mention or t.reviewed is None:
                out.append(f"target {t.id}: `mention` and `reviewed` are mandatory when changelog is set")
                continue
            if self.m.changelog.started_only and t.state == "not started":
                continue
            phrase = re.compile(rf"(?<![\w-]){re.escape(t.mention)}(?![\w-])")
            later = [stamp for stamp, heading, body in entries if stamp > t.reviewed and phrase.search(heading + body)]
            if later:
                newest = max(later).strftime(self.m.changelog.stamp_format)
                out.append(f"target {t.id}: {len(later)} change-log entr{'y' if len(later) == 1 else 'ies'} after its review "
                           f"({t.reviewed:%Y-%m-%d %H:%M}) name `{t.mention}`, newest {newest}; review the target and set `reviewed`")
        return out

    def _roadmap_leads(self) -> dict[str, list[bool]]:
        """Bold leads of the roadmap's task lines, keyed by each target's `mention` they contain, with the tick state.

        Returns:
            For each mention found, the tick state of every line naming it.
        """
        found: dict[str, list[bool]] = {}
        for tick, lead in re.findall(r"^- \[([ x])\] \*\*(.*?)\*\*", self.roadmap or "", re.M):
            for t in self.m.targets:
                if t.mention and re.search(rf"\b{re.escape(t.mention)}\b", lead):
                    found.setdefault(t.mention, []).append(tick == "x")
        return found

    def _target(self, t: Target, goal_ids: set[str], named: dict[str, list[bool]]) -> list[str]:
        """The rules for one target.

        Args:
            t: the target.
            goal_ids: the goals defined.
            named: the roadmap's bold leads by mention (from _roadmap_leads).

        Returns:
            The target's problems.
        """
        out: list[str] = []
        tag = f"target {t.id}"
        started = t.state != "not started"
        if t.goal not in goal_ids:
            out.append(f"{tag}: goal `{t.goal}` is not defined")
        if t.state not in TARGET_STATES:
            out.append(f"{tag}: state `{t.state}` is outside the vocabulary")
        elif t.exit_met != (t.state in ("exit met", "done")):
            out.append(f"{tag}: exit_met {str(t.exit_met).lower()} disagrees with state `{t.state}`")
        for a, what in ((t.blocker, "blocker"), (t.next, "next")):
            if a.owner not in OWNERS:
                out.append(f"{tag}: {what} owner `{a.owner}` is outside the vocabulary")
        out += self._definition_rules(t, tag)
        for e in t.evidence:
            out += self._evidence(e, tag)
        for c in t.criteria:
            out += self._criterion(c, f"{tag} criterion {c.n}")
        if any(named.get(t.mention, [])) and t.state != "done":
            out.append(f"{tag}: {self.m.roadmap_file} ticks a line naming `{t.mention}`, but the state is `{t.state}`")
        if started:
            if not t.evidence and not all(c.evidence for c in t.criteria if c.status in ASSERTED):
                out.append(f"{tag}: evidence is mandatory once started")
            if not t.evidence and not any(c.status in ASSERTED for c in t.criteria):
                out.append(f"{tag}: evidence is mandatory once started")
            if self.m.roadmap_file and (not t.mention or t.mention not in named):
                out.append(f"{tag}: `{t.state}` but no task line in {self.m.roadmap_file} names `{t.mention}` in its bold lead")
            if not t.as_built_diagram:
                self.warnings.append(f"{tag}: recommended field `as_built` is missing (started)")
            if not t.next.text:
                self.warnings.append(f"{tag}: recommended field `next` is missing (started)")
        return out

    def _definition_rules(self, t: Target, tag: str) -> list[str]:
        """Where a target's definition comes from: a source it must match, or inline fields it must carry.

        Args:
            t: the target.
            tag: how messages name it.

        Returns:
            The problems; tick disagreements on a checklist source go to `self.warnings`.
        """
        out: list[str] = []
        if t.source:
            if t.name or t.exit_condition or any(c.text for c in t.criteria):
                out.append(f"{tag}: name, exit_condition and criterion text come from source {t.source}; do not restate them")
            if t.source not in {src.id for src in self.m.sources}:
                out.append(f"{tag}: source `{t.source}` is not listed under `sources`")
            elif t.source in self.source_defs:
                d = self.source_defs[t.source].get(t.key)
                if d is None:
                    out.append(f"{tag}: `{t.key}` is not defined in source {t.source}")
                elif sorted(c.n for c in t.criteria) != sorted(d.criteria):
                    out.append(f"{tag}: criteria {sorted(c.n for c in t.criteria)} differ from the source's {sorted(d.criteria)}")
                elif any(src.id == t.source and src.checklist_line for src in self.m.sources):
                    for c in t.criteria:
                        if (c.n in d.ticked) != (c.status == "pass"):
                            self.warnings.append(f"{tag} criterion {c.n}: the source {'ticks' if c.n in d.ticked else 'does not tick'} it "
                                                 f"but the map says `{c.status}`")
        else:
            if t.ref:
                out.append(f"{tag}: `ref` needs a `source`")
            if not t.name or not t.exit_condition:
                out.append(f"{tag}: name and exit_condition are mandatory when no source is set")
            if any(not c.text for c in t.criteria):
                out.append(f"{tag}: criterion text is mandatory when no source is set")
            if not t.criteria:
                out.append(f"{tag}: an inline target needs at least one criterion")
        return out

    def _criterion(self, c: Criterion, tag: str) -> list[str]:
        """The rules for one criterion verdict.

        Args:
            c: the criterion.
            tag: how messages name it.

        Returns:
            Its problems.
        """
        out: list[str] = []
        if c.status not in CRITERION_STATES:
            out.append(f"{tag}: status `{c.status}` is outside the vocabulary")
        if c.status in ASSERTED:
            if not c.evidence:
                out.append(f"{tag}: evidence is mandatory when `{c.status}`")
            if c.verified is None:
                out.append(f"{tag}: verified is mandatory when `{c.status}`")
        if c.status == "partly" and not c.note:
            out.append(f"{tag}: note is mandatory when `partly` (say what is not shown)")
        if c.status == "pending" and c.verified and (self.today - c.verified).days > self.m.stale_after_days:
            out.append(f"{tag}: `pending` last verified {c.verified}, over {self.m.stale_after_days} days ago; re-check it")
        for e in c.evidence:
            out += self._evidence(e, tag)
        return out

    def _evidence(self, e: Evidence, tag: str) -> list[str]:
        """One evidence item names exactly one of path or ref, and its path exists.

        Args:
            e: the evidence.
            tag: how messages name its owner.

        Returns:
            Its problems.
        """
        if bool(e.path) == bool(e.ref):
            return [f"{tag}: evidence needs exactly one of `path` or `ref`"]
        if e.path and not (self.root / e.path).exists():
            return [f"{tag}: evidence path `{e.path}` does not exist"]
        return []


# ---------------------------------------------------------------------------------------------------------------- render


class TrackerRenderer:
    """Renders the tracker markdown. Deterministic: the same map and definitions always give the same bytes, so the check can compare.

    Prose is wrapped at 200 columns (the workspace markdown rule) here rather than by an editor hook, because a hook never
    sees a file a script writes; tables are single-line rows and diagrams are fenced, both exempt from wrapping.
    """

    def __init__(self, tmap: TargetMap, defs: dict[str, Definition]) -> None:
        """Hold the map and its resolved definitions.

        Args:
            tmap: the map.
            defs: each target's definition, keyed by map id (from resolve()).
        """
        self.m, self.defs = tmap, defs
        self.here = Path(tmap.render_to).parent
        self.word = tmap.label_target

    def render(self) -> str:
        """The tracker file's whole text.

        Returns:
            The markdown, ending in one newline.
        """
        m, w = self.m, self.word
        front = ["---", f"Title: {m.title}", "Category: living-tracker", "Status: current", "Authority: local-supplement"]
        if m.sources:
            front.append(("Plan: " if len(m.sources) == 1 else "Sources: ") + ", ".join(src.path for src in m.sources))
        front += [f"Source of truth: {MAP_FILE}", f"Last reviewed: {m.updated.isoformat()}",
                  f"Summary: Generated from {MAP_FILE} by the target-map renderer; do not edit by hand. Where each {w.lower()} stands against its exit "
                  "condition and each of its acceptance criteria.", "---", "", f"# {m.title}", ""]
        out = front
        intro = (f"**Generated; do not edit.** The source is [`{MAP_FILE}`]({self._rel(MAP_FILE)}); change it and render again. The check fails when "
                 "this file differs from what the map renders.")
        if m.sources:
            links = ", ".join(self._source_link(src) for src in m.sources)
            intro += (f" Names, exit conditions and criteria text come from {links}; for those {w.lower()}s the map holds only numbers and "
                      "verdicts.")
        out += self._para(intro)
        sec = m.label_section
        out += ["## Contents", "", "- [How to read this file](#how-to-read-this-file)", "- [Goals](#goals)", "- [Summary](#summary)"]
        if m.current_state_diagram:
            out.append("- [Current state, as built](#current-state-as-built)")
        out += [f"- [{sec}](#{self._slug(sec)})", "", "## How to read this file", ""]
        out += self._para(f"*Exit met* is `yes` only when the {w.lower()}'s own exit condition, quoted in its section, is met; nothing else counts. "
                          "*State* is one of:")
        out += [f"- `not started`: no work under this {w.lower()}.",
                "- `groundwork`: pieces built or decided, but no acceptance criterion attempted on the real target.",
                "- `in progress`: acceptance criteria being worked; some may pass.",
                f"- `exit met`: the exit condition is met; later work may still hang off the {w.lower()}.",
                f"- `done`: exit met and nothing further under this {w.lower()}.", ""]
        out += self._para(f"Each {w.lower()}'s table lists its acceptance criteria verbatim. *Status* is one of `pass`, `partly` (some of the criterion "
                          "shown, the rest named in the note), `pending` (under way, result not in yet) or `not run`; `pass`, `partly` and `pending` carry "
                          f"their own evidence and the date last verified, and a `pending` older than {m.stale_after_days} days fails the check. A note says "
                          "where a `pass` was shown when that was not the production target.")
        out += ["## Goals", "", f"| Goal | Name | Statement | {w}s |", "| --- | --- | --- | --- |"]
        for g in m.goals:
            members = ", ".join(t.id for t in m.targets if t.goal == g.id)
            out.append(f"| {g.id} | {self._cell(g.name)} | {self._cell(g.statement)} | {members} |")
        out += ["", "## Summary", "", f"| {w} | Name | Goal | Exit met | State | Blocker |", "| --- | --- | --- | --- | --- | --- |"]
        for t in m.targets:
            out.append(f"| {t.id} | {self._cell(self._def(t).name)} | {t.goal} | {'yes' if t.exit_met else 'no'} | {t.state} | {self._action(t.blocker)} |")
        out.append("")
        if m.current_state_diagram:
            out += ["## Current state, as built", ""]
            out += self._para(m.current_state_intro)
            out += ["```text", m.current_state_diagram, "```", ""]
        out += [f"## {sec}", ""]
        for t in m.targets:
            out += self._target(t)
        return "\n".join(out).rstrip() + "\n"

    def embed_block(self, embed: Embed) -> str:
        """The summary table for a page that embeds it, markers included: one row per target, each id linking to its section.

        Args:
            embed: the page and the sentence to print above the table.

        Returns:
            The block, from EMBED_BEGIN to EMBED_END, without a trailing newline.
        """
        page_dir = Path(embed.path).parent
        tracker = os.path.relpath(self.m.render_to, page_dir).replace(os.sep, "/")
        w = self.word
        out = [EMBED_BEGIN]
        if embed.heading:
            out += self._para(embed.heading)
        table = [f"| {w} | Name | State | Exit met | Where it stands | Blocker | Next action |", "| --- | --- | --- | --- | --- | --- | --- |"]
        for t in self.m.targets:
            name = self._def(t).name
            anchor = self._slug(f"{w} {t.id} — {name}")
            nxt = self._action(t.next) if t.next.text else ""
            table.append(f"| [{t.id}]({tracker}#{anchor}) | {self._cell(name)} | {t.state} | {'yes' if t.exit_met else 'no'} | {self._cell(t.summary)} | "
                         f"{self._action(t.blocker)} | {nxt} |")
        out += wrap_table("\n".join(table), embed.wrap_width).split("\n")   # wrapped as the markdown hook wraps it (2026-10-22)
        out.append(EMBED_END)
        return "\n".join(out)

    def _source_link(self, src: Source) -> str:
        """A markdown link to a source document, relative to the tracker.

        Args:
            src: the source.

        Returns:
            The link.
        """
        return f"[{src.label or Path(src.path).name}]({self._rel(src.path)})"

    def _def(self, t: Target) -> Definition:
        """A target's definition, or a `?` placeholder when its source lacks it.

        Args:
            t: the target.

        Returns:
            The definition.
        """
        return self.defs.get(t.id) or Definition(id=t.id, name="?", exit_condition="", given="", criteria={})

    def _target(self, t: Target) -> list[str]:
        """One target's section: heading, exit condition, summary, criteria table, as built, evidence and next action.

        Args:
            t: the target.

        Returns:
            The section's lines.
        """
        d = self._def(t)
        out = [f"### {self.word} {t.id} — {d.name}", ""]
        if len(self.m.sources) > 1:
            src = next((x for x in self.m.sources if x.id == t.source), None)
            out += self._para(f"Defined in {self._source_link(src)}." if src else "Defined inline in the map.")
        if d.exit_condition:
            out += self._para(f"Exit condition: \"{d.exit_condition}\"")
        out += self._para(t.summary)
        if d.given:
            out += self._para(f"*{d.given}:*")
        if t.criteria:
            out += ["| # | Acceptance criterion | Status | Verified | Evidence | Note |", "| --- | --- | --- | --- | --- | --- |"]
            for c in sorted(t.criteria, key=lambda x: x.n):
                out.append(f"| {c.n} | {self._cell(d.criteria.get(c.n, '?'))} | {c.status} | {c.verified.isoformat() if c.verified else ''} | "
                           f"{self._evidence_list(c.evidence)} | {self._cell(c.note)} |")
            out.append("")
        else:
            out += self._para(f"The source writes no acceptance criteria for this {self.word.lower()} yet.")
        if t.as_built_diagram:
            out += self._para(t.as_built_intro)
            out += ["```text", t.as_built_diagram, "```", ""]
        if t.evidence:
            out += self._para(f"Evidence: {self._evidence_list(t.evidence)}.")
        if t.next.text:
            out += self._para(f"Next action ({t.next.owner}): {t.next.text}")
        return out

    def _action(self, a: Action) -> str:
        """An action as a table cell: `owner: text`, or the text alone when nobody owns it.

        Args:
            a: the action.

        Returns:
            The cell text.
        """
        return self._cell(f"{a.owner}: {a.text}" if a.owner != "none" else a.text)

    def _evidence_list(self, items: list[Evidence]) -> str:
        """Evidence items as comma-separated links or references.

        Args:
            items: the evidence.

        Returns:
            The text.
        """
        parts = []
        for e in items:
            if e.path:
                parts.append(f"[{e.label or Path(e.path).name}]({self._rel(e.path)})")
            else:
                parts.append(f"{e.label + ': ' if e.label else ''}{e.ref}")
        return ", ".join(parts)

    def _rel(self, path: str) -> str:
        """A repo-relative path as a link relative to the tracker.

        Args:
            path: repo-relative path.

        Returns:
            The relative link target.
        """
        return os.path.relpath(path, self.here).replace(os.sep, "/")

    @staticmethod
    def _slug(heading: str) -> str:
        """A heading's anchor as GitHub and VS Code make it.

        Args:
            heading: the heading text.

        Returns:
            The anchor without `#`.
        """
        return re.sub(r"[^a-z0-9 -]", "", heading.lower()).replace(" ", "-")

    @staticmethod
    def _cell(text: str) -> str:
        """Text as one table cell: one line, pipes escaped.

        Args:
            text: the text.

        Returns:
            The cell.
        """
        return " ".join(text.split()).replace("|", "\\|")

    @staticmethod
    def _para(text: str) -> list[str]:
        """A paragraph wrapped at WRAP columns, followed by a blank line.

        Args:
            text: the paragraph.

        Returns:
            Its lines; [] for empty text.
        """
        text = " ".join(text.split())
        if not text:
            return []
        return textwrap.wrap(text, width=WRAP, break_long_words=False, break_on_hyphens=False) + [""]


# ---------------------------------------------------------------------------------------------------------------- starter and sync

#: A value a person must replace. `--init` and `--sync` write it where only a person can decide (a goal, a name, a title);
#: `placeholders()` makes the check fail while any is left, so a generated map cannot pass as a reviewed one.
PLACEHOLDER = "TODO"
DEFAULT_RENDER_TO = "docs/trackers/target-tracker.md"
STARTER_HEADER = """\
# target-map.yaml — the source of truth for this project's goals, its targets and where each stands; the tracker is rendered from it.
# Generated by skill-ai-it `target_map.py --init` on {date}. Hand-authored from here on: no script rewrites it (`--sync` only appends).
# Replace every value starting with TODO (the check fails while one is left), then run `just target-map` (target_map.py --write).
# Structure: goals <- targets <- criteria. A target starts `not started` with every criterion `not run`; a status above
# `not run` needs `verified` and `evidence`. Field levels and reasons: `just target-map --schema`.
# When the plan gains a heading, `target_map.py --sync` shows it as a `not started` target; `--sync --write` appends it (existing ones untouched).
"""


class InitError(ValueError):
    """`--init` cannot build a starter map from what it was given."""


class SyncError(ValueError):
    """`--sync` cannot append to this map without risking its hand-written content."""


def placeholders(raw: object, path: str = "map") -> list[str]:
    """Every string value that still starts with PLACEHOLDER, as a problem. Only a leading TODO counts, so prose may mention one.

    Args:
        raw: the parsed map, or any value inside it.
        path: how messages name where `raw` sits.

    Returns:
        One problem per placeholder left.
    """
    out: list[str] = []
    if isinstance(raw, dict):
        for k, v in raw.items():
            out += placeholders(v, f"{path}.{k}")
    elif isinstance(raw, list):
        for i, v in enumerate(raw):
            tag = v.get("id", v.get("n", i)) if isinstance(v, dict) else i
            out += placeholders(v, f"{path}[{tag}]")
    elif isinstance(raw, str) and raw.strip().startswith(PLACEHOLDER):
        out.append(f"{path}: placeholder `{raw.strip()[:40]}` left in; replace it")
    return out


def starter_target(tid: str, goal: str, criteria: list[int], label: str, source: str = "", now: dt.datetime | None = None,
                   inline: bool = False) -> dict:
    """One target as `--init` and `--sync` write it: not started, every criterion `not run`, nothing asserted.

    Args:
        tid: the target id.
        goal: the goal id (a PLACEHOLDER from --sync).
        criteria: the criterion numbers; may be empty when the source writes none.
        label: what the project calls a target, for `mention`.
        source: the source id; empty for inline.
        now: the `reviewed` moment; None leaves it out (no changelog).
        inline: write placeholder name, exit condition and criterion text.

    Returns:
        The target as a mapping.
    """
    t: dict = {"id": tid}
    if source:
        t["source"] = source
    t |= {"goal": goal, "state": "not started", "exit_met": False, "mention": f"{label} {tid}"}
    if now is not None:
        t["reviewed"] = now.strftime("%Y-%m-%d %H:%M")
    if inline:
        t |= {"name": f"{PLACEHOLDER} name", "exit_condition": f"{PLACEHOLDER} the condition that finishes this target"}
    t["summary"] = "Not started."
    t["criteria"] = [{"n": n, "status": "not run"} | ({"text": f"{PLACEHOLDER} criterion {n}"} if inline else {}) for n in criteria]
    return t


def _dump(obj: object) -> str:
    """YAML text for a starter map or appended targets, in field order and unwrapped.

    Args:
        obj: the value to dump.

    Returns:
        The YAML text.
    """
    return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True, width=1000, default_flow_style=False)


def starter_map(root: Path, *, source_path: str = "", target_heading: str = "", exit_section: str = "Exit condition",
                criteria_section: str = "Acceptance test", label: str = "Target", render_to: str = DEFAULT_RENDER_TO,
                changelog: str = "", entry_heading: str = r"^## (?P<stamp>\d{8}_\d{4}) — ", now: dt.datetime | None = None,
                exit_line: str = "", checklist_line: str = "") -> str:
    """A starter `target-map.yaml` as text. Source mode (a plan with one heading per target) tracks every heading the pattern
    matches; inline mode (no plan) writes one placeholder target. Goals, the title and inline names are PLACEHOLDERs.

    Args:
        root: the project root.
        source_path: repo-relative plan; empty for inline mode.
        target_heading: regex with `id` and `name` groups.
        exit_section: heading title of each target's exit condition.
        criteria_section: heading title of each target's numbered criteria.
        label: what the project calls a target.
        render_to: where the tracker will render.
        changelog: repo-relative change log; empty for none.
        entry_heading: the change log's entry heading regex.
        now: the moment to stamp; default now.
        exit_line: bold lead of a one-line exit condition, for plans written as bullets.
        checklist_line: bold lead of a one-line checklist, for plans written as bullets.

    Returns:
        The map text, header comment included.

    Raises:
        InitError: when the plan or change log is missing, or the pattern matches nothing.
    """
    now = now or dt.datetime.now().replace(second=0, microsecond=0)
    raw: dict = {"schema": 1, "title": f"{PLACEHOLDER} title of the rendered tracker", "render_to": render_to,
                 "updated": now.date().isoformat(), "stale_after_days": 7}
    if (root / "ROADMAP.md").is_file():
        raw["roadmap_file"] = "ROADMAP.md"
    if changelog:
        if not (root / changelog).is_file():
            raise InitError(f"changelog `{changelog}` does not exist")
        raw["changelog"] = {"path": changelog, "entry_heading": entry_heading}
    raw["labels"] = {"target": label, "section": f"Per {label.lower()}"}
    reviewed = now if changelog else None
    if source_path:
        path = root / source_path
        if not path.is_file():
            raise InitError(f"source `{source_path}` does not exist")
        src = Source(id="plan", path=source_path, target_heading=target_heading, exit_section=exit_section, criteria_section=criteria_section,
                     exit_line=exit_line, checklist_line=checklist_line)
        defs = SourceReader(path.read_text(encoding="utf-8"), src).definitions()
        if not defs:
            raise InitError(f"`{target_heading}` matched no heading in {source_path}")
        raw["sources"] = [{"id": "plan", "label": f"{PLACEHOLDER} link text for the plan", "path": source_path, "target_heading": target_heading,
                           "exit_section": exit_section, "criteria_section": criteria_section}
                          | ({"exit_line": exit_line} if exit_line else {}) | ({"checklist_line": checklist_line} if checklist_line else {})]
        targets = [starter_target(d.id, "G1", sorted(d.criteria), label, "plan", reviewed) for d in defs.values()]
    else:
        targets = [starter_target("1", "G1", [1], label, now=reviewed, inline=True)]
    raw["goals"] = [{"id": "G1", "name": f"{PLACEHOLDER} a few words", "statement": f"{PLACEHOLDER} why the project exists, and where that is written"}]
    raw["targets"] = targets
    return STARTER_HEADER.format(date=now.date().isoformat()) + _dump(raw)


def sync_text(text: str, root: Path, now: dt.datetime | None = None) -> tuple[str, list[str]]:
    """The map text with a `not started` target appended for every source heading no target tracks, and the ids added.

    Appends text rather than re-dumping the YAML, so every comment and hand-made layout survives; existing targets are never
    touched. Refuses when `targets:` is not the file's last top-level key (appending there would land inside another key).
    The new target's goal is a PLACEHOLDER: which goal a step serves is a person's decision.

    Args:
        text: the map file's text.
        root: the project root.
        now: the `reviewed` moment for new targets; default now.

    Returns:
        (the new text, the ids appended); the text is unchanged when nothing is missing.

    Raises:
        SyncError: when `targets:` is not the last key or a source is missing.
    """
    now = now or dt.datetime.now().replace(second=0, microsecond=0)
    raw = yaml.safe_load(text)
    tmap = TargetMap.from_dict(raw)
    keys = re.findall(r"^([A-Za-z_][\w-]*):", text, re.M)
    if not keys or keys[-1] != "targets":
        raise SyncError(f"`targets:` must be the last top-level key to append safely; the last is `{keys[-1] if keys else '?'}`")
    ids = {t.id for t in tmap.targets}
    new: list[dict] = []
    for src in tmap.sources:
        path = root / src.path
        if not path.is_file():
            raise SyncError(f"source {src.id}: `{src.path}` does not exist")
        tracked = {t.key for t in tmap.targets if t.source == src.id}
        for key, d in SourceReader(path.read_text(encoding="utf-8"), src).definitions().items():
            if key in tracked:
                continue
            tid = key if key not in ids else f"{src.id}-{key}"
            t = starter_target(tid, f"{PLACEHOLDER}_GOAL", sorted(d.criteria), tmap.label_target, src.id,
                               now if tmap.changelog else None)
            if tid != key:
                t = {"id": tid, "ref": key} | {k: v for k, v in t.items() if k != "id"}
                t["mention"] = f"{tmap.label_target} {key}"
            new.append(t)
            ids.add(tid)
    if not new:
        return text, []
    m = re.search(r"^(\s*)- id:", text[text.rindex("\ntargets:"):], re.M)
    indent = m.group(1) if m else "  "
    block = "".join(indent + line if line else line for line in _dump(new).splitlines(keepends=True))
    return text.rstrip("\n") + "\n\n" + block, [t["id"] for t in new]


# ---------------------------------------------------------------------------------------------------------------- orchestration


@dataclass
class Outcome:
    """What evaluate() found: problems (any fails), warnings, whether a rendered file differs, the tracker text and path, and each embed's new page text."""

    problems: list[str]
    warnings: list[str]
    drift: bool
    rendered: str
    output: Path | None
    embeds: dict[Path, str] = field(default_factory=dict)


def splice(page: str, block: str) -> str:
    """Put a rendered embed block between the target-map markers of a page.

    Args:
        page: the page's text.
        block: the block, markers included.

    Returns:
        The page with its block replaced; text outside the markers is untouched.

    Raises:
        ValueError: when the page lacks the markers, holds them more than once, or holds them out of order.
    """
    start, stop = page.find(EMBED_BEGIN), page.find(EMBED_END)
    if page.count(EMBED_BEGIN) != 1 or page.count(EMBED_END) != 1 or stop < start:
        raise ValueError("the page needs exactly one target-map BEGIN marker followed by one END marker")
    return page[:start] + block + page[stop + len(EMBED_END):]


def evaluate(root: Path, today: dt.date | None = None) -> Outcome:
    """Load the map from `root`, check it against SCHEMA, read its sources and roadmap, validate, render, compare with disk.

    Args:
        root: the project root holding target-map.yaml.
        today: the date staleness is judged against; default today.

    Returns:
        The outcome; `drift` is True when the tracker or any embed page differs from its render.
    """
    path = root / MAP_FILE
    if not path.is_file():
        return Outcome([f"{MAP_FILE} does not exist"], [], False, "", None)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return Outcome([f"{MAP_FILE} is not a mapping"], [], False, "", None)
    schema = SchemaCheck(raw).run()
    if schema.problems:
        return Outcome(schema.problems + placeholders(raw), schema.warnings, False, "", None)
    tmap = TargetMap.from_dict(raw)
    problems: list[str] = placeholders(raw)
    source_defs: dict[str, dict[str, Definition]] = {}
    for src in tmap.sources:
        path = root / src.path
        if not path.is_file():
            problems.append(f"source {src.id}: `{src.path}` does not exist")
            continue
        source_defs[src.id] = SourceReader(path.read_text(encoding="utf-8"), src).definitions()
    defs = resolve(tmap, source_defs)
    roadmap = None
    if tmap.roadmap_file and (root / tmap.roadmap_file).is_file():
        roadmap = (root / tmap.roadmap_file).read_text(encoding="utf-8")
    changelog = None
    if tmap.changelog and (root / tmap.changelog.path).is_file():
        changelog = (root / tmap.changelog.path).read_text(encoding="utf-8")
        # Rotated entries (skill-ai-it rotate_records.py, 2026-10-10) live in docs/history; the rule must still see them.
        for arc in sorted((root / "docs" / "history").glob(f"{Path(tmap.changelog.path).stem.lower()}-*.md")):
            changelog += ARCHIVE_BOUNDARY + arc.read_text(encoding="utf-8")
    validator = TargetMapValidator(tmap, source_defs, roadmap, root, today or dt.date.today(), changelog)
    problems += validator.problems()
    renderer = TrackerRenderer(tmap, defs)
    rendered = renderer.render()
    output = root / tmap.render_to
    current = output.read_text(encoding="utf-8") if output.is_file() else None
    drift = current != rendered
    embeds: dict[Path, str] = {}
    for emb in tmap.embeds:
        page_path = root / emb.path
        try:
            page = page_path.read_text(encoding="utf-8")
            new_page = splice(page, renderer.embed_block(emb))
        except (OSError, ValueError) as exc:
            problems.append(f"embed {emb.path}: {exc}")
            continue
        if new_page != page:
            embeds[page_path] = new_page
            drift = True
    return Outcome(problems, schema.warnings + validator.warnings, drift, rendered, output, embeds)


def show(root: Path, target_id: str | None) -> str:
    """A read-only view of the map, so an agent reads one target instead of the whole file.

    Args:
        root: the project root holding the map.
        target_id: a target id to show in full; None lists every target on one line each.

    Returns:
        The text to print: the list, or one target's definition (name, exit condition, criteria from its source) and its map entry as YAML.

    Raises:
        KeyError: when no target has `target_id`.
    """
    raw = yaml.safe_load((root / MAP_FILE).read_text(encoding="utf-8"))
    tmap = TargetMap.from_dict(raw)
    source_defs = {src.id: SourceReader((root / src.path).read_text(encoding="utf-8"), src).definitions()
                   for src in tmap.sources if (root / src.path).is_file()}
    defs = resolve(tmap, source_defs)
    if target_id is None:
        rows = [f"{t.id:>4}  {t.state:<12} exit_met={str(t.exit_met).lower():<5} {defs[t.id].name if t.id in defs else t.name}" for t in tmap.targets]
        return "\n".join(rows) + f"\n({len(rows)} targets; `--show <id>` for one)"
    entry = next((d for d in raw.get("targets", []) if str(d.get("id")) == str(target_id)), None)
    if entry is None:
        raise KeyError(target_id)
    d = defs.get(str(target_id))
    head = [f"# {d.name}" if d else f"# target {target_id}"]
    if d:
        head += ["", f"Exit condition: {d.exit_condition}", "", "Criteria:"] + [f"  {n}. {c}" for n, c in sorted(d.criteria.items())]
    return "\n".join(head) + "\n\n" + yaml.safe_dump(entry, sort_keys=False, allow_unicode=True, width=160)


def _sync(root: Path, write: bool) -> int:
    """`--sync`: show the targets a source defines that the map lacks, or append them with `write`.

    Args:
        root: the project root.
        write: append to the map instead of printing.

    Returns:
        0 when done or nothing is missing, 1 when the map cannot be appended to safely.
    """
    path = root / MAP_FILE
    try:
        original = path.read_text(encoding="utf-8")
        text, added = sync_text(original, root)
    except (SyncError, OSError) as err:
        print(f"sync: {err}", file=sys.stderr)
        return 1
    if not added:
        print(f"sync: every source heading already has a target in {MAP_FILE}")
        return 0
    if write:
        path.write_text(text, encoding="utf-8")
        print(f"sync: appended {', '.join(added)} to {MAP_FILE}; set each goal (TODO_GOAL), then --write")
    else:
        print(text[len(original.rstrip(chr(10))) + 2:], end="")
        print(f"sync: would append {', '.join(added)}; run with --write to append")
    return 0


def _check(root: Path, today: dt.date | None, write: bool) -> int:
    """Validate, report, and render with `write`.

    Args:
        root: the project root.
        today: the date staleness is judged against; None for today.
        write: render the tracker and embeds in place.

    Returns:
        0 when valid and current (or written), 1 on a problem or drift.
    """
    outcome = evaluate(root, today)
    for w in outcome.warnings:
        print(f"  ! {w}")
    for p in outcome.problems:
        print(f"  ✗ {p}")
    if outcome.problems or outcome.output is None:
        print(f"FAIL — {len(outcome.problems)} problem(s) in {MAP_FILE}; nothing written")
        return 1
    rel = outcome.output.relative_to(root)
    tracker_drift = not outcome.output.is_file() or outcome.output.read_text(encoding="utf-8") != outcome.rendered
    if write:
        if tracker_drift:
            outcome.output.parent.mkdir(parents=True, exist_ok=True)
            outcome.output.write_text(outcome.rendered, encoding="utf-8")
            print(f"wrote {rel}")
        for page_path, text in outcome.embeds.items():
            page_path.write_text(text, encoding="utf-8")
            print(f"wrote the target-map block in {page_path.relative_to(root)}")
        if not outcome.drift:
            print(f"{rel} already current")
        return 0
    if outcome.drift:
        stale = ([str(rel)] if tracker_drift else []) + [str(p.relative_to(root)) for p in outcome.embeds]
        print(f"DRIFT — {', '.join(stale)} differ(s) from what {MAP_FILE} renders; run with --write")
        return 1
    print(f"OK — {MAP_FILE} valid and {rel} current")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Command line: validate and report, render with --write, or --schema, --init, --sync, --show.

    Args:
        argv: arguments (default: sys.argv).

    Returns:
        0 when valid and current (or written), 1 on a problem or drift.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project-root", type=Path, default=Path("."), help="the project holding target-map.yaml (default: the current folder)")
    ap.add_argument("--write", action="store_true", help="render the tracker and embeds in place after a clean validation; with --sync, append in place")
    ap.add_argument("--schema", action="store_true", help="print the field reference (mandatory, recommended, optional) and exit")
    ap.add_argument("--init", action="store_true", help="print a starter map to stdout (never writes a file); see the --source options")
    ap.add_argument("--sync", action="store_true", help="show the targets a source defines that the map lacks; with --write, append them")
    ap.add_argument("--show", nargs="?", const="", metavar="ID", help="read only: list every target on one line, or show one target in full")
    ap.add_argument("--today", type=dt.date.fromisoformat, default=None, help="judge staleness against this date (YYYY-MM-DD; tests, previews)")
    g = ap.add_argument_group("--init options")
    g.add_argument("--source", default="", help="repo-relative plan document (source mode); omit for inline mode")
    g.add_argument("--heading", default=r"^## Step (?P<id>\d+) — (?P<name>.+)$", help="regex with `id` and `name` groups, one line per target")
    g.add_argument("--exit-section", default="Exit condition")
    g.add_argument("--criteria-section", default="Acceptance test")
    g.add_argument("--exit-line", default="", help="bold lead of a one-line exit condition (plans written as bullets)")
    g.add_argument("--checklist-line", default="", help="bold lead of a one-line checklist (plans written as bullets)")
    g.add_argument("--label", default="Step", help="what the project calls a target (Step, Phase, Milestone)")
    g.add_argument("--render-to", default=DEFAULT_RENDER_TO)
    g.add_argument("--changelog", default="", help="repo-relative change log; adds `changelog` and a `reviewed` stamp per target")
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    if args.show is not None:
        try:
            print(show(root, args.show or None))
        except KeyError:
            print(f"show: no target `{args.show}` in {MAP_FILE}", file=sys.stderr)
            return 1
        return 0
    if args.schema:
        print(schema_markdown())
        return 0
    if args.init:
        try:
            sys.stdout.write(starter_map(root, source_path=args.source, target_heading=args.heading, exit_section=args.exit_section,
                                         criteria_section=args.criteria_section, label=args.label, render_to=args.render_to,
                                         changelog=args.changelog, exit_line=args.exit_line, checklist_line=args.checklist_line))
        except InitError as err:
            print(f"init: {err}", file=sys.stderr)
            return 1
        return 0
    if args.sync:
        return _sync(root, args.write)
    return _check(root, args.today, args.write)


if __name__ == "__main__":
    sys.exit(main())
