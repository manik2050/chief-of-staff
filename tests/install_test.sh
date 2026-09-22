#!/usr/bin/env bash
#
# tests/install_test.sh — prove the installer is idempotent and non-destructive.
#
# Everything runs inside a temporary HOME. Your real ~/.claude is never touched.
#
#   ./tests/install_test.sh

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/cos-test.XXXXXX")"
trap 'rm -rf "$WORK_DIR"' EXIT

# Resolve the scratch root before deriving anything from it. On macOS /tmp is a symlink to
# /private/tmp and $TMPDIR lives under /var -> /private/var, so an unresolved WORK_DIR makes
# every path assertion below compare two spellings of the same directory.
WORK_DIR="$(cd "$WORK_DIR" && pwd -P)"

PASSED=0
FAILED=0

pass() { printf '  ok    %s\n' "$1"; PASSED=$((PASSED + 1)); }
fail() { printf '  FAIL  %s\n' "$1"; FAILED=$((FAILED + 1)); }
head_() { printf '\n%s\n' "$1"; }

check()      { if [ "$2" = "$3" ]; then pass "$1"; else fail "$1 (expected '$3', got '$2')"; fi; }
check_file() { if [ -f "$1" ]; then pass "exists: ${1#$WORK_DIR/}"; else fail "missing: ${1#$WORK_DIR/}"; fi; }
check_dir()  { if [ -d "$1" ]; then pass "exists: ${1#$WORK_DIR/}/"; else fail "missing dir: ${1#$WORK_DIR/}/"; fi; }

# Absolute path with symlinks resolved. Works on a path that does not exist yet, and does not
# depend on realpath(1), which macOS did not ship until Monterey.
realpath_of() {
  local input="$1" suffix="" parent
  while [ -n "$input" ] && [ "$input" != "/" ] && [ ! -d "$input" ]; do
    suffix="/$(basename "$input")$suffix"
    parent="$(dirname "$input")"
    [ "$parent" = "$input" ] && break
    input="$parent"
  done
  if [ -d "$input" ]; then printf '%s%s' "$(cd "$input" && pwd -P)" "$suffix"
  else printf '%s' "$1"
  fi
}

# The "root" value recorded in a generated paths.json.
json_root() { sed -n 's/^[[:space:]]*"root":[[:space:]]*"\(.*\)",\{0,1\}$/\1/p' "$1" | head -1; }

hash_file() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}'
  elif command -v shasum   >/dev/null 2>&1; then shasum -a 256 "$1" | awk '{print $1}'
  else cksum "$1" | awk '{print $1, $2}'
  fi
}

# A stable fingerprint of every file under a directory: relative path plus content hash.
fingerprint() {
  local root="$1"
  [ -d "$root" ] || { printf '<absent>\n'; return; }
  ( cd "$root" && find . -type f -print | LC_ALL=C sort | while read -r f; do
      printf '%s  %s\n' "$(hash_file "$f")" "$f"
    done )
}

run_install() {
  local home_dir="$1"; shift
  HOME="$home_dir" CLAUDE_HOME="$home_dir/.claude" COS_HOME="" NO_COLOR=1 \
    "$REPO_DIR/install.sh" \
      --name "Ada Lovelace" \
      --role "Chief Executive" \
      --company "Analytical Engines" \
      --email "ada@example.com" \
      --timezone "Europe/London" \
      --work-hours "08:30-17:30" \
      --yes "$@" < /dev/null
}

printf 'Chief of Staff — installer test\n'
printf 'workspace: %s\n' "$WORK_DIR"

# ------------------------------------------------------------------ 1. dry run writes nothing
head_ "1. --dry-run writes nothing"
DRY_HOME="$WORK_DIR/home-dry"
mkdir -p "$DRY_HOME"
run_install "$DRY_HOME" --dry-run > "$WORK_DIR/dry.log" 2>&1 || fail "dry run exited non-zero"
check "home is still empty" "$(find "$DRY_HOME" -mindepth 1 | wc -l | tr -d ' ')" "0"

# ---------------------------------------------------------------------- 2. fresh install
head_ "2. fresh install"
H1="$WORK_DIR/home-fresh"
mkdir -p "$H1"
run_install "$H1" > "$WORK_DIR/install1.log" 2>&1 || fail "install exited non-zero"

COS="$H1/.claude/chief-of-staff"
check_file "$COS/CLAUDE.md"
check_file "$COS/goals.yaml"
check_file "$COS/my-tasks.yaml"
check_file "$COS/schedules.yaml"
check_file "$COS/core/paths.py"
check_file "$COS/docs/mcp-servers.md"
check_file "$COS/contacts/_template.md"
check_file "$COS/contacts/jordan-rivera.md"
check_dir  "$COS/briefings"
check_dir  "$COS/drafts"
check_dir  "$COS/work-log"
check_file "$COS/work-log/_template.md"
check_file "$COS/work-log/README.md"
check_file "$COS/templates/weekly-status.md"
check_file "$COS/docs/cursor-projects.md"
check_file "$COS/docs/pstack.md"
check_file "$COS/docs/mcp.json.example"
check_file "$H1/.claude/commands/gm.md"
check_file "$H1/.claude/commands/triage.md"
check_file "$H1/.claude/commands/my-tasks.md"
check_file "$H1/.claude/commands/enrich.md"
check_file "$H1/.claude/commands/dispatch.md"
check_file "$H1/.cursor/commands/gm.md"
check_file "$H1/.cursor/commands/dispatch.md"
check_file "$H1/.claude/CLAUDE.md"

grep -q '^tier: balanced$' "$COS/work-log/_template.md" \
  && pass "work-log template includes a routing tier" \
  || fail "work-log template is missing its routing tier"
grep -q '^approval_required: false$' "$COS/work-log/_template.md" \
  && pass "work-log template includes the approval gate" \
  || fail "work-log template is missing its approval gate"
grep -q '^approval_reasons: \[\]$' "$COS/work-log/_template.md" \
  && pass "work-log template includes approval reasons" \
  || fail "work-log template is missing approval reasons"
grep -qF 'explore` — read-only research' "$H1/.claude/commands/dispatch.md" \
  && grep -qF 'Tier: `cost`' "$H1/.claude/commands/dispatch.md" \
  && pass "/dispatch maps explore to cost" \
  || fail "/dispatch is missing explore → cost routing"
grep -qF 'Tier: `balanced`' "$H1/.claude/commands/dispatch.md" \
  && pass "/dispatch maps implement to balanced" \
  || fail "/dispatch is missing implement → balanced routing"
grep -qF 'Tier: `intelligence`' "$H1/.claude/commands/dispatch.md" \
  && pass "/dispatch maps review to intelligence" \
  || fail "/dispatch is missing review → intelligence routing"
grep -qF 'request never routes down.' "$H1/.claude/commands/dispatch.md" \
  && pass "/dispatch preserves the intelligence risk floor" \
  || fail "/dispatch is missing its intelligence risk floor"
grep -qF 'Set `approval_required: true`' "$H1/.claude/commands/dispatch.md" \
  && grep -qF 'ask again immediately before the gated action' "$H1/.claude/commands/dispatch.md" \
  && pass "/dispatch records gates without treating them as approval" \
  || fail "/dispatch approval gates are incomplete"
grep -qF 'Bypass or missing routing tools may choose `balanced`' \
    "$H1/.cursor/commands/dispatch.md" \
  && pass "Cursor /dispatch keeps policy active during routing bypass" \
  || fail "Cursor /dispatch can bypass routing policy"
grep -qF '**Execution: `investigation`.**' "$H1/.claude/commands/dispatch.md" \
  && pass "/dispatch maps explore to investigation" \
  || fail "/dispatch is missing explore → investigation"
grep -qF '**Execution: `feature`.**' "$H1/.claude/commands/dispatch.md" \
  && pass "/dispatch maps implement to feature" \
  || fail "/dispatch is missing implement → feature"
grep -qF '**Execution: `interrogate`.**' "$H1/.claude/commands/dispatch.md" \
  && pass "/dispatch maps review to interrogate" \
  || fail "/dispatch is missing review → interrogate"
grep -qF 'pstack unavailable — owner runs without a named playbook' \
    "$H1/.claude/commands/dispatch.md" \
  && pass "/dispatch degrades when pstack is off" \
  || fail "/dispatch is missing its pstack-unavailable line"
grep -qE '^execution: null$' "$COS/work-log/_template.md" \
  && pass "work-log template includes an execution playbook field" \
  || fail "work-log template is missing its execution field"
grep -qF 'pstack unavailable — owner runs without a named playbook' \
    "$H1/.cursor/commands/dispatch.md" \
  && pass "Cursor /dispatch keeps pstack degradation" \
  || fail "Cursor /dispatch dropped pstack degradation"
if grep -qF '"pstack"' "$REPO_DIR/.cursor/settings.json" \
   && grep -qF '"enabled": true' "$REPO_DIR/.cursor/settings.json"; then
  pass "repo enables pstack in .cursor/settings.json"
else
  fail "repo .cursor/settings.json does not enable pstack"
fi
grep -qF '`CLAUDE.md` §4 outranks every pstack playbook' \
    "$REPO_DIR/.cursor/rules/pstack-execution.mdc" \
  && pass "pstack-execution rule keeps the approval override" \
  || fail "pstack-execution rule is missing the CLAUDE.md §4 override"

if command -v python3 >/dev/null 2>&1; then
  check_file "$COS/paths.json"
  # Compare resolved against resolved: paths.py canonicalizes, so anything under a symlinked
  # /tmp or $TMPDIR would otherwise fail on a spelling difference rather than a real defect.
  check "paths.json points at the install root" \
    "$(realpath_of "$(json_root "$COS/paths.json")")" "$(realpath_of "$COS")"
  # And the installer must agree with it verbatim, or the OS file and paths.json diverge.
  check "installer and paths.json agree verbatim" "$(json_root "$COS/paths.json")" "$COS"
  grep -qF "$(json_root "$COS/paths.json")" "$COS/CLAUDE.md" \
    && pass "OS file carries the same root as paths.json" \
    || fail "OS file and paths.json disagree on the install root"
  grep -qF "$(json_root "$COS/paths.json")/CLAUDE.md" "$H1/.claude/CLAUDE.md" \
    && pass "memory import line carries the same root as paths.json" \
    || fail "memory import line and paths.json disagree on the install root"
  if python3 - "$COS/paths.json" "$COS/work-log" <<'PY'
import json, sys
data = json.load(open(sys.argv[1]))
got = data.get("dirs", {}).get("work_log")
sys.exit(0 if got == sys.argv[2] else 1)
PY
  then
    pass "paths.json lists work_log at the install dir"
  else
    fail "paths.json missing or wrong work_log dir"
  fi
fi

# ------------------------------------------------------------------ 3. placeholders resolved
head_ "3. placeholder substitution"
if grep -rlE '\{\{[A-Z_]+\}\}' "$COS" "$H1/.claude/commands" "$H1/.cursor/commands" 2>/dev/null \
     | grep -v '_template.md' | grep -q .; then
  fail "unsubstituted placeholders remain"
  grep -rlE '\{\{[A-Z_]+\}\}' "$COS" "$H1/.claude/commands" "$H1/.cursor/commands" 2>/dev/null | grep -v '_template.md'
else
  pass "no unsubstituted placeholders in installed files"
fi
grep -q "Ada Lovelace" "$COS/CLAUDE.md"        && pass "name substituted into CLAUDE.md"        || fail "name missing from CLAUDE.md"
grep -q "Europe/London" "$COS/CLAUDE.md"       && pass "timezone substituted into CLAUDE.md"    || fail "timezone missing from CLAUDE.md"
grep -q "Europe/London" "$COS/schedules.yaml"  && pass "timezone substituted into schedules"    || fail "timezone missing from schedules.yaml"
grep -q "Ada Lovelace" "$H1/.claude/commands/gm.md" && pass "name substituted into /gm"         || fail "name missing from gm.md"
grep -q "Ada Lovelace" "$H1/.cursor/commands/gm.md" && pass "name substituted into Cursor /gm"  || fail "name missing from Cursor gm.md"
grep -qF "@$COS/CLAUDE.md" "$H1/.claude/CLAUDE.md"  && pass "user memory imports the OS"        || fail "user memory does not import the OS"
grep -qF "@klodr/gmail-mcp" "$COS/docs/mcp.json.example" \
  && pass "pinned Gmail MCP package is installed" || fail "mcp.json.example missing @klodr/gmail-mcp"
grep -qF "@cocal/google-calendar-mcp" "$COS/docs/mcp.json.example" \
  && pass "pinned Calendar MCP package is installed" || fail "mcp.json.example missing @cocal/google-calendar-mcp"
if grep -qE '<[a-z-]*mcp' "$COS/docs/mcp.json.example" "$COS/docs/mcp-servers.md"; then
  fail "placeholder MCP package names remain in installed docs"
else
  pass "no placeholder MCP package names in installed docs"
fi

# -------------------------------------------------------------------------- 4. idempotency
head_ "4. re-running changes nothing"
BEFORE="$(fingerprint "$H1")"
run_install "$H1" > "$WORK_DIR/install2.log" 2>&1 || fail "second install exited non-zero"
AFTER="$(fingerprint "$H1")"
if [ "$BEFORE" = "$AFTER" ]; then
  pass "every file is byte-identical after a second run"
else
  fail "second run modified files:"
  diff <(printf '%s\n' "$BEFORE") <(printf '%s\n' "$AFTER") || true
fi
if grep -q "0 created" "$WORK_DIR/install2.log"; then
  pass "second run reports 0 created"
else
  fail "second run reported creations: $(grep -E '^Done\.' "$WORK_DIR/install2.log" || true)"
fi

# -------------------------------------------------------------------- 5. non-destructiveness
head_ "5. existing user files are never touched"
H2="$WORK_DIR/home-existing"
COS2="$H2/.claude/chief-of-staff"
mkdir -p "$COS2/contacts" "$H2/.claude/commands"
printf 'MY OWN MEMORY — do not touch\n'            > "$H2/.claude/CLAUDE.md"
printf '# my real goals\ngoals: []\n'              > "$COS2/goals.yaml"
printf 'my own gm command\n'                       > "$H2/.claude/commands/gm.md"
printf 'name: Someone Real\n'                      > "$COS2/contacts/jordan-rivera.md"
SENTINELS="$(fingerprint "$H2")"

run_install "$H2" > "$WORK_DIR/install3.log" 2>&1 || fail "install over existing files exited non-zero"

check "user memory unchanged"   "$(cat "$H2/.claude/CLAUDE.md")"    "MY OWN MEMORY — do not touch"
check "user goals unchanged"    "$(cat "$COS2/goals.yaml")"         "$(printf '# my real goals\ngoals: []')"
check "user command unchanged"  "$(cat "$H2/.claude/commands/gm.md")" "my own gm command"
check "user contact unchanged"  "$(cat "$COS2/contacts/jordan-rivera.md")" "name: Someone Real"

if printf '%s\n' "$SENTINELS" | grep -q . && \
   printf '%s\n' "$(fingerprint "$H2")" | grep -qF "$(printf '%s\n' "$SENTINELS" | head -1)"; then
  pass "pre-existing file hashes still present after install"
else
  fail "a pre-existing file was modified"
fi

check_file "$COS2/my-tasks.yaml"
check_file "$H2/.claude/commands/triage.md"
if grep -q "already exists and was left untouched" "$WORK_DIR/install3.log"; then
  pass "installer warned about the existing user memory instead of editing it"
else
  fail "installer did not warn about the existing user memory"
fi

# ------------------------------------------------------------------------ 6. --merge-memory
head_ "6. --merge-memory appends the import line, once"
run_install "$H2" --merge-memory > "$WORK_DIR/install4.log" 2>&1 || fail "merge-memory run exited non-zero"
COUNT="$(grep -cF "@$COS2/CLAUDE.md" "$H2/.claude/CLAUDE.md" || true)"
check "import line present exactly once" "$COUNT" "1"
grep -q "MY OWN MEMORY" "$H2/.claude/CLAUDE.md" && pass "original memory content preserved" || fail "original memory content lost"
run_install "$H2" --merge-memory > "$WORK_DIR/install5.log" 2>&1 || fail "second merge-memory run exited non-zero"
COUNT2="$(grep -cF "@$COS2/CLAUDE.md" "$H2/.claude/CLAUDE.md" || true)"
check "still exactly once after a repeat run" "$COUNT2" "1"

# ---------------------------------------------------------------------- 7. custom --root
head_ "7. --root installs elsewhere"
H3="$WORK_DIR/home-root"
ALT="$WORK_DIR/alt-root"
mkdir -p "$H3"
run_install "$H3" --root "$ALT" > "$WORK_DIR/install6.log" 2>&1 || fail "--root install exited non-zero"
check_file "$ALT/CLAUDE.md"
check_file "$ALT/goals.yaml"
grep -qF "$ALT" "$ALT/CLAUDE.md" && pass "install root substituted into the OS" || fail "install root not substituted"

# --------------------------------------------------------------- 8. symlinked install root
# This is the macOS /tmp -> /private/tmp case, reproduced explicitly so it is covered on every
# platform. The installer resolves the root; every recorded path must agree on the resolved one.
head_ "8. symlinked install root resolves consistently"
H4="$WORK_DIR/home-symlink"
REAL_ROOT="$WORK_DIR/real-root"
LINK_ROOT="$WORK_DIR/link-root"
mkdir -p "$H4" "$REAL_ROOT"
ln -s "$REAL_ROOT" "$LINK_ROOT"
run_install "$H4" --root "$LINK_ROOT" > "$WORK_DIR/install7.log" 2>&1 \
  || fail "symlinked-root install exited non-zero"

check_file "$REAL_ROOT/CLAUDE.md"
grep -qF "$REAL_ROOT" "$REAL_ROOT/CLAUDE.md" \
  && pass "OS file records the resolved root" || fail "OS file does not record the resolved root"
grep -qF "@$REAL_ROOT/CLAUDE.md" "$H4/.claude/CLAUDE.md" \
  && pass "import line records the resolved root" || fail "import line does not record the resolved root"
if command -v python3 >/dev/null 2>&1; then
  check "paths.json records the resolved root" "$(json_root "$REAL_ROOT/paths.json")" "$REAL_ROOT"
fi
if grep -rqF "$LINK_ROOT/" "$REAL_ROOT" 2>/dev/null; then
  fail "an unresolved symlink path leaked into an installed file"
else
  pass "no unresolved symlink path in any installed file"
fi
BEFORE_LINK="$(fingerprint "$REAL_ROOT")"
run_install "$H4" --root "$LINK_ROOT" > "$WORK_DIR/install8.log" 2>&1 \
  || fail "second symlinked-root install exited non-zero"
check "still idempotent through the symlink" "$(fingerprint "$REAL_ROOT")" "$BEFORE_LINK"
grep -q "0 created" "$WORK_DIR/install8.log" \
  && pass "second symlinked-root run reports 0 created" || fail "second symlinked-root run created files"

# --------------------------------------------------------------------------- 9. yaml parses
head_ "9. shipped YAML parses"
if command -v python3 >/dev/null 2>&1 && python3 -c 'import yaml' 2>/dev/null; then
  for f in goals.yaml my-tasks.yaml schedules.yaml; do
    if python3 -c "import sys,yaml; yaml.safe_load(open('$REPO_DIR/$f'))" 2>/dev/null; then
      pass "parses: $f"
    else
      fail "does not parse: $f"
    fi
  done
else
  printf '  skip  PyYAML not installed\n'
fi

# -------------------------------------------------------------------------------- summary
printf '\n%s passed, %s failed\n' "$PASSED" "$FAILED"
[ "$FAILED" -eq 0 ]
