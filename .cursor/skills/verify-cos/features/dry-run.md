# Dry run

`--dry-run` shows what a real install would create and writes nothing under the target home.

## Sub-features

- `dry-mode` prints the dry-run mode line.
- `dry-empty` leaves the throwaway HOME with zero entries.

## How to get to it (user POV)

- Run `./install.sh --dry-run --yes` with identity flags set.
- Run `./.cursor/skills/verify-cos/verify-cos.sh drive dry-run`.

## Driving it with verify-cos

Preconditions:

- `verify-cos.sh doctor` printed `pstack=enabled`.
- No files exist under the throwaway HOME yet.

- **Run dry-run.** Run `./.cursor/skills/verify-cos/verify-cos.sh drive dry-run`. Exit code
  `0`. The log contains `mode         : dry run (nothing will be written)`.
- **Confirm empty home.** Read `artifacts/<run-id>/dry-run.home-count`. It is `empty`.
  `find` on the throwaway HOME listed in `homes.txt` returns no entries.
- **Proof.** Keep `dry-run.log` and `dry-run.home-count`. The log lists `would create` or
  `would mkdir` paths and the home still has no files.

## Gotchas

- Running `--dry-run` against a real `$HOME` is out of bounds. Refuse and use the helper.
- A zero exit code with a populated home is a fail. Count files. Do not trust the banner.
