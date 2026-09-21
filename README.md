# Chief of Staff

A personal chief-of-staff OS for [Cursor](https://cursor.com) and
[Claude Code](https://docs.claude.com/en/docs/claude-code). Clone it, run `./install.sh`,
open this repo in Cursor, and type `/gm`.

It is files, not a service. An OS definition, five command playbooks, three state files, a
markdown CRM, and a work-log — all plain text on your machine, all readable with `cat`, all
editable with the editor you already have open.

```
$ ./install.sh
$ cursor .          # or: claude
> /gm
```

---

## What you get

| File | What it does |
| --- | --- |
| `CLAUDE.md` | **The OS.** Identity, voice, hard constraints, modes, MCP inventory. Loaded every session. |
| `goals.yaml` | **Prioritization truth.** Nothing — not urgency, not seniority — outranks it. |
| `my-tasks.yaml` | Open commitments, each tied to a goal, each with a physical next action. |
| `schedules.yaml` | Working hours, protected blocks, recurring commitments, scheduling defaults. |
| `contacts/` | A dated, append-only markdown CRM. One file per person. Tiers drive outreach cadence. |
| `work-log/` | Assignments: owner, done-when, out-of-scope, status location. Written by `/dispatch`. |
| `commands/` | Executable playbooks: `/gm`, `/triage`, `/my-tasks`, `/enrich`, `/dispatch`. |
| `core/paths.py` | One path contract for everything, plus a generated `paths.json`. |
| `install.sh` | Idempotent, non-destructive install into `~/.claude/` and `~/.cursor/commands/`. |

## The commands

**`/gm`** — the morning briefing. One screen: today's agenda, Tier 1 items with a recommended
action each, open dispatches, what is waiting on whom, which relationships are going cold,
where the calendar collides with your protected time. Ends with one question: what do you want
to take first.

**`/triage`** — turns inbound into three tiers, drafts replies for the ones you pick, and
captures every commitment into `my-tasks.yaml` in the same pass.

**`/my-tasks`** — reconciles open work against your goals and your actual free hours. Tells you
the ugly number when the week does not fit, and forces a call on anything quietly rotting.
`/my-tasks status` writes a `templates/weekly-status.md`-shaped briefing.

**`/enrich`** — keeps the CRM true. Logs what happened with whom, surfaces at most three overdue
relationships, and refuses to propose outreach without a specific reason to reach out.

**`/dispatch`** — the multi-agent layer. Takes a goal id and a work request, writes
`work-log/YYYY-MM-DD-<slug>.md` with an owner (a human engineer or `explore` / `implement` /
`review`), an execution tier (`cost` / `balanced` / `intelligence`), explicit approval gates,
done-when, out-of-scope, and where status goes. File-native. GitHub is optional and still needs
a yes.

## It will not send anything without you

This is the load-bearing constraint, stated in CLAUDE.md §4 and repeated in every command:

> Never send anything on the operator's behalf without explicit, in-the-moment approval.

Email, chat, calendar invites, RSVPs, archiving — all of it drafts first, shows you the full
text and the exact recipients, and stops. Approving a plan is never approval of a message. If
you want that enforced below the model as well, grant your Gmail MCP server **draft-only**
scope; see [`docs/mcp-servers.md`](docs/mcp-servers.md).

It also never proposes a meeting slot it has not verified against your live calendar. If it
could not read the calendar, it proposes nothing and says so.

---

## Install

Requires bash and git. Python 3.8+ is optional but recommended (it generates `paths.json`).

```bash
git clone https://github.com/manik2050/chief-of-staff.git
cd chief-of-staff
./install.sh
```

The installer asks for your name, role, company, email, timezone, and working hours, then
substitutes them into the `{{PLACEHOLDER}}` tokens as it copies. Pass them as flags to skip the
prompts:

```bash
./install.sh --name "Ada Lovelace" --role "CEO" --company "Analytical" \
             --timezone "Europe/London" --work-hours "08:30-17:30" --yes
```

Preview without writing anything:

```bash
./install.sh --dry-run
```

### Where things land

```
~/.claude/
├── CLAUDE.md                      # created only if absent; imports the OS below
├── commands/
│   ├── gm.md  triage.md  my-tasks.md  enrich.md  dispatch.md
└── chief-of-staff/                # the install root
    ├── CLAUDE.md                  # the OS
    ├── goals.yaml  my-tasks.yaml  schedules.yaml
    ├── paths.json                 # generated
    ├── contacts/                  # _template.md + a worked example
    ├── work-log/                  # _template.md + README; /dispatch writes here
    ├── briefings/  drafts/        # written by the agent
    ├── templates/weekly-status.md
    ├── core/paths.py
    └── docs/                      # mcp-servers.md, cursor-projects.md, mcp.json.example

~/.cursor/commands/                # same playbooks, for Cursor slash commands
```

Override either location with `--root` and `--claude-home`, or the `COS_HOME` and `CLAUDE_HOME`
environment variables.

### Non-destructive, and idempotent

Every copy goes through one primitive, `copy_if_missing`. If a file already exists it is left
exactly as it is and reported as `exists`. Nothing is overwritten, appended to, or deleted. Run
the installer a hundred times; after the first, it changes nothing and exits 0.

The one exception is `paths.json`, which is generated rather than authored — its contents are a
pure function of the install root, so rewriting it is a no-op.

If you already have a `~/.claude/CLAUDE.md`, the installer will not touch it. It prints the one
line to add:

```
@~/.claude/chief-of-staff/CLAUDE.md
```

Add it yourself, or re-run with `--merge-memory` to have the installer append it.

**To update a file the installer placed:** delete your copy and run `./install.sh` again. It
will never overwrite one for you, precisely because it cannot tell your edits from the default.

---

## First run

1. **Rewrite `goals.yaml`.** This is the whole system. The shipped goals belong to a fictional
   TPM operator (public build, deep work, weekly status) — they make the format obvious and are
   useless to you. Five to seven goals, each with a `why` that names the consequence of failure
   — triage quality comes directly from that field.
2. **Connect Gmail and Google Calendar.** See [`docs/mcp-servers.md`](docs/mcp-servers.md). These
   are the minimum; everything else is optional and degrades cleanly.
3. **Set your protected time** in `schedules.yaml`. If deep work is not in here, it will get
   scheduled over.
4. **Delete the example contact** and add three real ones — the people you most regret losing
   touch with.
5. **Run `/gm`.**

Expect the first week to be a calibration exercise. When a briefing surfaces the wrong thing,
the fix is almost always in `goals.yaml`, not in the prompt.

## Using it in Cursor

This is a Cursor-native kit. Opening the repo is enough for the OS to load; `./install.sh`
also wires user-level slash commands.

1. **Clone and install**

   ```bash
   git clone https://github.com/manik2050/chief-of-staff.git
   cd chief-of-staff
   ./install.sh
   ```

   Playbooks land in `~/.cursor/commands/` and `~/.claude/commands/`. State lands in
   `~/.claude/chief-of-staff/`. Re-running is a no-op.

2. **Open this folder in Cursor.** `.cursor/rules/chief-of-staff.mdc` always-applies and
   `@`'s `CLAUDE.md`. After install, the filled copy at `~/.claude/chief-of-staff/CLAUDE.md`
   wins over the unsubstituted repo file.

3. **Pin Gmail and Calendar.** Copy [`.cursor/mcp.json.example`](.cursor/mcp.json.example) to
   `~/.cursor/mcp.json` (every project) or `.cursor/mcp.json` (just this one). The example
   uses real packages: `@klodr/gmail-mcp` and `@cocal/google-calendar-mcp`. Authenticate with
   draft-only Gmail scopes — [`docs/mcp-servers.md`](docs/mcp-servers.md). Do not commit the
   filled file.

4. **Rewrite `goals.yaml`** in the install root. Then type `/gm`.

   If slash commands are not listed yet, send the message `/gm`. The rule treats that as
   "run `commands/gm.md`". Same for `/triage`, `/my-tasks`, `/enrich`, `/dispatch`.

How a Cursor Project coordinator differs from this CoS persona:
[`docs/cursor-projects.md`](docs/cursor-projects.md).

## Customizing

- **Voice** — CLAUDE.md §3. Rewrite it in your own register; the defaults are terse on purpose.
- **Tiers and cadence** — §8 and §9. The cadence numbers are a starting point, not research.
- **Scheduling defaults** — `schedules.yaml`. 25/50 minute meetings by default, 15 minute
  buffers around anything with a location.
- **New commands** — copy an existing playbook. Every one has Description, Arguments, numbered
  Instructions, and Guardrails, in that order. Keep the shape.

## Roadmap

A PARA vault, local Python MCP servers for the deterministic work, `SKILL.md` packaging, and CI
lifecycle gates are planned but deliberately not in this release.
[`docs/roadmap.md`](docs/roadmap.md) says what is missing and why.

## Contributing

See [`AGENTS.md`](AGENTS.md) — conventions, file layout, and how to run the install test. It is
contributor-facing and separate from `CLAUDE.md`, which is the product.

## License

MIT. See [`LICENSE`](LICENSE).
