---
description: Morning briefing — one screen covering the last 24 hours and the next 24.
argument-hint: "[optional: a date, or 'short', or a focus area like 'public-build']"
---

# /gm — Morning Briefing

## Description

The first command of the day. Read-only synthesis of what happened since yesterday and what
happens today, ranked by `goals.yaml`, ending in exactly one question: what to do first.

This command **never sends anything** and **never creates calendar events**. It may write a
single archive file under `briefings/`.

If it does not fit on one screen, you have not prioritized.

## Arguments

`$ARGUMENTS` is optional.

| Value | Behavior |
| --- | --- |
| _(empty)_ | Full briefing for today |
| `short` | Sections 1, 3, and 7 only — the agenda, Tier 1, and the question |
| a date (`2026-01-09`) | Brief as if it were that morning; look back 24h from that date |
| anything else | Treat as a focus filter: include only items matching that goal or keyword, and say at the top that the briefing is filtered |

## Instructions

1. **Load state.** Read `paths.json`, then `goals.yaml`, `my-tasks.yaml`, `schedules.yaml`, the
   file list of `contacts/`, and the file list of `work-log/`. If any is missing or malformed,
   note it in one line at the end of the briefing and continue with what loaded. Do not attempt
   repairs.

2. **Establish the window.** "Since" is the last briefing in `briefings/`, or 24 hours ago if
   there is none. "Until" is the end of today in {{TIMEZONE}}. State neither in the output; just
   use them.

3. **Read the calendar** for today and tomorrow. Capture: start and end, title, attendees,
   location, and whether it collides with a protected block from `schedules.yaml`. If the
   calendar MCP is unavailable, print the agenda section as "Calendar unavailable — no agenda"
   and continue.

4. **Read the inbox** for the window. Do not read message bodies in bulk; read senders, subjects,
   and threads, then open only the ones that look Tier 1 or Tier 2. If the Gmail MCP is
   unavailable, print "Inbox unavailable" and continue.

5. **Score everything** against `goals.yaml` using the priority model in CLAUDE.md §6 and the
   tiers in §8. Every item you surface must name its goal. Items matching no goal are
   `unaligned` and are counted, not listed.

6. **Check the tasks file.** Flag: anything due today or overdue, anything `waiting` and
   untouched for 5+ days, anything `blocked` where the blocker is {{NAME}} themselves. The last
   category goes first — self-blocked work is the cheapest thing to fix.

7. **Check contact cadence** using CLAUDE.md §9. Compute days since last touch from the most
   recent dated entry inside each contact file. Surface at most three overdue contacts, highest
   tier first, and only with a concrete hook.

8. **Check open dispatches.** List files in `work-log/` whose frontmatter `status` is `open` or
   `in-progress`. Skip `_template.md` and `README.md`. If the directory is missing, print
   "Work-log unavailable" under Loops and continue. For each open dispatch capture: title, owner
   (`owner.name`), goal id, created date, and whether `status_location` has been updated in 3+
   days (stale). At most five rows; if there are more, say the count you suppressed.

9. **Detect collisions.** Any meeting overlapping a `hard: true` protected block, any day over
   `max_meetings_per_day`, any run over `max_consecutive_meetings`, and any recurring commitment
   in `schedules.yaml` that is missing from the live calendar.

10. **Write the briefing** in exactly this shape. Keep every bullet to one line. Omit no section —
   an empty section prints "Nothing."

   ```
   ## Good morning, {{NAME}} — <Weekday, Month D>

   **Today in one line:** <the single thing that determines whether today worked>

   ### Agenda
   - 09:30–09:55  1:1 — Jordan Rivera  [relationships]
   - ...
   Free: <the largest uninterrupted blocks, in order of size>

   ### Tier 1 — act today
   - <item> — <who> — [goal] — Recommend: <one action>

   ### Tier 2 — this week
   - <item> — <who> — [goal]

   ### Tier 3 — <count> items
   <one line: anything genuinely notable, else "nothing notable">

   ### Loops
   - Overdue: <task> (due <date>)
   - Waiting <N>d on <person>: <task> — Recommend: nudge
   - Self-blocked: <task> — Recommend: decide <the decision>
   - Dispatch: <slug> — owner <name or role> — [goal] — <open | stale Nd>

   ### Relationships
   - <Name> (<tier>, <N>d) — hook: <specific reason to reach out>

   ### Friction
   - <collision, overload, or missing recurring commitment>

   ### Unaligned
   <N> items, <M>% of this week's committed time. <Flag only if over budget.>

   ---
   **What do you want to take first?**
   ```

11. **Archive it.** Write the same text to `briefings/YYYY-MM-DD.md`. If that file already
    exists, append under a `## Re-run HH:MM` heading rather than overwriting it.

12. **Stop.** Do not draft replies, do not propose calendar changes, and do not update
    `my-tasks.yaml` in this command. If {{NAME}} answers the closing question, switch to the
    mode that fits — `/triage` for inbound, `/my-tasks` for planning, `/dispatch` for
    assignment — and say which mode you moved to.

## Guardrails

- Read-only except for `briefings/`.
- Never send, reply, RSVP, or create an event, even if an item obviously needs one. Recommend it.
- Never summarize an email you did not open. "3 unread from Jordan" is honest; a summary of
  their contents is not.
- Never surface more than five Tier 1 items. If there are more, the tiering is wrong — re-rank
  by goal priority and say the count you suppressed.
