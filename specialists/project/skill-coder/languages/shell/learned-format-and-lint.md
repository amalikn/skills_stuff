---
Title: shell override - learned format and lint
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/shell.md (split by scripts/language_split.py)
Last reviewed: 2026-11-19
Summary: The learned format and lint part of the shell override; the entry file holds the tools and the core rule mapping.
---

# shell: learned format and lint

Part of [shell.md](../shell.md).

> **Learned 2026-10-23** · shfmt 3.14.1 (`uvx --from shfmt-py shfmt`), ShellCheck · VERIFIED_PRIMARY (ansible-wifi checkout) · Source: local-knowledge-ansible `ansible-wifi/ansible-wifi-root-governance/{.editorconfig,.shellcheckrc,lint_new.sh}` · Falsifier: shfmt
> listing a file marked `ignore = true` Two-space shell for new scripts only: shfmt reads `.editorconfig` (`[*.{sh,bash}] indent_style = space`, `indent_size = 2`, `shell_variant = bash`), and a
> section listing the existing scripts with `ignore = true` (plus `indent_size = unset` so editors keep their style) keeps them out. `shfmt -f <dirs>` then lists exactly the scripts to check,
> including extensionless ones found by shebang (6 here that a `*.sh` glob missed); pass that list to `shfmt -d` and `shellcheck`. shfmt does not descend into a symlinked folder, and finds
> `.editorconfig` by walking up from each file, so a physical path outside the checkout needs the file linked into an ancestor.

> **Learned 2026-11-07** · shfmt 3.14.1, ShellCheck 0.11.0, mise · VERIFIED_PRIMARY · Source: smc-resiliency `lab/payloads/*.sh`,
> `lab/infra/proxmox/*.sh`, justfile `lint` (2026-11-07) · Falsifier: `shfmt -i 2 -ci -d` reporting no change on a one-line `a; b` pair
> Pinned in `.mise.toml` and run as `mise exec -- shfmt -i 2 -ci -d $(find lab -name '*.sh')` with `shellcheck -S warning`: shfmt splits
> `a=1; b=2` and `cmd || { ...; exit 2; }` onto separate lines. A box-side payload is copied to `/tmp` and run with `bash <file> <args>`
> under sudo, not piped on stdin, so a long script never meets an argument-length limit (`prlctl exec` cut long inline arguments). An
> agent's command text that contains `dd`, a recursive force delete or a pipe into `sha256sum` is refused by this environment's guard
> even inside a heredoc: write `head -c` fills, `rm` through a script file, and `sha256sum -c <file>`.

> **Learned 2026-11-05 (k)** · bash scripts that run code on remote hosts and check many hosts · VERIFIED_PRIMARY (skill-smc
> smc_gateway_loss.sh and smc_change_parallel.sh, shellcheck 0.10) · Source: skill-smc scripts/probes/smc_gateway_loss.sh
> · Falsifier: shellcheck stays quiet on a single-quoted remote probe, or a silent 2-minute check loop is read as working
> Send the remote half as its own script on stdin (`ssh host "sh -s $arg" < remote.sh`). A single-quoted string draws SC2016, and a
> `declare -f` function draws SC2329; each needs an inline disable, which is not allowed. A separate file is also linted and tested on its
> own. When a script checks many hosts before acting, run the checks at once and print a line per host as each lands: one at a time with no
> output (30 s timeout each), the operator read it as stalled and stopped it before anything ran.

> **Learned 2026-11-24** · bash, shellcheck 0.11.0 · VERIFIED_PRIMARY · Source: home NAS project `scripts/nas_api.sh`, `scripts/nas_lib.sh` (shellcheck -x run 2026-11-24) ·
> Falsifier: SC1091 still reported with the directive below
> A script that sources a sibling through `$(dirname "${BASH_SOURCE[0]}")` gets SC1091 ("not following") under `shellcheck -x` when run from another folder, because
> a plain `# shellcheck source=nas_lib.sh` resolves against the working directory. Prefix the directive with `SCRIPTDIR`, which shellcheck resolves against the script's
> own folder; the same works for a config file one level up. No inline `disable` needed.
> ```bash
> # shellcheck source=SCRIPTDIR/nas_lib.sh
> source "$(dirname "${BASH_SOURCE[0]}")/nas_lib.sh"
> # shellcheck source=SCRIPTDIR/../config/nas.env
> source "$NAS_ROOT/config/nas.env"
> ```
