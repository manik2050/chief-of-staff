---
description: Assign a piece of work to a human engineer or a named agent role.
argument-hint: "[goal-id] [work request] | 'status' | 'stale' | an assignment slug"
---

# /dispatch — Assign work

## Description

Turn a work request into a file that a human engineer or a named agent role can execute without
guessing. This is how the Chief of Staff coordinates people and agents: **one assignment, one
owner, written down**.

It writes one file under `work-log/`. It may append a matching task to `my-tasks.yaml`. It
**never sends**, never opens a GitHub issue or PR, and never merges, unless {{NAME}} approves
that specific write in a later turn using CLAUDE.md §4.

If you cannot name an owner, a tier, a done-when, an out-of-scope, and a status location, you
do not write the file. Ask at most one question, then stop.

## Arguments

`$ARGUMENTS` is optional.

| Value | Behavior |
| --- | --- |
| _(empty)_ | Ask for the goal id and the request in one question, then stop |
| `<goal-id> <request>` | Draft the assignment against that goal |
| `status` | List open and in-progress dispatches only — read-only |
| `stale` | Open dispatches with no status update in 3+ days |
| an assignment slug (`ship-readme`) | Show that file and whether it still matches the goal |

## Instructions

1. **Load** `paths.json`, `goals.yaml`, `my-tasks.yaml`, the file list of `work-log/`, and
   `contacts/`. If `goals.yaml` is missing, stop — you cannot assign work you cannot rank.

2. **Parse the request.** You need these facts before writing anything. Pull them from
   `$ARGUMENTS` and recent conversation. Missing facts become **one** question, then stop:

   | Field | What good looks like |
   | --- | --- |
   | `goal` | An id that exists in `goals.yaml`. Unaligned work is allowed only if {{NAME}} says so. |
   | `owner` | A human in `contacts/` **or** a named agent role: `explore`, `implement`, `review`. |
   | `tier` | `cost`, `balanced`, or `intelligence`, selected by step 3. |
   | `execution` | A pstack playbook name from the table in step 3, or `null`. |
   | `approval_required` | `true` only when execution has an external or irreversible side effect. |
   | `approval_reasons` | Concrete gated actions, or `[]`. |
   | `done_when` | Observable outcome. "Look into X" is not done-when. "PR open with tests green" is. |
   | `out_of_scope` | At least one concrete exclusion. Empty out-of-scope is a defect. |
   | `status_location` | Where the owner writes progress. Default: this assignment file, plus a `my-tasks.yaml` id. |

3. **Pick the owner, tier, and execution using this deterministic rule, and say which you
   chose:**
   - `explore` — read-only research. May write only to `status_location`. No code edits, no
     sends, no merges. **Tier: `cost`.** **Execution: `investigation`.**
   - `implement` — may edit code on a branch. No merge, no send, no new repos, no scope beyond
     the file. **Tier: `balanced`.** **Execution: `feature`.** Use `refactoring` when the
     request is shape-only, or `authoring-a-skill` when it is SKILL.md packaging.
   - `review` — read a diff, write findings to `status_location`. No approve/merge without
     {{NAME}}. **Tier: `intelligence`.** **Execution: `interrogate`.**
   - a **human** — name them as in `contacts/`. If they have no contact file, create one from
     the template at `tier: cold` only after listing them as a new person and getting a yes.
     Use `balanced` unless the request is clearly short/read-only (`cost`) or high-risk
     (`intelligence`). **Execution: `null`.**

   Raise any owner to **`intelligence`** when the request touches security, authentication,
   secrets, payments, production, destructive changes, or an external send. A high-risk
   request never routes down.

   `execution` is the pstack playbook the agent owner runs (`docs/pstack.md`). Read
   `.cursor/settings.json`. If `plugins.pstack.enabled` is not true, set `execution` to
   `null` and print "pstack unavailable — owner runs without a named playbook". The
   assignment is still valid. Never invent a playbook name that is not in the list above.

   Set `approval_required: true` and list `approval_reasons` for any send, publish, merge,
   production deploy, financial transaction, or data deletion. This records a future gate; it
   is not approval. `/dispatch` still asks before writing every assignment, and the owner must
   ask again immediately before the gated action under CLAUDE.md §4.

   Never invent a fourth agent role. Never assign "the model" or "whoever is free".

4. **Check collisions.** If an open dispatch already covers this request (same goal, overlapping
   done-when), show it and recommend amending that file instead of writing a second. Wait.

5. **Present the assignment** before writing:

   ```
   ## Dispatch — <short title>

   Goal:     <id> (<priority>)
   Owner:    <human name | explore | implement | review>
   Tier:     <cost | balanced | intelligence>
   Execution: <investigation | feature | refactoring | authoring-a-skill | interrogate | none>
   Approval: <not required | required: reason, reason>
   Done when:
     - <observable>
   Out of scope:
     - <exclusion>
   Status:   work-log/<YYYY-MM-DD>-<slug>.md  and  my-tasks.yaml#<t-NNN>

   Write this file? (yes / change owner / change scope)
   ```

   Then stop. Do not write before {{NAME}} says yes to **this** assignment. Approving a plan
   earlier in the conversation is not yes.

6. **On yes, write** `work-log/YYYY-MM-DD-<slug>.md` using `_template.md`. Fill every frontmatter
   field. `id` is `d-YYYYMMDD-<slug>`. `status` is `open`. `created` is today in {{TIMEZONE}}.
   Record `tier`, `execution`, `approval_required`, and `approval_reasons` exactly as
   presented. Write `execution: null` when the owner is a human or pstack is unavailable.
   Body sections: Request, Done when, Out of scope, Owner, Status. No secrets. No employer
   names, product metrics, or internal architecture.

7. **Ledger the loop.** Append a task to `my-tasks.yaml`:
   - `id` from `next_id`, then increment
   - `goal` from step 2
   - `status: waiting` / `waiting_on` set to the owner (role name or person)
   - `next_action`: "Read work-log/<file> and update its Status section"
   - `source: dispatch`
   - `notes`: the assignment id

   Point the assignment's `status_location` at both the file and that task id.

8. **GitHub is optional and never silent.** If a GitHub MCP is connected and {{NAME}} asked for
   an issue or PR, draft the exact title and body and end with the approval block from
   CLAUDE.md §4. Do not call a create/merge tool in the same turn. If GitHub is unavailable,
   print "GitHub unavailable — assignment is file-only" and continue. File-only is success.

9. **Output after writing:**

   ```
   Wrote: work-log/<file>
   Task:  <t-NNN>  waiting on <owner>
   Execution: <playbook | pstack unavailable>
   GitHub: <not requested | unavailable | READY TO SEND draft below>

   Open dispatches: <N>
   ```

10. **`status` / `stale`.** Do not write. List each matching file: title, owner, goal, age in
    days, last status line. At most ten rows. Recommend one next action: nudge, drop, or
    re-assign.

## Guardrails

- Never send, comment, open, merge, or close anything without the approval protocol.
- A tier selects execution effort; it never grants permission. `intelligence` is not approval.
- A named pstack playbook does not grant permission either. CLAUDE.md §4 still wins if
  poteto-mode would send, merge, or publish. See `docs/pstack.md`.
- Bypass or missing routing tools may choose `balanced`, but may not remove a risk floor or
  approval reason.
- Missing pstack may set `execution` to `null`. It may not drop the owner, the tier, or an
  approval reason.
- Never expand scope in the assignment after the operator approved it. A change of scope is a
  new yes.
- Never assign work that conflicts with a `hard: true` protected block as if it were due today.
- Agent owners do not get to create repos, dump vendor trees, or stand up a hosted service.
- If the request is "build a dashboard" and no goal supports it, mark it unaligned and say so
  before writing.
- The owner line is a single noun. "explore + implement" is two dispatches, not one.
