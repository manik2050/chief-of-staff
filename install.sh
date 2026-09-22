#!/usr/bin/env bash
#
# install.sh — install the Chief of Staff OS into your Claude Code and Cursor homes.
#
# Two promises:
#   Non-destructive — an existing file is never overwritten, appended to, or deleted.
#                     Every copy goes through copy_if_missing.
#   Idempotent      — running it again changes nothing and exits 0.
#
# The only file this script rewrites on every run is the generated paths.json, whose contents
# are a pure function of the install root.
#
# Usage:  ./install.sh [options]
#         ./install.sh --help

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------------------------------------------------------------------------- defaults ----

CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
CURSOR_HOME="${CURSOR_HOME:-$HOME/.cursor}"
COS_HOME="${COS_HOME:-}"
DRY_RUN=0
ASSUME_YES=0
MERGE_MEMORY=0

COS_NAME="${COS_NAME:-}"
COS_ROLE="${COS_ROLE:-}"
COS_COMPANY="${COS_COMPANY:-}"
COS_EMAIL="${COS_EMAIL:-}"
COS_TIMEZONE="${COS_TIMEZONE:-}"
COS_WORK_HOURS="${COS_WORK_HOURS:-}"

CREATED=0
SKIPPED=0
WARNINGS=()

# ------------------------------------------------------------------------------- output ----

if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  C_DIM=$'\033[2m'; C_OK=$'\033[32m'; C_WARN=$'\033[33m'; C_ERR=$'\033[31m'; C_BOLD=$'\033[1m'; C_OFF=$'\033[0m'
else
  C_DIM=''; C_OK=''; C_WARN=''; C_ERR=''; C_BOLD=''; C_OFF=''
fi

say()   { printf '%s\n' "$*"; }
ok()    { printf '%s  created%s  %s\n' "$C_OK" "$C_OFF" "$1"; }
skip()  { printf '%s  exists %s  %s%s (left alone)%s\n' "$C_DIM" "$C_OFF" "$1" "$C_DIM" "$C_OFF"; }
warn()  { printf '%s  warn   %s  %s\n' "$C_WARN" "$C_OFF" "$1"; WARNINGS+=("$1"); }
die()   { printf '%serror%s %s\n' "$C_ERR" "$C_OFF" "$*" >&2; exit 1; }

usage() {
  cat <<'EOF'
install.sh — install the Chief of Staff OS into your Claude Code home.

Options:
  --name NAME            Your name                        (default: git config user.name, else $USER)
  --role ROLE            Your role                        (default: "Operator")
  --company COMPANY      Your company                     (default: "Independent")
  --email EMAIL          Primary email                    (default: git config user.email)
  --timezone TZ          IANA timezone, e.g. Europe/London (default: detected)
  --work-hours HOURS     e.g. "09:00-18:00"               (default: "09:00-18:00")

  --root DIR             Install root      (default: $COS_HOME, else ~/.claude/chief-of-staff)
  --claude-home DIR      Claude Code home  (default: $CLAUDE_HOME, else ~/.claude)
  --cursor-home DIR      Cursor home       (default: $CURSOR_HOME, else ~/.cursor)

  --merge-memory         Append the OS import line to an existing ~/.claude/CLAUDE.md.
                         Off by default; without it the line is printed for you to add.
  --yes, -y              Never prompt; use defaults for anything not passed
  --dry-run              Show what would happen and write nothing
  --help, -h             This message

Every value can also be supplied as an environment variable: COS_NAME, COS_ROLE,
COS_COMPANY, COS_EMAIL, COS_TIMEZONE, COS_WORK_HOURS, COS_HOME, CLAUDE_HOME,
CURSOR_HOME.

Re-running is safe. To refresh a file the installer already placed, delete your copy and run
again — the installer will never overwrite one for you.
EOF
}

# -------------------------------------------------------------------------------- args ----

while [ $# -gt 0 ]; do
  case "$1" in
    --name)        COS_NAME="${2:?--name needs a value}"; shift 2 ;;
    --role)        COS_ROLE="${2:?--role needs a value}"; shift 2 ;;
    --company)     COS_COMPANY="${2:?--company needs a value}"; shift 2 ;;
    --email)       COS_EMAIL="${2:?--email needs a value}"; shift 2 ;;
    --timezone)    COS_TIMEZONE="${2:?--timezone needs a value}"; shift 2 ;;
    --work-hours)  COS_WORK_HOURS="${2:?--work-hours needs a value}"; shift 2 ;;
    --root)        COS_HOME="${2:?--root needs a value}"; shift 2 ;;
    --claude-home) CLAUDE_HOME="${2:?--claude-home needs a value}"; shift 2 ;;
    --cursor-home) CURSOR_HOME="${2:?--cursor-home needs a value}"; shift 2 ;;
    --merge-memory) MERGE_MEMORY=1; shift ;;
    --dry-run)     DRY_RUN=1; shift ;;
    -y|--yes)      ASSUME_YES=1; shift ;;
    -h|--help)     usage; exit 0 ;;
    *)             die "unknown option: $1 (try --help)" ;;
  esac
done

COS_HOME="${COS_HOME:-$CLAUDE_HOME/chief-of-staff}"
COMMANDS_DIR="$CLAUDE_HOME/commands"
CURSOR_COMMANDS_DIR="$CURSOR_HOME/commands"

# ------------------------------------------------------------------------------ helpers ----

detect_timezone() {
  if [ -n "${TZ:-}" ]; then printf '%s' "$TZ"; return; fi
  if [ -r /etc/timezone ]; then tr -d '[:space:]' < /etc/timezone; return; fi
  if [ -L /etc/localtime ]; then
    local link; link="$(readlink /etc/localtime)"
    printf '%s' "${link#*zoneinfo/}"; return
  fi
  date +%Z 2>/dev/null || printf 'UTC'
}

git_config() { git config --get "$1" 2>/dev/null || true; }

# canonicalize PATH — absolute path with symlinks resolved, portably and without realpath(1).
#
# macOS makes this mandatory rather than cosmetic: /tmp is a symlink to /private/tmp and
# $TMPDIR lives under /var -> /private/var. core/paths.py resolves symlinks, so without this
# the path substituted into CLAUDE.md and the memory import line would disagree with the root
# recorded in paths.json for any install under those trees.
#
# Walks up to the deepest existing ancestor so it also works before the directory is created
# (--dry-run), then re-attaches the remainder.
canonicalize() {
  local input="$1" suffix="" parent
  case "$input" in "~") input="$HOME" ;; "~/"*) input="$HOME/${input#\~/}" ;; esac

  while [ -n "$input" ] && [ "$input" != "/" ] && [ ! -d "$input" ]; do
    suffix="/$(basename "$input")$suffix"
    parent="$(dirname "$input")"
    [ "$parent" = "$input" ] && break
    input="$parent"
  done

  if [ -d "$input" ]; then
    printf '%s%s' "$(cd "$input" && pwd -P)" "$suffix"
  else
    printf '%s' "$1"
  fi
}

# short PATH — display form, with the canonical home collapsed to ~
short() {
  case "$1" in
    "$HOME_CANON") printf '~' ;;
    "$HOME_CANON"/*) printf '~%s' "${1#$HOME_CANON}" ;;
    *) printf '%s' "$1" ;;
  esac
}

# ask VARNAME "Prompt" "default"
ask() {
  local var="$1" prompt="$2" default="$3" answer=""
  if [ -n "${!var}" ]; then return; fi
  if [ "$ASSUME_YES" -eq 1 ] || [ ! -t 0 ]; then
    printf -v "$var" '%s' "$default"; return
  fi
  read -r -p "  $prompt [$default]: " answer || answer=""
  printf -v "$var" '%s' "${answer:-$default}"
}

# Escape the characters that are special on the right-hand side of s|...|...|
escape_replacement() { printf '%s' "$1" | sed 's/[\&|]/\\&/g'; }

# substitute_placeholders FILE — rewrite {{TOKENS}} in place, portably.
substitute_placeholders() {
  local file="$1" tmp
  tmp="$(mktemp "${TMPDIR:-/tmp}/cos.XXXXXX")"
  sed \
    -e "s|{{NAME}}|$(escape_replacement "$COS_NAME")|g" \
    -e "s|{{ROLE}}|$(escape_replacement "$COS_ROLE")|g" \
    -e "s|{{COMPANY}}|$(escape_replacement "$COS_COMPANY")|g" \
    -e "s|{{EMAIL}}|$(escape_replacement "$COS_EMAIL")|g" \
    -e "s|{{TIMEZONE}}|$(escape_replacement "$COS_TIMEZONE")|g" \
    -e "s|{{WORK_HOURS}}|$(escape_replacement "$COS_WORK_HOURS")|g" \
    -e "s|{{COS_HOME}}|$(escape_replacement "$COS_HOME")|g" \
    "$file" > "$tmp"
  mv "$tmp" "$file"
}

make_dir() {
  local dir="$1"
  [ -d "$dir" ] && return 0
  if [ "$DRY_RUN" -eq 1 ]; then say "  would mkdir  $dir"; return 0; fi
  mkdir -p "$dir"
}

# copy_if_missing SOURCE DESTINATION [--raw]
# The one write primitive. An existing destination is never touched.
copy_if_missing() {
  local src="$1" dest="$2" raw="${3:-}"
  [ -f "$src" ] || die "missing source file: $src"

  if [ -e "$dest" ]; then
    skip "$(short "$dest")"
    SKIPPED=$((SKIPPED + 1))
    return 0
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    say "  would create $(short "$dest")"
    CREATED=$((CREATED + 1))
    return 0
  fi

  make_dir "$(dirname "$dest")"
  cp "$src" "$dest"
  [ "$raw" = "--raw" ] || substitute_placeholders "$dest"
  ok "$(short "$dest")"
  CREATED=$((CREATED + 1))
}

# ------------------------------------------------------------------------------- checks ----

[ -f "$SCRIPT_DIR/CLAUDE.md" ] || die "run this from a checkout of the chief-of-staff repo"

case "$COS_HOME" in
  /*) ;;
  *) die "--root must be an absolute path (got: $COS_HOME)" ;;
esac

# Resolve every location once, here, so the path substituted into CLAUDE.md, the memory
# import line, and the root recorded in paths.json are the same string by construction.
# Cursor home is canonicalized the same way so ~/.cursor/commands records agree.
HOME_CANON="$(canonicalize "$HOME")"
CLAUDE_HOME="$(canonicalize "$CLAUDE_HOME")"
CURSOR_HOME="$(canonicalize "$CURSOR_HOME")"
COS_HOME="$(canonicalize "$COS_HOME")"
COMMANDS_DIR="$CLAUDE_HOME/commands"
CURSOR_COMMANDS_DIR="$CURSOR_HOME/commands"

# ------------------------------------------------------------------------------- config ----

say ""
say "${C_BOLD}Chief of Staff — install${C_OFF}"
say "  install root : $(short "$COS_HOME")"
say "  claude home  : $(short "$CLAUDE_HOME")"
say "  cursor home  : $(short "$CURSOR_HOME")"
[ "$DRY_RUN" -eq 1 ] && say "  mode         : dry run (nothing will be written)"
say ""

DEFAULT_NAME="$(git_config user.name)"; DEFAULT_NAME="${DEFAULT_NAME:-${USER:-operator}}"
DEFAULT_EMAIL="$(git_config user.email)"; DEFAULT_EMAIL="${DEFAULT_EMAIL:-you@example.com}"

say "Profile (used to fill placeholders; edit the files later if you change your mind)"
ask COS_NAME       "Your name"          "$DEFAULT_NAME"
ask COS_ROLE       "Your role"          "Operator"
ask COS_COMPANY    "Company"            "Independent"
ask COS_EMAIL      "Primary email"      "$DEFAULT_EMAIL"
ask COS_TIMEZONE   "Timezone"           "$(detect_timezone)"
ask COS_WORK_HOURS "Working hours"      "09:00-18:00"
say ""

# ------------------------------------------------------------------------------ install ----

say "State"
make_dir "$COS_HOME"
make_dir "$COS_HOME/contacts"
make_dir "$COS_HOME/briefings"
make_dir "$COS_HOME/drafts"
make_dir "$COS_HOME/work-log"

copy_if_missing "$SCRIPT_DIR/CLAUDE.md"      "$COS_HOME/CLAUDE.md"
copy_if_missing "$SCRIPT_DIR/goals.yaml"     "$COS_HOME/goals.yaml"
copy_if_missing "$SCRIPT_DIR/my-tasks.yaml"  "$COS_HOME/my-tasks.yaml"
copy_if_missing "$SCRIPT_DIR/schedules.yaml" "$COS_HOME/schedules.yaml"

say ""
say "Contacts"
for contact in "$SCRIPT_DIR"/contacts/*.md; do
  [ -e "$contact" ] || continue
  copy_if_missing "$contact" "$COS_HOME/contacts/$(basename "$contact")"
done

say ""
say "Work log"
for work_log_file in "$SCRIPT_DIR"/work-log/*.md; do
  [ -e "$work_log_file" ] || continue
  copy_if_missing "$work_log_file" "$COS_HOME/work-log/$(basename "$work_log_file")"
done

say ""
say "Templates"
for template_file in "$SCRIPT_DIR"/templates/*.md; do
  [ -e "$template_file" ] || continue
  copy_if_missing "$template_file" "$COS_HOME/templates/$(basename "$template_file")"
done

say ""
say "Commands"
make_dir "$COMMANDS_DIR"
make_dir "$CURSOR_COMMANDS_DIR"
for command_file in "$SCRIPT_DIR"/commands/*.md; do
  [ -e "$command_file" ] || continue
  copy_if_missing "$command_file" "$COMMANDS_DIR/$(basename "$command_file")"
  copy_if_missing "$command_file" "$CURSOR_COMMANDS_DIR/$(basename "$command_file")"
done

say ""
say "Support files"
copy_if_missing "$SCRIPT_DIR/core/paths.py"               "$COS_HOME/core/paths.py" --raw
copy_if_missing "$SCRIPT_DIR/docs/mcp-servers.md"         "$COS_HOME/docs/mcp-servers.md"
copy_if_missing "$SCRIPT_DIR/docs/cursor-projects.md"     "$COS_HOME/docs/cursor-projects.md"
copy_if_missing "$SCRIPT_DIR/docs/pstack.md"              "$COS_HOME/docs/pstack.md"
copy_if_missing "$SCRIPT_DIR/.cursor/mcp.json.example"    "$COS_HOME/docs/mcp.json.example" --raw

# The path contract is generated, not authored, so regenerating it is not a destructive write.
if command -v python3 >/dev/null 2>&1; then
  if [ "$DRY_RUN" -eq 1 ]; then
    say "  would write  $(short "$COS_HOME")/paths.json"
  else
    manifest_existed=0
    [ -f "$COS_HOME/paths.json" ] && manifest_existed=1
    CLAUDE_HOME="$CLAUDE_HOME" \
      python3 "$COS_HOME/core/paths.py" --root "$COS_HOME" --ensure --write >/dev/null
    if [ "$manifest_existed" -eq 1 ]; then
      printf '%s  regen  %s  %s/paths.json\n' "$C_DIM" "$C_OFF" "$(short "$COS_HOME")"
    else
      ok "$(short "$COS_HOME")/paths.json ${C_DIM}(generated)${C_OFF}"
    fi
  fi
else
  warn "python3 not found — paths.json was not generated. Agents will fall back to \$COS_HOME."
fi

# ------------------------------------------------------------------- wire up user memory ----

IMPORT_LINE="@$COS_HOME/CLAUDE.md"
USER_MEMORY="$CLAUDE_HOME/CLAUDE.md"

say ""
say "Claude Code memory"
if [ ! -e "$USER_MEMORY" ]; then
  if [ "$DRY_RUN" -eq 1 ]; then
    say "  would create $(short "$USER_MEMORY") importing the OS"
  else
    {
      printf '# Personal Claude memory\n\n'
      printf 'Chief of Staff OS — the file below defines identity, constraints, and modes.\n\n'
      printf '%s\n' "$IMPORT_LINE"
    } > "$USER_MEMORY"
    ok "$(short "$USER_MEMORY")"
    CREATED=$((CREATED + 1))
  fi
elif grep -qF "$IMPORT_LINE" "$USER_MEMORY" 2>/dev/null; then
  skip "$(short "$USER_MEMORY") — already imports the OS"
  SKIPPED=$((SKIPPED + 1))
elif [ "$MERGE_MEMORY" -eq 1 ]; then
  if [ "$DRY_RUN" -eq 1 ]; then
    say "  would append the import line to $(short "$USER_MEMORY")"
  else
    printf '\n%s\n' "$IMPORT_LINE" >> "$USER_MEMORY"
    ok "$(short "$USER_MEMORY") — import line appended"
  fi
else
  warn "$(short "$USER_MEMORY") already exists and was left untouched."
  say ""
  say "  Add this line to it so Claude Code loads the OS:"
  say ""
  say "      $IMPORT_LINE"
  say ""
  say "  Or re-run with --merge-memory to have the installer append it."
fi

# -------------------------------------------------------------------------------- verify ----

if [ "$DRY_RUN" -eq 0 ]; then
  installed_files=("$COS_HOME"/*.yaml "$COS_HOME"/CLAUDE.md "$COS_HOME"/contacts/*.md)
  for command_file in "$SCRIPT_DIR"/commands/*.md; do
    installed_files+=("$COMMANDS_DIR/$(basename "$command_file")")
    installed_files+=("$CURSOR_COMMANDS_DIR/$(basename "$command_file")")
  done
  for candidate in "${installed_files[@]}"; do
    case "$candidate" in */_template.md) continue ;; esac
    [ -f "$candidate" ] || continue
    if grep -qE '\{\{[A-Z_]+\}\}' "$candidate"; then
      warn "unsubstituted placeholders in $(short "$candidate")"
    fi
  done
fi

# --------------------------------------------------------------------------------- done ----

say ""
say "${C_BOLD}Done.${C_OFF} $CREATED created, $SKIPPED left alone."
if [ "${#WARNINGS[@]}" -gt 0 ]; then
  say "${C_WARN}${#WARNINGS[@]} warning(s) above.${C_OFF}"
fi
say ""
say "Next:"
say "  1. Edit $(short "$COS_HOME")/goals.yaml — it is the prioritization truth, and the"
say "     shipped goals are someone else's."
say "  2. Connect Gmail and Google Calendar: see $(short "$COS_HOME")/docs/mcp-servers.md"
say "     Cursor: copy $(short "$COS_HOME")/docs/mcp.json.example to ~/.cursor/mcp.json"
say "  3. Open this repo in Cursor (or Claude Code) and run:  ${C_BOLD}/gm${C_OFF}"
say ""
