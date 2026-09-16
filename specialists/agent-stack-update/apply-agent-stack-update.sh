#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FILES_DIR="$SCRIPT_DIR/files"
MANIFEST="$SCRIPT_DIR/update-manifest.json"

DRY_RUN=0
FORCE=0
TARGET=""

usage() {
  cat <<'EOF'
Usage:
  ./apply-agent-stack-update.sh [--dry-run] [--force] /path/to/agent-stack

Options:
  --dry-run  Validate and show changes without writing anything.
  --force    Overwrite modified files even if they differ from the expected base.
             Existing files are still backed up first.
  -h, --help Show this help.

If TARGET is omitted, the script will use ../agent-stack when that looks like
an Agent Stack repository, otherwise the current directory if it does.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --force) FORCE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
    *)
      if [[ -n "$TARGET" ]]; then
        echo "Only one target path may be supplied." >&2
        exit 2
      fi
      TARGET="$1"; shift ;;
  esac
done

looks_like_agent_stack() {
  local p="$1"
  [[ -f "$p/manifest.yaml" && -d "$p/skills" && -d "$p/personas" ]]
}

if [[ -z "$TARGET" ]]; then
  if looks_like_agent_stack "$SCRIPT_DIR/../agent-stack"; then
    TARGET="$SCRIPT_DIR/../agent-stack"
  elif looks_like_agent_stack "$PWD"; then
    TARGET="$PWD"
  else
    echo "Target not specified and could not be detected." >&2
    usage >&2
    exit 2
  fi
fi

TARGET="$(cd "$TARGET" 2>/dev/null && pwd)" || {
  echo "Target directory does not exist: $TARGET" >&2
  exit 2
}

if ! looks_like_agent_stack "$TARGET"; then
  echo "Refusing to update: target does not look like Agent Stack: $TARGET" >&2
  exit 2
fi

if [[ ! -f "$MANIFEST" || ! -d "$FILES_DIR" ]]; then
  echo "Update package is incomplete." >&2
  exit 2
fi

PYTHON="${PYTHON:-python3}"
command -v "$PYTHON" >/dev/null 2>&1 || {
  echo "python3 is required for manifest/hash validation." >&2
  exit 2
}

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_ROOT="$TARGET/.agent-stack-update-backups/$TIMESTAMP"

# Validate package and target before changing anything.
"$PYTHON" - "$MANIFEST" "$FILES_DIR" "$TARGET" "$FORCE" <<'PY'
import hashlib, json, pathlib, sys
manifest_path, files_dir, target, force = sys.argv[1:]
force = force == '1'
files_dir = pathlib.Path(files_dir)
target = pathlib.Path(target)
manifest = json.loads(pathlib.Path(manifest_path).read_text())
errors=[]
for rec in manifest['files']:
    rel=rec['path']
    src=files_dir/rel
    if not src.is_file():
        errors.append(f"package missing: {rel}")
        continue
    got=hashlib.sha256(src.read_bytes()).hexdigest()
    if got != rec['new_sha256']:
        errors.append(f"package hash mismatch: {rel}")
        continue
    dst=target/rel
    if rec['status']=='modified':
        if not dst.is_file():
            if not force:
                errors.append(f"target missing expected modified file: {rel}")
            continue
        old=hashlib.sha256(dst.read_bytes()).hexdigest()
        if old != rec['old_sha256'] and old != rec['new_sha256'] and not force:
            errors.append(f"target has local/unexpected changes: {rel}")
    elif rec['status']=='added':
        if dst.exists():
            cur=hashlib.sha256(dst.read_bytes()).hexdigest() if dst.is_file() else None
            if cur != rec['new_sha256'] and not force:
                errors.append(f"target already has different file at added path: {rel}")
if errors:
    print("Update validation failed:", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    print("Use --force only if you intentionally want to replace these paths.", file=sys.stderr)
    sys.exit(1)
print(f"Validated {len(manifest['files'])} update files.")
PY

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Dry run only. No files changed."
  "$PYTHON" - "$MANIFEST" <<'PY'
import json, pathlib, sys
m=json.loads(pathlib.Path(sys.argv[1]).read_text())
for r in m['files']:
    print(f"{r['status'].upper():8} {r['path']}")
for p in m.get('removed',[]):
    print(f"REMOVE   {p}")
PY
  exit 0
fi

mkdir -p "$BACKUP_ROOT"

# Backup existing files that will be replaced.
"$PYTHON" - "$MANIFEST" "$TARGET" "$BACKUP_ROOT" <<'PY'
import json, pathlib, shutil, sys
manifest, target, backup = sys.argv[1:]
m=json.loads(pathlib.Path(manifest).read_text())
target=pathlib.Path(target); backup=pathlib.Path(backup)
for rec in m['files']:
    dst=target/rec['path']
    if dst.is_file():
        b=backup/rec['path']
        b.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dst,b)
PY

# Install each file through a same-directory temp file + rename.
"$PYTHON" - "$MANIFEST" "$FILES_DIR" "$TARGET" <<'PY'
import json, os, pathlib, shutil, sys, tempfile
manifest, files_dir, target = sys.argv[1:]
m=json.loads(pathlib.Path(manifest).read_text())
files_dir=pathlib.Path(files_dir); target=pathlib.Path(target)
for rec in m['files']:
    src=files_dir/rec['path']
    dst=target/rec['path']
    dst.parent.mkdir(parents=True, exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.agent-stack-update-', dir=dst.parent)
    os.close(fd)
    tmp=pathlib.Path(tmp)
    try:
        shutil.copy2(src,tmp)
        os.replace(tmp,dst)
    finally:
        if tmp.exists():
            tmp.unlink()
for rel in m.get('removed',[]):
    p=target/rel
    if p.is_file() or p.is_symlink():
        p.unlink()
PY

# Verify installed hashes.
"$PYTHON" - "$MANIFEST" "$TARGET" <<'PY'
import hashlib, json, pathlib, sys
manifest,target=sys.argv[1:]
m=json.loads(pathlib.Path(manifest).read_text()); target=pathlib.Path(target)
errors=[]
for rec in m['files']:
    p=target/rec['path']
    if not p.is_file():
        errors.append(f"missing after update: {rec['path']}")
        continue
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    if h != rec['new_sha256']:
        errors.append(f"hash mismatch after update: {rec['path']}")
if errors:
    print("Post-update verification failed:", file=sys.stderr)
    for e in errors: print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print(f"Update applied successfully: {len(m['files'])} files verified.")
PY

echo "Backup of replaced files: $BACKUP_ROOT"
echo "Agent Stack update complete."
