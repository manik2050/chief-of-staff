#!/usr/bin/env bash
#
# Isolated HOME drives of install.sh. Never points at the operator's real home.
#
#   ./.cursor/skills/verify-cos/verify-cos.sh doctor
#   ./.cursor/skills/verify-cos/verify-cos.sh drive dry-run
#   ./.cursor/skills/verify-cos/verify-cos.sh suite
#   ./.cursor/skills/verify-cos/verify-cos.sh cleanup
#
# Evidence stays under artifacts/<run-id>/. Scratch homes are listed in homes.txt.

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SKILL_DIR/../../.." && pwd)"
ARTIFACT_ROOT="$SKILL_DIR/artifacts"
RUN_ID="${COS_VERIFY_RUN_ID:-$(date +%Y%m%dT%H%M%S)-$$}"
RUN_DIR="$ARTIFACT_ROOT/$RUN_ID"
HOMES_FILE="$RUN_DIR/homes.txt"

die() { printf 'error %s\n' "$*" >&2; exit 1; }

need_repo() {
  [ -x "$REPO_DIR/install.sh" ] || die "missing executable $REPO_DIR/install.sh"
  [ -x "$REPO_DIR/tests/install_test.sh" ] || die "missing executable $REPO_DIR/tests/install_test.sh"
}

prepare_run() {
  mkdir -p "$RUN_DIR"
  : >> "$HOMES_FILE"
}

new_home() {
  local home_dir
  home_dir="$(mktemp -d "${TMPDIR:-/tmp}/cos-verify.XXXXXX")"
  home_dir="$(cd "$home_dir" && pwd -P)"
  printf '%s\n' "$home_dir" >> "$HOMES_FILE"
  printf '%s' "$home_dir"
}

run_install() {
  local home_dir="$1"
  shift
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

count_home_entries() {
  find "$1" -mindepth 1 | wc -l | tr -d ' '
}

cmd_doctor() {
  need_repo
  [ -f "$REPO_DIR/.cursor/settings.json" ] || die "missing .cursor/settings.json"
  grep -qF '"pstack"' "$REPO_DIR/.cursor/settings.json" \
    && grep -qF '"enabled": true' "$REPO_DIR/.cursor/settings.json" \
    || die "pstack is not enabled in .cursor/settings.json"
  [ -f "$REPO_DIR/.cursor/rules/pstack-execution.mdc" ] \
    || die "missing .cursor/rules/pstack-execution.mdc"
  command -v bash >/dev/null 2>&1 || die "bash is required"
  command -v python3 >/dev/null 2>&1 || die "python3 is required"
  printf 'ok doctor repo=%s pstack=enabled\n' "$REPO_DIR"
}

cmd_drive() {
  local feature="${1:-}"
  [ -n "$feature" ] || die "drive needs a feature id (dry-run, fresh-install, reinstall, existing-files, suite)"
  need_repo
  cmd_doctor >/dev/null
  prepare_run
  case "$feature" in
    dry-run) drive_dry_run ;;
    fresh-install) drive_fresh_install ;;
    reinstall) drive_reinstall ;;
    existing-files) drive_existing_files ;;
    suite) drive_suite ;;
    *) die "unknown feature: $feature" ;;
  esac
  printf 'ok drive %s artifacts=%s\n' "$feature" "$RUN_DIR"
}

drive_dry_run() {
  local home_dir log
  home_dir="$(new_home)"
  log="$RUN_DIR/dry-run.log"
  run_install "$home_dir" --dry-run > "$log" 2>&1 || die "dry-run exited non-zero; see $log"
  grep -q 'mode         : dry run (nothing will be written)' "$log" \
    || die "dry-run log missing mode line; see $log"
  [ "$(count_home_entries "$home_dir")" = "0" ] \
    || die "dry-run wrote under $home_dir; see $log"
  printf 'empty\n' > "$RUN_DIR/dry-run.home-count"
}

drive_fresh_install() {
  local home_dir log cos
  home_dir="$(new_home)"
  log="$RUN_DIR/fresh-install.log"
  run_install "$home_dir" > "$log" 2>&1 || die "fresh install exited non-zero; see $log"
  cos="$home_dir/.claude/chief-of-staff"
  [ -f "$cos/CLAUDE.md" ] || die "fresh install missing $cos/CLAUDE.md"
  [ -f "$cos/work-log/_template.md" ] || die "fresh install missing work-log template"
  [ -f "$home_dir/.cursor/commands/dispatch.md" ] || die "fresh install missing Cursor /dispatch"
  grep -q "Ada Lovelace" "$cos/CLAUDE.md" || die "name was not substituted"
  [ ! -e "$cos/.cursor/skills" ] || die "installer copied .cursor/skills into the install root"
  [ ! -e "$cos/docs/build-log" ] || die "installer copied docs/build-log into the install root"
  printf '%s\n' "$cos" > "$RUN_DIR/fresh-install.cos"
}

drive_reinstall() {
  local home_dir first second before after
  drive_fresh_install
  home_dir="$(tail -1 "$HOMES_FILE")"
  before="$RUN_DIR/reinstall.before"
  after="$RUN_DIR/reinstall.after"
  ( cd "$home_dir" && find . -type f -print | LC_ALL=C sort ) > "$before"
  run_install "$home_dir" > "$RUN_DIR/reinstall.log" 2>&1 || die "reinstall exited non-zero"
  ( cd "$home_dir" && find . -type f -print | LC_ALL=C sort ) > "$after"
  cmp -s "$before" "$after" || die "reinstall changed the file list; see $RUN_DIR"
  grep -q "0 created" "$RUN_DIR/reinstall.log" || die "reinstall did not report 0 created"
}

drive_existing_files() {
  local home_dir cos log
  home_dir="$(new_home)"
  cos="$home_dir/.claude/chief-of-staff"
  mkdir -p "$cos/contacts" "$home_dir/.claude/commands"
  printf 'MY OWN MEMORY — do not touch\n' > "$home_dir/.claude/CLAUDE.md"
  printf '# my real goals\ngoals: []\n' > "$cos/goals.yaml"
  log="$RUN_DIR/existing-files.log"
  run_install "$home_dir" > "$log" 2>&1 || die "install over existing files exited non-zero"
  [ "$(cat "$home_dir/.claude/CLAUDE.md")" = "MY OWN MEMORY — do not touch" ] \
    || die "installer overwrote user memory"
  grep -q "already exists and was left untouched" "$log" \
    || die "installer did not warn about existing memory"
}

drive_suite() {
  "$REPO_DIR/tests/install_test.sh" > "$RUN_DIR/suite.log" 2>&1 \
    || die "install_test.sh failed; see $RUN_DIR/suite.log"
  tail -1 "$RUN_DIR/suite.log" | grep -q ', 0 failed$' \
    || die "install_test.sh did not report 0 failed; see $RUN_DIR/suite.log"
}

cmd_cleanup() {
  local home_dir
  [ -d "$ARTIFACT_ROOT" ] || { printf 'ok cleanup nothing\n'; return 0; }
  shopt -s nullglob
  for homes in "$ARTIFACT_ROOT"/*/homes.txt; do
    while IFS= read -r home_dir; do
      [ -n "$home_dir" ] || continue
      case "$home_dir" in
        *cos-verify.*) rm -rf "$home_dir" ;;
      esac
    done < "$homes"
  done
  printf 'ok cleanup artifacts kept under %s\n' "$ARTIFACT_ROOT"
}

usage() {
  cat <<'EOF'
verify-cos.sh doctor
verify-cos.sh drive dry-run|fresh-install|reinstall|existing-files|suite
verify-cos.sh cleanup
EOF
}

cmd="${1:-}"
shift || true
case "$cmd" in
  doctor) cmd_doctor ;;
  drive) cmd_drive "${1:-}" ;;
  cleanup) cmd_cleanup ;;
  -h|--help|"") usage; [ -n "$cmd" ] || exit 1 ;;
  *) die "unknown command: $cmd" ;;
esac
