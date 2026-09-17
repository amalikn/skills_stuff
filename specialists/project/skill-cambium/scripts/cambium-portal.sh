#!/usr/bin/env bash
# Cambium support portal (support.cambiumnetworks.com) automation: login, and fetching a specific
# release's files (firmware image, MIBs, etc.) for archiving in a consuming project.
#
# Read-only against the portal: signs in, searches Downloads, downloads files a logged-in user
# could already download by hand. Never uploads, submits a case, or changes anything Cambium-side.
# Nothing here touches AWS, cnMaestro or devices.
#
# Moved here from cambium-swap 2026-09-17 (was scripts/cambium-support-login.sh) — this is
# cross-project Cambium vendor-research tooling, not specific to any one consuming project's
# investigation. See skill-cambium's Standing Write-Back Contract.
#
# Requires: npx (Node), the KeePassXC `kp` wrapper at ~/.config/keepassxc/kp with an entry named
# "/Network/cambium support" (UserName + Password attributes), and a LIVE MFA code from the account
# holder — the vault entry has no stored TOTP seed (its Notes field says "2FA OTP"), so this cannot
# run unattended. Run it from an interactive shell (or have the operator paste the current code the
# moment it is asked for, since codes expire in well under a minute).
#
# Usage:
#   cambium-portal.sh login                          # login only, session stays open
#   cambium-portal.sh login --search "cnMaestro"     # login, then open a Downloads search
#   cambium-portal.sh fetch-release "<model search>" "<version string>" <dest-dir>
#       # login, search Downloads for <model search>, expand the release heading whose text
#       # contains <version string>, download every file under it into <dest-dir>, sniff each
#       # file's real type (MIB text vs firmware image vs other) since the portal's download
#       # links carry no filename, and print a short manifest (path, sniffed type, sha256).
#       # Does NOT commit anything to git and does NOT decide storage_locations — that policy
#       # decision belongs to the consuming project (see its firmware-manifest.yaml /
#       # software-manifest.yaml convention for recording a checksum without committing a binary).
#
# See docs/operations/agent-research-and-tooling-notes.md in a consuming project (originally
# written in cambium-swap) for the manual step-by-step this automates, why the sidebar accordion
# on /files must be avoided in favour of the search box, and why /file/<hash> download links are
# per-session and must always be re-derived rather than reused.
#
# Known gap (2026-09-17): Cambium does not publish a per-patch-version CLI reference or release
# notes file separately from firmware/MIBs on this portal for XV2 — only firmware image + MIB
# files are attached to each dated release entry. For CLI-syntax-vs-firmware-version questions,
# cross-check the CLI Reference Guide's own "New Commands Introduced in <release>" section instead
# of expecting a version-specific CLI doc to exist.

set -euo pipefail

AB_PKG="agent-browser@0.37.1"
AB() { npx --yes "$AB_PKG" "$@"; }

KP="${HOME}/.config/keepassxc/kp"
ENTRY="/Network/cambium support"
PORTAL_URL="https://support.cambiumnetworks.com/"

cambium_login() {
  local search_query="$1"

  if [ ! -x "$KP" ]; then
    echo "kp wrapper not found or not executable at $KP — see the KeePassXC reference in your memory system" >&2
    exit 1
  fi

  local username
  username="$("$KP" show -a UserName "$ENTRY")"
  if [ -z "$username" ]; then
    echo "Could not read UserName from KeePassXC entry '$ENTRY'" >&2
    exit 1
  fi

  echo "Opening $PORTAL_URL ..." >&2
  AB open "$PORTAL_URL"
  AB find text "Login" click
  AB wait --load networkidle

  echo "Filling email ($username) ..." >&2
  AB find label "Email address" fill "$username"
  AB find role button --name Next click 2>/dev/null || AB find text "Next" click
  AB wait --load networkidle

  echo "Filling password (from vault, not printed) ..." >&2
  local pw
  pw="$("$KP" show -s -a Password "$ENTRY")"
  AB find label "Password" fill "$pw"
  unset pw
  AB find role button --name "Sign In" click 2>/dev/null || AB find text "Sign In" click
  AB wait --load networkidle

  echo "" >&2
  echo "=== MFA required — this account has no stored TOTP seed. ===" >&2
  local otp
  read -r -p "Enter the current authentication code from the account holder: " otp
  if [ -z "$otp" ]; then
    echo "No code entered, aborting." >&2
    exit 1
  fi

  AB find label "Authentication Code" fill "$otp"
  AB find role button --name Submit click 2>/dev/null || AB find text "Submit" click
  AB wait --load networkidle

  if AB snapshot -i 2>/dev/null | grep -q 'button "Malik Ahmad"'; then
    echo "Logged in as Malik Ahmad." >&2
  else
    echo "WARNING: could not confirm login — snapshot the page and check manually (agent-browser snapshot -i)." >&2
  fi

  if [ -n "$search_query" ]; then
    echo "Searching Downloads for: $search_query" >&2
    AB open "https://support.cambiumnetworks.com/files?q=${search_query// /%20}"
    AB wait --load networkidle
    AB snapshot -i
  fi
}

cmd_login() {
  local search_query=""
  if [ "${1:-}" = "--search" ]; then
    search_query="${2:?--search requires a query, e.g. --search cnMaestro}"
  fi
  cambium_login "$search_query"
  echo "" >&2
  echo "Session left open. Continue with: npx --yes $AB_PKG <command...> (snapshot -i, click, get attr <ref> href, download <ref> <path>)." >&2
  echo "Close when done: npx --yes $AB_PKG close" >&2
}

cmd_fetch_release() {
  local model_query="${1:?usage: fetch-release <model search> <version string> <dest-dir>}"
  local version_string="${2:?usage: fetch-release <model search> <version string> <dest-dir>}"
  local dest_dir="${3:?usage: fetch-release <model search> <version string> <dest-dir>}"

  mkdir -p "$dest_dir"
  cambium_login "$model_query"

  echo "" >&2
  echo "Looking for a release heading containing: $version_string" >&2
  local snapshot
  snapshot="$(AB snapshot -i 2>&1)"
  local heading_line
  heading_line="$(printf '%s\n' "$snapshot" | grep -F "$version_string" | grep -m1 "link\|heading")"
  if [ -z "$heading_line" ]; then
    echo "No matching release entry found for '$version_string' in the current Downloads search results." >&2
    echo "Re-run with a broader --search or inspect manually: npx --yes $AB_PKG snapshot -i" >&2
    exit 1
  fi
  local ref
  ref="$(printf '%s\n' "$heading_line" | grep -oE 'ref=e[0-9]+' | head -1 | cut -d= -f2)"
  echo "Matched: $heading_line" >&2
  echo "Expanding ref=$ref ..." >&2
  AB click "$ref"
  AB wait --load networkidle

  # Re-snapshot and find every "Download" link immediately after this release's heading and
  # before the next heading — the portal renders one heading per release with its files nested
  # under it, no distinguishing labels on the Download links themselves.
  snapshot="$(AB snapshot -i 2>&1)"
  local in_section=0
  local dl_refs=()
  while IFS= read -r line; do
    if printf '%s' "$line" | grep -qF "$version_string"; then
      in_section=1
      continue
    fi
    if [ "$in_section" = 1 ]; then
      if printf '%s' "$line" | grep -q '^- heading'; then
        break
      fi
      if printf '%s' "$line" | grep -q '"Download"'; then
        dl_refs+=("$(printf '%s' "$line" | grep -oE 'ref=e[0-9]+' | cut -d= -f2)")
      fi
    fi
  done <<< "$snapshot"

  if [ "${#dl_refs[@]}" -eq 0 ]; then
    echo "No Download links found under the matched release heading." >&2
    exit 1
  fi

  echo "Found ${#dl_refs[@]} download link(s): ${dl_refs[*]}" >&2
  echo "" >&2
  printf '%-40s %-20s %s\n' "file" "sniffed_type" "sha256"
  local i=1
  for r in "${dl_refs[@]}"; do
    local out="$dest_dir/download-${i}.bin"
    if AB download "$r" "$out" >/dev/null 2>&1; then
      local kind
      kind="$(file -b "$out" | cut -c1-20)"
      local sum
      sum="$(shasum -a 256 "$out" | awk '{print $1}')"
      printf '%-40s %-20s %s\n' "$out" "$kind" "$sum"
    else
      echo "Download failed for ref=$r (see docs/operations/agent-research-and-tooling-notes.md for the per-session download-link gotcha; retry the whole fetch-release run)" >&2
    fi
    i=$((i + 1))
  done

  echo "" >&2
  echo "Downloaded files are NOT committed to git and storage_locations is NOT decided here — that is" >&2
  echo "a consuming-project policy decision (see its firmware-manifest.yaml / software-manifest.yaml)." >&2
}

case "${1:-}" in
  login)
    shift
    cmd_login "$@"
    ;;
  fetch-release)
    shift
    cmd_fetch_release "$@"
    ;;
  *)
    echo "Usage: $0 login [--search QUERY] | fetch-release <model search> <version string> <dest-dir>" >&2
    exit 2
    ;;
esac
