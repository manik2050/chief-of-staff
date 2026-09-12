# Roadmap — what is deliberately not here yet

This kit is a bootable Chief of Staff, not a finished platform. What ships today is the part
that earns its keep on day one: an OS file, four command playbooks, three state files, a
markdown CRM, and an installer that will not clobber your home directory.

The hardening below is planned. It is listed here so nobody has to guess whether an absence is
an oversight or a decision.

## In this release

- `CLAUDE.md` as the OS: identity, voice, hard constraints, modes, MCP inventory
- `goals.yaml` as prioritization truth, with `my-tasks.yaml` and `schedules.yaml` alongside it
- `/gm`, `/triage`, `/my-tasks`, `/enrich`
- `contacts/` as a dated, append-only markdown CRM
- `core/paths.py` — a single path contract, plus a generated `paths.json`
- `install.sh` — idempotent, non-destructive, placeholder substitution at install time

## Later

**PARA vault.** State currently lives as a flat set of files under the install root. A
Projects / Areas / Resources / Archive vault gives commands a place to put research, meeting
notes, and long-lived reference material without every command inventing its own layout.
`core/paths.py` already reserves `vault/` for this, so nothing will need to move.

**Python MCP servers.** Some things the OS wants — cadence computation across the whole CRM,
capacity math against the calendar, task staleness sweeps — are deterministic and should not be
done by a language model one file at a time. Those become local MCP servers that expose a few
typed tools. `paths.json` exists so a server written later reads the same contract as the
commands written today, and `mcp/` is reserved for them.

**`SKILL.md` packaging.** Commands are markdown playbooks executed by the agent. As they grow,
the reusable parts (drafting in the operator's voice, tiering, cadence math) should be extracted
into skills that several commands share, rather than being restated in each playbook. `skills/`
is reserved.

**CI and lifecycle gates.** The checks that keep a kit like this honest:
- schema validation for `goals.yaml`, `my-tasks.yaml`, `schedules.yaml` and contact frontmatter
- a lint that fails if any command playbook omits Description, Arguments, or Instructions
- a secret scan over the whole tree
- an installer test matrix across macOS and Linux: fresh install, re-install, install over a
  conflicting `~/.claude`, and install through a symlinked root
- a check that every `{{PLACEHOLDER}}` in the repo is one the installer actually substitutes

`tests/install_test.sh` is the first of these. The rest follow once the file formats stop moving.

## Deliberately out of scope

- **Autonomous sending.** The approval protocol is the product. An "auto-send trusted senders"
  mode is not on this list and is not coming.
- **A hosted service.** Everything is files on your machine. If it cannot be read with `cat` and
  fixed with an editor, it does not belong here.
- **A second source of truth.** `goals.yaml` decides priority. Any feature that introduces a
  competing ranking gets rejected on that basis alone.
