# Cursor Projects vs this Chief of Staff

This kit is an **operating system for one operator**. A Cursor Project is an **orchestration runtime** that can fan work out to multiple agents. They fit together; they are not the same thing.

If you open this repository in Cursor, the CoS persona loads (see `.cursor/rules/chief-of-staff.mdc`). If you also run a Cursor Project, that Project is a customer of `/dispatch`, not a replacement for `CLAUDE.md`.

## Two jobs

| | Cursor Project coordinator | Chief of Staff persona |
| --- | --- | --- |
| Job | Assign work to workers; workers do not expand scope | Hold the board so the operator does not have to |
| Who acts | Coordinator plus named sub-agents (explore, implement, review, …) | One persona, switching **modes** (`/gm`, `/triage`, `/dispatch`, …) |
| Memory | Project store: `notes.md`, `docs/`, `internal/` | Install root: `goals.yaml`, `my-tasks.yaml`, `contacts/`, `work-log/` |
| Hands | GitHub, repo tools, whatever MCP the Project connected | Gmail + Calendar required; Slack / Notion / Linear / GitHub optional |
| Writes that leave the machine | Human approval for pushes, PRs, external posts | Approval protocol in `CLAUDE.md` §4 for send / RSVP / invite / archive |
| Ranking | The assignment you were given | `goals.yaml` only |

Do not collapse the two. A coordinator that starts sending email has left its job. A CoS that starts inventing extra repos has left its job.

## Where a file lives

| Need | Put it here | Not here |
| --- | --- | --- |
| What matters this quarter | `goals.yaml` | A Project `notes.md` bullet |
| An open commitment with a next action | `my-tasks.yaml` | A chat transcript |
| A relationship | `contacts/<slug>.md` | A CRM SaaS |
| An assignment to a human or an agent role | `work-log/YYYY-MM-DD-<slug>.md` | A verbal "can you look at this" |
| A morning briefing archive | `briefings/YYYY-MM-DD.md` | Slack |
| Contributor conventions for this repo | `AGENTS.md` | `CLAUDE.md` |
| Cross-agent status for a Cursor Project | that Project's `notes.md` | `goals.yaml` |

`notes.md` in a Project is the coordinator's scratch and status board. `my-tasks.yaml` is the operator's commitment ledger. When `/dispatch` hands work to a Project worker, the assignment file names **both**: the worker writes status to the location in the assignment (`status_location`), and the CoS mirrors the open loop in `/gm`.

## How to run this as a Cursor Project

1. Clone this repo and open it in Cursor. The project rule `@`'s `CLAUDE.md` and lists the commands.
2. Run `./install.sh` so placeholders fill and playbooks land in `~/.cursor/commands/` as well as `~/.claude/commands/`.
3. Copy `.cursor/mcp.json.example` to `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (this workspace). Fill in the calendar credentials path. Authenticate the Gmail and Calendar servers — see [`mcp-servers.md`](mcp-servers.md). Never commit the filled file.
4. Reload Cursor so project-scoped pstack from `.cursor/settings.json` is live. Run `/setup-pstack` once on the machine to pick models. See [`pstack.md`](pstack.md).
5. Rewrite `goals.yaml`. The shipped goals are a generic TPM operator, not yours.
6. Type `/gm`. If slash commands are not wired yet, send the message `/gm` and the rule tells the agent to execute `commands/gm.md`.

A Cursor Project around this repo is optional. It is useful when you want a coordinator to fan `/dispatch` work to isolated agents. Those agents execute through pstack when the plugin is on (`.cursor/settings.json`). The CoS still ranks that work against `goals.yaml` and still will not send without a yes.

## `/dispatch` is the bridge

`/dispatch` writes a file, not a ticket by default:

- **Owner** is either a human engineer (name as in `contacts/`) or a named agent role: `explore`, `implement`, `review`.
- **Tier** is execution effort, not permission: `explore` → `cost`, `implement` → `balanced`,
  `review` → `intelligence`. Security, auth, payments, production, destructive changes, and
  external sends are always `intelligence`.
- **Approval fields** record future gates. Send, publish, merge, production deploy, financial
  transaction, and deletion require a fresh yes immediately before execution.
- **Done-when**, **out-of-scope**, and **status location** are mandatory. An assignment without those is a vibe, and the command refuses to write it.
- GitHub issues / PRs are optional follow-on writes. They use the same approval protocol as email. If GitHub MCP is missing, the assignment stays a file and the command says so in one line.

The Project coordinator may *be* the `implement` or `review` owner. It does not get to skip `out-of-scope` or to merge, send, or publish without the operator.

The runtime maps tiers to models **and** owners to pstack playbooks. Mapping:
[`docs/pstack.md`](pstack.md). A cost-tier `explore` worker runs Investigation; it should
use a cheap model from `/setup-pstack` rather than inheriting the coordinator's model.
Cap retries at two; retry a transient failure once at the same tier, escalate a failed result,
and stop on authentication, entitlement, invalid-model, cancellation, or approval errors.
No live Jev service is required for this deterministic mapping. pstack missing is not a
routing failure: print "pstack unavailable" and keep the owner and tier.

## What not to do

- Do not treat a Cursor Project store as a second `goals.yaml`.
- Do not auto-send, and do not build a hosted CoS service. Files on disk are the product.
- Do not dump an unrelated app into this repo because a Project worker had a blank canvas.
