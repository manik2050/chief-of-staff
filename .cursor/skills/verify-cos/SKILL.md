---
name: verify-cos
description: Drive the Chief of Staff installer in an isolated HOME the way a user does. Use when proving install.sh, --dry-run, re-install, non-destructiveness, or that this repo enables pstack.
---

# Verify Chief of Staff

The product a user runs is `./install.sh`. There is no server. Every drive uses a throwaway
HOME. Never point `HOME`, `CLAUDE_HOME`, `COS_HOME`, or `--cursor-home` at the operator's
real directories.

Agents working on this repo read this skill mid-task. The installer test is the full suite.
A named feature drive is the smaller proof when you changed one path.

## Launch

No long-lived process. "Launch" means the repo scripts are executable and you have a run id.

```bash
./.cursor/skills/verify-cos/verify-cos.sh doctor
```

Teardown is `cleanup`. It deletes only scratch homes recorded in `artifacts/*/homes.txt`.
It leaves `artifacts/<run-id>/` in place.

## Doctor

Run doctor first if anything looks off.

It checks that `install.sh` and `tests/install_test.sh` are executable, that
`.cursor/settings.json` enables pstack, that `.cursor/rules/pstack-execution.mdc` exists,
and that `bash` and `python3` are on `PATH`.

A healthy print looks like:

```text
ok doctor repo=/path/to/chief-of-staff pstack=enabled
```

If pstack is off, stop. Do not invent a playbook. Print "pstack unavailable" and keep the
owner and tier from `/dispatch`.

## Drive

Use the helper. It copies the same flags as `tests/install_test.sh` (Ada Lovelace,
`ada@example.com`, `--yes`, `NO_COLOR=1`).

```bash
./.cursor/skills/verify-cos/verify-cos.sh drive dry-run
./.cursor/skills/verify-cos/verify-cos.sh drive fresh-install
./.cursor/skills/verify-cos/verify-cos.sh drive reinstall
./.cursor/skills/verify-cos/verify-cos.sh drive existing-files
./.cursor/skills/verify-cos/verify-cos.sh drive suite
```

`suite` runs `./tests/install_test.sh` and requires a last line of `, 0 failed`.

Read `features/README.md` and drive every mapped entry point that your change can touch.
Do not report a skipped entry point as verified through a different path.

Stable handles:

- `install.sh --dry-run` prints `mode         : dry run (nothing will be written)`
- a successful install prints `Done.` with a created count
- a second install over the same HOME prints `0 created`
- an existing user file produces `already exists and was left untouched`

## Evidence

Proof lives in `.cursor/skills/verify-cos/artifacts/<run-id>/`. Keep the command log and
the observable after-state. A log without a file-tree or emptiness check is not proof.

- Exercise `install.sh` (or `install_test.sh`), not an internal helper.
- Capture the action and the resulting files. Dry-run proof is an empty HOME plus the mode
  line. Install proof is `CLAUDE.md` on disk with substituted values.
- `--dry-run` must write nothing. Confirm by counting files under the throwaway HOME.
- Do not mock the installer.

This directory is gitignored except the skill files. Do not commit run logs.

## Cleanup

```bash
./.cursor/skills/verify-cos/verify-cos.sh cleanup
```

Cleanup removes scratch homes named in `homes.txt`. It does not delete `artifacts/`.
After cleanup, confirm the run directory still exists.

## Helpers

`./.cursor/skills/verify-cos/verify-cos.sh` is executable. Invocation is in Drive.

`./tests/install_test.sh` is the full user-path suite. Prefer `drive suite` after an
installer or path-contract change.

`./install.sh --dry-run` against a real HOME is forbidden here. The helper always
creates `/tmp/cos-verify.*` (or `$TMPDIR/cos-verify.*`).
