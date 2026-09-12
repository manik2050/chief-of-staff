---
description: Reconcile open commitments against goals and the calendar, then re-rank.
argument-hint: "[optional: 'today' | 'week' | a goal id | 'stale' | 'add <task text>']"
---

# /my-tasks — Planning and Reconciliation

## Description

Bring `my-tasks.yaml` back into alignment with `goals.yaml` and reality. This command re-ranks,
surfaces staleness, forces decisions on items that have been quietly rotting, and tells {{NAME}}
what the week can actually hold.

It writes to `my-tasks.yaml`. It never sends anything and never books time without approval.

## Arguments

`$ARGUMENTS` is optional.

| Value | Behavior |
| --- | --- |
| _(empty)_ | Full reconciliation |
| `today` | Only what is due today, overdue, or already scheduled today |
| `week` | The next seven days, plus a capacity check |
| a goal id (`series-a`) | Only tasks for that goal, plus whether the goal is on track |
| `stale` | Only the staleness report from step 5 |
| `add <text>` | Capture a single task, ask at most one clarifying question, then stop |

## Instructions

1. **Load** `my-tasks.yaml`, `goals.yaml`, and `schedules.yaml`. If `my-tasks.yaml` is malformed,
   quote the offending line and stop — do not rewrite a file you cannot parse.

2. **Validate every task.** Report and fix in place:
   - `goal` that does not exist in `goals.yaml` → ask which goal, or mark `unaligned`
   - `status: waiting` with no `waiting_on` → ask who
   - missing or vague `next_action` ("follow up", "think about") → rewrite it as a physical
     action, or flag the task as a decision rather than a task
   - `done` older than `archive_after_days` → propose moving to `my-tasks-archive.yaml`

3. **Re-rank.** Order by: goal priority (P0 → P3), then hard deadline, then whether the task
   unblocks someone else, then age. Tier from triage is an input, not the answer — a Tier 1 item
   serving a P3 goal ranks below a Tier 2 item serving a P0 goal.

4. **Capacity check.** Read the calendar for the window. Compute unscheduled working hours after
   subtracting meetings and `hard: true` protected blocks. Compare against the number of open
   `next` and `in-progress` tasks, assuming 45 minutes each unless the task says otherwise. If
   the open set does not fit, say the overage as a number of hours and name what to drop — do
   not soften it.

5. **Staleness report:**
   - `waiting` untouched 5+ days → propose a nudge (draft it only if asked)
   - `next` untouched 14+ days → propose dropping it and say what it was for
   - Tier 2 aged 14+ days → force the call: promote to Tier 1 or drop
   - `blocked` where the blocker is {{NAME}} → list first, name the decision, and offer to
     schedule 25 minutes to make it

6. **Goal coverage.** For each active goal in priority order, count open tasks. Any P0 or P1 goal
   with zero open tasks is the most important thing in this output — a goal with no tasks is not
   being worked on, whatever the plan says. State it plainly.

7. **Output:**

   ```
   ## Tasks — <N> open across <M> goals

   **Capacity:** <X>h open vs <Y>h of work. <"Fits." | "Over by <Z>h.">

   ### Do next (in order)
   1. <title> — [goal, P0] — <next_action> — due <date>
   ...

   ### Waiting on others
   - <person>, <N>d — <title> — Recommend: nudge

   ### Decisions only you can make
   - <title> — the call is: <the actual question>

   ### Drop candidates
   - <title> — untouched <N>d, serves <goal>

   ### Goal coverage
   - series-a (P0): 3 open
   - retention (P0): 0 open  ← no one is working on this

   Changes written: <list of task ids and what changed>
   ```

8. **Write back** to `my-tasks.yaml`: re-ranked order, corrected fields, updated `touched` dates
   for anything you changed, and an incremented `next_id` for anything you added. Preserve every
   comment in the file. Never drop a task without explicit approval — `status: dropped` with a
   reason in `notes`, never deletion.

9. **Offer one next step**, not five: either scheduling the top item into a free block, or making
   the first decision in the decisions list.

## Guardrails

- Never delete a task. `dropped` is a status.
- Never invent a due date. `null` is an honest answer.
- Never mark something `done` on {{NAME}}'s say-so about a plan — only when the work is reported
  finished.
- If the capacity math is ugly, say the ugly number. A plan that does not fit is the single most
  useful thing this command can find.
