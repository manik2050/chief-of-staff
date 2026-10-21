# Chief of Staff verification map

This directory is the maintained source for verifying installer behavior. Read the index
before driving, then use the matching feature file as the recipe.

## Baseline preconditions

- Work from a git checkout of this repo. `install.sh` and `tests/install_test.sh` are
  executable.
- Run `./.cursor/skills/verify-cos/verify-cos.sh doctor` and require `pstack=enabled`.
- Every install uses a throwaway HOME created by the helper. Never the operator's `$HOME`.
- Identity flags match `tests/install_test.sh`. Name is `Ada Lovelace`. Email is
  `ada@example.com`. Timezone is `Europe/London`.
- Set `NO_COLOR=1` (the helper does this).
- Never drive an instance that was not started by this verification run.

## Driving conventions

- Start every recipe from an empty throwaway HOME unless the feature seeds files first.
- Treat every command as literal. Keep quoted names and flags unchanged.
- Run installs through `verify-cos.sh drive <feature>`.
- Restore nothing into the operator's home. Delete only helper scratch homes on cleanup.
- Keep proof artifacts under `artifacts/<run-id>/`.

## Proof and skip reporting

- Capture the user action and the resulting files, not only the exit code.
- CLI proof includes the command, stdout, stderr, and exit code (the helper log).
- Mutation proof includes a second read of the written file or an empty-home count.
- Record the feature ID with every artifact.
- Report an unreachable path with the attempted command and the unmet precondition.
- Do not report a skipped entry point as verified through a different path.

## Feature entry contract

Each feature file starts with an H1 title and one paragraph describing the user-visible
behavior. It then uses exactly four H2 sections in this order.

1. `Sub-features` lists short IDs with one line for each behavior.
2. `How to get to it (user POV)` lists every user entry point.
3. `Driving it with verify-cos` starts with `Preconditions:` and uses labeled bullets that
   pair each user action with an exact command and observable result.
4. `Gotchas` lists traps that can waste or invalidate a verification run.

Keep implementation details out of the map. Name only user paths, flags, required state,
commands, and observable proof.

## Features

- [Dry run](./dry-run.md) covers `--dry-run` writing nothing.
- [Fresh install](./fresh-install.md) covers a first install into an empty home.
- [Reinstall](./reinstall.md) covers a second run that creates nothing.
- [Existing files](./existing-files.md) covers leaving user files byte-identical.
- [Pstack enable](./pstack-enable.md) covers the repo plugin flag that the installer does
  not copy into the install root.
