---
Title: Configuration and literals
Category: reference
Status: current
Authority: local-supplement
Scope: Where settings, paths, hosts, tokens and version pins live, and what may appear as a literal in code
Last reviewed: 2026-10-19
Summary: >-
  No absolute paths, hostnames, URLs or tokens in code; one settings module reads the environment and config files;
  version pins recorded in one place and changed together with the pin they mirror.
---

# Configuration and literals

## No deployment literals in code

No module contains an absolute path, a hostname, an IP address, a URL or a token. They come from settings. Why: code is copied between hosts and projects, and a literal ties it to one; a token in code
leaks with every copy (a governed project's rule R16; The Twelve-Factor App calls for "strict separation of config from code", VERIFIED_PRIMARY).

Allowed as literals: protocol constants, well-known ports used as defaults, relative paths inside the project, and test fixtures that use documentation-only ranges (`192.0.2.0/24`, `example.com`).

## One settings reader

- One module (for example `core/settings`) is the only reader of environment variables and configuration files. It provides roots, directories, URLs and budgets as typed values. Why: one place to see
  every input a program takes.
- Defaults suit the developer's machine; a deployment overrides them through the environment or a config file, never by editing code. Why: the same build runs everywhere.
- Never edit a host's environment file in place with a stream editor; change the instance's declared settings and re-apply them. Why: an in-place edit is not logged and not repeatable.
- Configuration is validated at start-up and the program refuses to start on a missing or malformed value. Why: failing at start-up is cheaper than failing halfway through a write.

## Version pins in one place

- Record every pinned version (images with tag and digest, base interpreters, tools, library constraints, host packages) in one file, and change a version there and at its pin in the same change; a
  check fails when they disagree. Why: two copies of a version drift (a governed project's `versions.yaml` and `just versions`).
- No floating tag (`latest`, an unbounded range) in a deployed profile. Why: a floating tag changes behaviour without a commit.

## Catalog data over code tables

Facts the code acts on (what each kind of thing can do, its limits, its mappings) are keys in a data file, with a check that every kind answers every key. Why: a fact in two code tables can disagree;
a governed project found two such tables disagreeing about which units allowed writes. See [generated-artifacts.md](generated-artifacts.md) for data files that render other files.

## Before writing a config directive

Check the official documentation or source for the exact version deployed before writing any directive, template syntax, API call or flag. Nearby examples in the same file are not verification. Why:
three changes that "validated" and deployed cleanly did nothing because they copied the shape of a nearby line or used another version's docs (operator lesson `feedback_verify_docs_correct_version`).
