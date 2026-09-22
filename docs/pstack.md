# pstack — how this kit executes engineering work

[pstack](https://cursor.com/marketplace/cursor/pstack) is the execution engine for code,
reviews, and stacked PRs. It is not the Chief of Staff. `CLAUDE.md` still ranks work against
`goals.yaml` and still will not send, merge, or publish without a yes.

Use pstack when an assignment's owner is `explore`, `implement`, or `review`. Do not use it
to run `/gm` or `/triage`. Those stay CoS modes.

## Enable it

This repository already turns the plugin on for anyone who opens the folder:

```json
{
  "plugins": {
    "pstack": { "enabled": true }
  }
}
```

That file is `.cursor/settings.json`. Reload Cursor after a clone if `/poteto-mode` is missing.

User-scope install also works (`/add-plugin pstack` or the
[marketplace page](https://cursor.com/marketplace/cursor/pstack)). Project scope is the one
this kit commits, so a fresh agent in this repo gets the skills without a personal install.

Then, once per machine, pick models:

```text
/setup-pstack
```

That writes `~/.cursor/rules/pstack-models.mdc`. It is user-level on purpose. Do not commit
model slugs into this repo; entitlements differ. Until you run it, pstack uses its own
defaults.

If `/poteto-mode` still does not resolve, print "pstack unavailable" and keep going. The
assignment is still valid. The owner just has no named playbook.

## First command

For any non-trivial engineering task:

```text
/poteto-mode <the request>
```

`/poteto-mode` picks a playbook, opens a todo list whose first items are that playbook's
steps, and calls the other pstack skills as the steps need them. You do not have to invoke
`/how`, `/architect`, or `/tdd` yourself unless you want that skill on its own.

Sticky: it stays on for the conversation until you opt out.

## How it maps to `/dispatch`

`/dispatch` still picks the owner and the tier. When pstack is enabled it also names one
playbook and writes it to the assignment as `execution`.

| Owner | Tier | `execution` | What the owner runs |
| --- | --- | --- | --- |
| `explore` | `cost` | `investigation` | `/poteto-mode` Investigation. Read-only. Findings go to `status_location`. Use `/how` or `/why` only when the question is how a subsystem works or why it was built that way. |
| `implement` | `balanced` | `feature` | `/poteto-mode` Feature. New or changed behavior. Switch to `refactoring` when the request is shape-only, or `authoring-a-skill` when it is SKILL.md packaging. Run `/architect` first when the change crosses a function boundary. |
| `review` | `intelligence` | `interrogate` | `/interrogate` on the diff. Write findings. Do not approve, merge, or "just fix it". |
| a human | as chosen | `null` | No pstack playbook. They read the assignment file. |

High-risk work still floors at `intelligence`. pstack does not lower that floor.

The owner line remains a single noun. `explore` then `implement` is two dispatches. Do not
stuff a second playbook into one file.

## Standing orders for every agent owner

Paste these into any long pstack run (orchestrate, autonomous run, stacked PRs). They are
the CoS constraints in a form a worker can obey without loading the whole OS.

1. Rank against `goals.yaml`. Unaligned work is allowed only if the assignment says so.
2. The assignment's `done_when` and `out_of_scope` are the scope. Do not add a vault, an MCP
   server, a skill, or a CI gate because it was nearby.
3. CLAUDE.md §4 wins. Draft anything that sends, publishes, or merges; stop; wait for a yes.
4. Open a PR if that is the done-when. Do not merge it. Do not run autopilot-full.
5. Do not create repos, dump vendor trees, or stand up a hosted service.
6. No secrets in files. Example addresses stay on `example.com`.
7. Status appends under `## Status` on the assignment. Do not rewrite the request.
8. Prove it on the real artifact. For this kit that means `./tests/install_test.sh` (and
   `./install.sh --dry-run` when the installer changed). Compiling is not proof.
9. One concern per PR. An installer change and a new command are two PRs.

## How to execute the roadmap

`docs/roadmap.md` lists what is deliberately not in this release. Do not implement those
items because you have pstack. Dispatch them, then let pstack run the named playbook.

Recommended first cut, each as its own `/dispatch public-build ...` (the shipped P0):

| Later item | First owner | `execution` | Why this cut |
| --- | --- | --- | --- |
| PARA vault | `explore` | `investigation` | `core/paths.py` already reserves `vault/`. Confirm the contract and the command writers before anyone creates folders. Follow with `implement` / `feature`. |
| Python MCP servers | `implement` | `feature` | After `/architect` on the tool surface. Servers live under reserved `mcp/` and read `paths.json`. One server per PR. |
| `SKILL.md` packaging | `implement` | `authoring-a-skill` | Extract a shared piece (tiering, cadence, drafting voice) into `skills/` without restating CLAUDE.md. One skill per PR. |
| CI and lifecycle gates | `implement` | `feature` | First cut is the GitHub Action that runs `tests/install_test.sh` on PRs and `main`. Next: schema validation or the playbook-shape lint. Add a case; do not weaken the suite. Use `/tdd` when the check is cheap. |

A standing program that owns the whole Later section is `/poteto-mode` Orchestrate, with the
standing orders above pasted into every spawn. That is the operator's call, not the default.
Default is one dispatch per row. Orchestrate is for when you are stepping away and want the
stack built, not merged.

Do not start with autopilot-full. The operator lands.

## What pstack must not become

- A second `goals.yaml`. Orchestrate boards and decision trails are worker scratch. The
  commitment ledger is `my-tasks.yaml`.
- A send path. Benny-style Slack automations are out of scope here. Approval is the product.
- A reason to copy plugin files into this tree. Enable the plugin; do not vendor it.

## If you are new to pstack

The plugin's own guide is the how-to for playbooks, models, and overnight runs. This file is
only the socket: enable the plugin, map owners to playbooks, keep §4, execute the roadmap as
dispatches. Start at https://cursor.com/marketplace/cursor/pstack.
