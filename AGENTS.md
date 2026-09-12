# Contributing

This file is for people (and agents) working **on** the repo. It is not loaded by the product.

`CLAUDE.md` at the root is the product: the OS that gets installed into a user's
`~/.claude/chief-of-staff/`. Do not put contributor instructions in it, and do not put product
behavior here. If you are ever unsure which file something belongs in, ask: *does the end user's
Chief of Staff need to know this to do its job?* If yes, `CLAUDE.md`. If no, here.

## Layout

```
CLAUDE.md          the OS — identity, voice, constraints, modes, MCP inventory
goals.yaml         prioritization truth (shipped as a worked example)
my-tasks.yaml      open commitments (worked example)
schedules.yaml     rhythms and protected time (worked example)
commands/*.md      slash-command playbooks, one per command
contacts/          CRM: README (schema), _template.md, one worked example
core/paths.py      the path contract; nothing else may build paths
docs/              mcp-servers.md (setup), roadmap.md (what is deliberately absent)
install.sh         the installer
tests/             shell tests for the installer
```

## Ground rules

1. **Write original content.** Do not copy files, prose, or structure verbatim from other
   chief-of-staff or agent-OS projects. Borrow ideas, write your own words.
2. **No secrets, ever.** No tokens, keys, OAuth JSON, or real email addresses in any file or any
   commit. Example addresses use `example.com` / `.example`.
3. **The installer is non-destructive.** Any new write must go through `copy_if_missing`, or
   come with an argument for why it is generated rather than authored. Deleting, overwriting, or
   appending to a user file is a defect.
4. **The installer is idempotent.** After the first run, a second run creates nothing and exits
   0. `tests/install_test.sh` enforces this; do not weaken the assertion.
5. **Every placeholder must be substituted.** If you add `{{SOMETHING}}` to a shipped file, add
   it to `substitute_placeholders` in `install.sh` in the same commit. The installer warns about
   leftovers, and the test fails on them.
6. **One path contract.** New paths go in `core/paths.py` as static methods and flow into
   `paths.json`. Never hardcode `~/.claude` anywhere else.
7. **Canonicalize before you record a path.** `install.sh` resolves `HOME`, `CLAUDE_HOME`, and
   the install root once, up front, and `core/paths.py` resolves the same way. Anything written
   into a file — a substituted `{{COS_HOME}}`, the memory import line, `paths.json` — must come
   from the resolved form. This is not cosmetic: on macOS `/tmp` is a symlink to `/private/tmp`
   and `$TMPDIR` sits under `/var` -> `/private/var`, so an unresolved path and a resolved one
   name the same directory while comparing unequal. Shell code uses the `canonicalize` helper
   (`pwd -P` on the deepest existing ancestor), never `realpath(1)`, which older macOS lacks.

## Writing a command playbook

Every file in `commands/` follows the same shape, in this order:

1. **YAML frontmatter** — `description` (one line, imperative) and `argument-hint`.
2. **`## Description`** — what it does, what it writes, and explicitly what it never does.
3. **`## Arguments`** — a table of `$ARGUMENTS` values and their behavior. Say what empty means.
4. **`## Instructions`** — numbered, imperative, each step a discrete action. Include the exact
   output shape in a fenced block; agents match format far better than they match prose.
5. **`## Guardrails`** — the failure modes specific to this command. Always restate the approval
   rule if the command can produce something sendable.

Other conventions:

- Reference the OS by section (`CLAUDE.md §8`) rather than restating rules. One source of truth.
- Name the degraded behavior for every tool the command needs. "If the calendar MCP is
  unavailable, print X and continue" is a requirement, not a nicety.
- Prefer a hard number over a judgment call: "at most three overdue contacts", not "a few".
- If a step can send, transmit, or publish, it ends in the approval protocol from CLAUDE.md §4.

## Style

**Markdown** — sentence case headings, tables for enumerable facts, prose for reasoning. Keep
lines under about 100 characters. No emoji.

**YAML** — two-space indent, quoted dates, `null` rather than an empty value, a comment block at
the top of every file explaining the schema. Comments must survive agent edits, so keep them
above the key they describe rather than trailing it.

**Shell** — bash with `set -euo pipefail`. Quote every expansion. No `sed -i` (BSD and GNU
disagree); write to a temp file and `mv`. Assume bash 3.2 so macOS works out of the box.

**Python** — standard library only. Prefer a class with static methods over a pile of
module-level functions: `Paths.goals(root)` reads better than `get_goals_path(root)` and keeps
the contract discoverable in one place. Type hints on public methods. No runtime dependencies —
this must work on a fresh machine with nothing installed.

## Testing

```bash
./tests/install_test.sh          # fresh install, re-install, non-destructiveness, placeholders
./install.sh --dry-run           # eyeball what a real run would do
python3 core/paths.py --json     # inspect the path contract
shellcheck install.sh tests/*.sh # if you have it
```

`tests/install_test.sh` runs everything inside a temporary `HOME` and touches nothing of yours.
It asserts:

- a fresh install creates the expected tree
- a second run creates nothing and leaves every file byte-identical
- a pre-existing user file is never modified
- no `{{PLACEHOLDER}}` survives into an installed file
- `--dry-run` writes nothing at all
- a symlinked install root resolves consistently across the OS file, the import line, and
  `paths.json`, and stays idempotent when re-run through the symlink

Add a case to it for anything you change in `install.sh`.

## Pull requests

- One concern per PR. An installer change and a new command are two PRs.
- Say how you tested it. "Ran the install test" is enough if that is true.
- If you changed a shipped YAML schema, update the comment block at the top of the file and the
  reader in the relevant command playbook in the same change.
- Do not commit anything from `~/.claude`. If you accidentally installed into your real home
  while testing, that is what `--root` exists to prevent next time.
