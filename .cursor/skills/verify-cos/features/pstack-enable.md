# Pstack enable

This repo turns the pstack plugin on for anyone who opens the folder. The installer does not
copy that setting into the install root. Agents that change `install.sh` must not start
shipping it there.

## Sub-features

- `pstack-settings` keeps `"pstack": { "enabled": true }` in `.cursor/settings.json`.
- `pstack-override` keeps the CLAUDE.md §4 line in `.cursor/rules/pstack-execution.mdc`.
- `pstack-repo-only` leaves the install root without `.cursor/skills/`.

## How to get to it (user POV)

- Open this folder in Cursor and look for `/poteto-mode`.
- Run `./.cursor/skills/verify-cos/verify-cos.sh doctor`.
- After a fresh install, confirm the install root has no copy of this skill.

## Driving it with verify-cos

Preconditions:

- The git checkout contains `.cursor/settings.json` and `.cursor/rules/pstack-execution.mdc`.

- **Doctor.** Run `./.cursor/skills/verify-cos/verify-cos.sh doctor`. Stdout contains
  `pstack=enabled`.
- **Read the override.** `.cursor/rules/pstack-execution.mdc` contains
  `` `CLAUDE.md` §4 outranks every pstack playbook ``.
- **Install without copying the skill.** Run
  `./.cursor/skills/verify-cos/verify-cos.sh drive fresh-install`. The install root in
  `fresh-install.cos` has no `.cursor/skills` directory and no `docs/build-log`.
- **Proof.** Keep the doctor line and the fresh-install log. `drive suite` also asserts
  the skill stays repo-only.

## Gotchas

- Enabling pstack in the plugin marketplace is user-scope. This feature only proves the
  committed project setting.
- `/setup-pstack` writes `~/.cursor/rules/pstack-models.mdc` on one machine. Do not commit
  that file. Doctor does not require it.
