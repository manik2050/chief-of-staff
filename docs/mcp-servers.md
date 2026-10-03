# MCP servers

The Chief of Staff is only as good as what it can see. **Google Calendar is required.**
**Gmail is required when this OS owns email** (`inbound.email.owner: cos` in
`schedules.yaml`). If another bot already triages Gmail, set that owner to `external` and
`/gm` will skip the inbox on purpose.

X is optional and billed. Do not connect it for a daily scan. CLAUDE.md §11 is the rule:
named post or named contact, never a briefing sweep.

Everything else is optional. The OS is written to degrade gracefully: a missing server
produces a one-line note in the output, never a silent gap. See CLAUDE.md §11 for the
per-server fallbacks.

## The minimum set

| Server | Why it is required | Scopes it needs | Used by |
| --- | --- | --- | --- |
| **Google Calendar** | You cannot propose a slot you have not verified. This is a hard constraint, not a nicety. | read events (freebusy plus event details); create events only if you want the agent to book. | `/gm`, `/my-tasks`, scheduling mode |
| **Gmail** | Only when `inbound.email.owner` is `cos`. Reading the inbox is what makes CoS triage possible. Drafting replies is the main output. Skip entirely when another bot owns mail. | read messages and threads; create drafts. Send scope is optional — see below. | `/gm` (owned mail), `/triage inbox`, `/enrich` (owned mail) |

### A note on send scope

The OS never sends without explicit approval (CLAUDE.md §4). If you want that guarantee enforced
by something stronger than instructions, grant **draft-only** scope on Gmail and
**read-only** on Calendar. The agent will draft into your Gmail drafts folder and you press send.
This costs one click per message and removes an entire class of failure. Start here; widen later
if you decide you want to.

## Useful additions

| Server | Adds | Without it |
| --- | --- | --- |
| Slack | DM and channel triage; catches the Tier 1 items that never reach email | Print "Chat unavailable" in one line |
| Notion / Google Docs | Meeting notes and project pages feed enrichment | `/enrich` uses only mail and calendar |
| Web search / fetch | Contact enrichment: role changes, funding, news | `/enrich` reports "no external check" |
| Task tracker (Linear, Jira, Asana) | Two-way sync with `my-tasks.yaml` | `my-tasks.yaml` stands alone, which is fine |
| GitHub | Optional follow-on for `/dispatch` (draft an issue or PR) | Assignment stays a file; `/dispatch` prints "GitHub unavailable" |
| X | A named post or a named `contacts/` person. Credits are spent per lookup. | Do not scan. `/gm` says nothing about X. |
| Filesystem | Explicit access to the install root if your client sandboxes it | Usually built in |

## Installing

Both Claude Code and Cursor read MCP server definitions from JSON. The shape is the same; only
the file location differs. This kit pins two maintained packages so you are not left with
placeholders:

| Server | npm package | Why this one |
| --- | --- | --- |
| Gmail | [`@klodr/gmail-mcp`](https://www.npmjs.com/package/@klodr/gmail-mcp) | Scope-gated tools. `gmail.readonly,gmail.compose` exposes read + drafts and **hides send**. |
| Google Calendar | [`@cocal/google-calendar-mcp`](https://www.npmjs.com/package/@cocal/google-calendar-mcp) | Active `nspady/google-calendar-mcp` publish. `list-events` / `get-freebusy` are the reads `/gm` needs. |

A ready-to-copy config lives at [`.cursor/mcp.json.example`](../.cursor/mcp.json.example) in the
repo (also installed to `docs/mcp.json.example` under the install root).

**Auth, once, with the minimum scopes.** Tokens stay outside the repo.

```bash
mkdir -p ~/.config/cos

# Gmail: read the inbox, create drafts, cannot send. That is the product guarantee
# enforced below the model. Widen to gmail.send later only if you decide you want to.
npx -y @klodr/gmail-mcp auth --scopes=gmail.readonly,gmail.compose

# Calendar: desktop OAuth client JSON lives under ~/.config/cos/, never in this repo.
# Point GOOGLE_OAUTH_CREDENTIALS at the absolute path of that JSON, then:
npx -y @cocal/google-calendar-mcp auth
```

`@klodr/gmail-mcp` writes tokens to `~/.gmail-mcp/credentials.json` (mode 0600). The calendar
server needs `GOOGLE_OAUTH_CREDENTIALS` set to an **absolute** path — tildes are not expanded.

**Claude Code**

```bash
claude mcp add gmail --scope user -- npx -y @klodr/gmail-mcp
claude mcp add google-calendar --scope user -- npx -y @cocal/google-calendar-mcp

claude mcp list
```

Pass the calendar credentials as an env var on that `mcp add` (or in `~/.claude.json`), matching
the Cursor file below.

**Cursor** — copy the example to `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (this
workspace), then replace the calendar credentials path with yours:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "npx",
      "args": ["-y", "@klodr/gmail-mcp"]
    },
    "google-calendar": {
      "command": "npx",
      "args": ["-y", "@cocal/google-calendar-mcp"],
      "env": {
        "GOOGLE_OAUTH_CREDENTIALS": "/Users/you/.config/cos/gcp-oauth.keys.json"
      }
    }
  }
}
```

Do not commit a filled `.cursor/mcp.json`. The example file is the one that belongs in git.

If you swap either package, keep the scope rule: Gmail draft-only until you choose otherwise,
and calendar read (plus free/busy) before any create-event scope.

## Credentials

- **Never** put a token, client secret, or OAuth JSON inside `~/.claude/chief-of-staff/` or any
  checkout of this repo. Both are places you will eventually copy, sync, or share.
- Keep credentials in a dedicated directory (`~/.config/cos/` works) and point at them with
  environment variables, as in the example above.
- `.gitignore` in this repo blocks the obvious filenames, but the real protection is not putting
  them here in the first place.
- Prefer a dedicated OAuth client for this tooling so you can revoke it independently.

## Verifying it works

1. `claude mcp list` (or Cursor's MCP settings) shows Calendar connected, and Gmail
   connected if this OS owns email.
2. Ask: *"What is on my calendar tomorrow?"* — you should get real events, not an apology.
3. Ask: *"How many unread emails arrived since yesterday?"* — a count, not a guess. Skip this
   check if `inbound.email.owner` is `external`.
4. Run `/gm`. The Agenda section should have content. The inbox line should either list
   mail this OS owns, or print `Inbox: owned by <handler> — skipped`.

If step 4 prints "Calendar unavailable" or "Inbox unavailable", the OS is working correctly and
the server is not connected — that message is the designed failure mode. If it prints
`Inbox: owned by Grok bot — skipped`, that is also designed: do not connect Gmail just to
double-triage.

## What the agent may and may not do with these

Calendar, Gmail, Slack, and filesystem reads are called freely when this OS owns the
channel. X reads spend credits — do not call X from `/gm` or default `/triage`. Write tools
— `send`, `reply`, `create_event`, `post_message` — require the approval protocol in
CLAUDE.md §4 every single time. Approval of a plan is never approval of a specific message.
If you ever see a message go out without you having typed an explicit yes, that is a bug in
the OS, not a feature of the model.
