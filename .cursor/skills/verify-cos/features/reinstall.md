# Reinstall

A second install into the same home creates nothing and leaves every file byte-identical.

## Sub-features

- `reinstall-zero` reports `0 created`.
- `reinstall-identical` leaves the file list unchanged.

## How to get to it (user POV)

- Run `./install.sh --yes` twice into the same home.
- Run `./.cursor/skills/verify-cos/verify-cos.sh drive reinstall`.

## Driving it with verify-cos

Preconditions:

- A fresh install into the throwaway HOME already succeeded, or the helper will do one first.

- **Re-run.** Run `./.cursor/skills/verify-cos/verify-cos.sh drive reinstall`. Exit code `0`.
- **Read the banner.** `reinstall.log` contains `0 created`.
- **Compare lists.** `reinstall.before` and `reinstall.after` are identical.
- **Proof.** Keep both lists and `reinstall.log`.

## Gotchas

- `paths.json` is rewritten as a pure function of the root. The content must match the first
  run. A timestamp inside it would be a defect.
- Do not delete a user file and treat the recreate as idempotency. Idempotency is a second
  run with the tree still present.
