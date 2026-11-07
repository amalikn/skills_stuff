---
Title: shell override - open items
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/shell.md (split by scripts/language_split.py)
Last reviewed: 2026-11-07
Summary: The open items part of the shell override; the entry file holds the tools and the core rule mapping.
---

# shell: open items

Part of [shell.md](../shell.md).

- Test framework choice and a formatter: UNVERIFIED stubs.

>  **Learned 2026-11-05** · BSD and GNU sed, `s` with a custom delimiter · VERIFIED_PRIMARY (macOS sed wrote two stray files into a role folder) ·
>  Source: this session's edit of an Ansible test fixture · Falsifier: a replacement holding the delimiter changes only the text
>  In `s#old#new#`, a `#` inside the replacement (a YAML comment, say) ends the replacement early. sed then reads the rest as flags, and
>  `w <file>` writes the matched lines to a file named after the rest of the comment, in the current folder. Pick a delimiter that cannot occur in
>  the text, or make the edit in Python with an exact-match assert, and run `git status` afterwards to catch stray files.

>  **Learned 2026-11-05 (ii)** · bash scripts that run code on remote hosts and check many hosts · VERIFIED_PRIMARY (skill-smc
>  smc_gateway_loss.sh and smc_change_parallel.sh, shellcheck 0.10) · Source: skill-smc scripts/probes/smc_gateway_loss.sh · Falsifier:
>  shellcheck stays quiet on a single-quoted remote probe, or a silent 2-minute check loop is read as working
>  Send the remote half as its own script on stdin (`ssh host "sh -s $arg" < remote.sh`). A single-quoted string draws SC2016, and a
>  `declare -f` function draws SC2329; each needs an inline disable, which is not allowed. A separate file is also linted and tested on its
>  own. When a script checks many hosts before acting, run the checks at once and print a line per host as each lands: one at a time with no
>  output (30 s timeout each), the operator read it as stalled and stopped it before anything ran.
