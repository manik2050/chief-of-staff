# Existing files

The installer never overwrites, appends to, or deletes a file that already exists. It warns
and continues.

## Sub-features

- `existing-memory` leaves a pre-seeded `~/.claude/CLAUDE.md` unchanged.
- `existing-goals` leaves a pre-seeded `goals.yaml` unchanged.
- `existing-warn` prints `already exists and was left untouched`.

## How to get to it (user POV)

- Create the destination files, then run `./install.sh --yes`.
- Run `./.cursor/skills/verify-cos/verify-cos.sh drive existing-files`.

## Driving it with verify-cos

Preconditions:

- `verify-cos.sh doctor` printed `pstack=enabled`.
- The helper seeds memory and goals before it runs the installer.

- **Install over sentinels.** Run
  `./.cursor/skills/verify-cos/verify-cos.sh drive existing-files`. Exit code `0`.
- **Read memory.** The seeded file still equals `MY OWN MEMORY — do not touch`.
- **Read the warning.** `existing-files.log` contains
  `already exists and was left untouched`.
- **Proof.** Keep `existing-files.log` and the unchanged sentinel text.

## Gotchas

- `--merge-memory` is a separate flag. This feature is the default, which does not merge.
- A missing warning with unchanged bytes is still a fail. The user has to see the skip.
