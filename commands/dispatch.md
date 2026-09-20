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

If you cannot name an owner, a done-when, an out-of-scope, and a status location, you do not
write the file. Ask at most one question, then stop.

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

2. **Parse the request.** You need four facts before writing anything. Pull them from
   `$ARGUMENTS` and recent conversation. Missing facts become **one** question, then stop:

   | Field | What good looks like |
   | --- | --- |
   | `goal` | An id that exists in `goals.yaml`. Unaligned work is allowed only if {{NAME}} says so. |
   | `owner` | A human in `contacts/` **or** a named agent role: `explore`, `implement`, `review`. |
   | `done_when` | Observable outcome. "Look into X" is not done-when. "PR open with tests green" is. |
   | `out_of_scope` | At least one concrete exclusion. Empty out-of-scope is a defect. |
   | `status_location` | Where the owner writes progress. Default: this assignment file, plus a `my-tasks.yaml` id. |

3. **Pick the owner using this rule, and say which you chose:**
   - `explore` — read-only research. May write only to `status_location`. No code edits, no
     sends, no merges.
   - `implement` — may edit code on a branch. No merge, no send, no new repos, no scope beyond
     the file.
   - `review` — read a diff, write findings to `status_location`. No approve/merge without
     {{NAME}}.
   - a **human** — name them as in `contacts/`. If they have no contact file, create one from
     the template at `tier: cold` only after listing them as a new person and getting a yes.

   Never invent a fourth agent role. Never assign "the model" or "whoever is free".

4. **Check collisions.** If an open dispatch already covers this request (same goal, overlapping
   done-when), show it and recommend amending that file instead of writing a second. Wait.

5. **Present the assignment** before writing:

   ```
   ## Dispatch — <short title>

   Goal:     <id> (<priority>)
   Owner:    <human name | explore | implement | review>
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
   GitHub: <not requested | unavailable | READY TO SEND draft below>

   Open dispatches: <N>
   ```

10. **`status` / `stale`.** Do not write. List each matching file: title, owner, goal, age in
    days, last status line. At most ten rows. Recommend one next action: nudge, drop, or
    re-assign.

## Guardrails

- Never send, comment, open, merge, or close anything without the approval protocol.
- Never expand scope in the assignment after the operator approved it. A change of scope is a
  new yes.
- Never assign work that conflicts with a `hard: true` protected block as if it were due today.
- Agent owners do not get to create repos, dump vendor trees, or stand up a hosted service.
- If the request is "build a dashboard" and no goal supports it, mark it unaligned and say so
  before writing.
- The owner line is a single noun. "explore + implement" is two dispatches, not one.
