# Fresh install

A first install into an empty home creates the OS tree, substitutes placeholders, and
installs `/dispatch` into both Claude and Cursor command dirs.

## Sub-features

- `install-tree` creates `CLAUDE.md`, `goals.yaml`, `work-log/`, and `paths.json`.
- `install-commands` copies commands into `~/.claude/commands` and `~/.cursor/commands`.
- `install-substitute` replaces `{{NAME}}` with `Ada Lovelace` in the OS file.

## How to get to it (user POV)

- Run `./install.sh --yes` with identity flags into an empty home.
- Run `./.cursor/skills/verify-cos/verify-cos.sh drive fresh-install`.
- Run `./.cursor/skills/verify-cos/verify-cos.sh drive suite` after installer edits.

## Driving it with verify-cos

Preconditions:

- `verify-cos.sh doctor` printed `pstack=enabled`.
- The throwaway HOME does not exist yet. The helper creates it.

- **Install.** Run `./.cursor/skills/verify-cos/verify-cos.sh drive fresh-install`. Exit
  code `0`.
- **Read the OS file.** Open `$HOME/.claude/chief-of-staff/CLAUDE.md` from
  `fresh-install.cos`. It contains `Ada Lovelace` and no `{{NAME}}`.
- **Read dispatch.** `$HOME/.cursor/commands/dispatch.md` exists and contains
  `pstack unavailable — owner runs without a named playbook`.
- **Proof.** Keep `fresh-install.log` and `fresh-install.cos`. The log contains `Done.`
  with a created count greater than zero.

## Gotchas

- `paths.json` is generated. Compare the recorded `root` to the resolved install directory,
  not to an unresolved `/tmp` symlink.
- The installer never copies `docs/build-log/` or `.cursor/skills/` into the install root.
  Their absence is required proof, not a miss.
