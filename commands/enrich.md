---
description: Update the contact CRM — log interactions, refresh context, flag overdue relationships.
argument-hint: "[optional: a person's name | 'overdue' | 'new' | 'audit']"
---

# /enrich — Relationship Enrichment

## Description

Keep `contacts/` true. Log what happened with whom, refresh what has changed about them, and
surface the relationships that are quietly going cold.

Writes to `contacts/`. Proposes outreach and never sends it.

## Arguments

`$ARGUMENTS` is optional.

| Value | Behavior |
| --- | --- |
| _(empty)_ | Enrich everyone {{NAME}} interacted with since the last run |
| a person's name | Deep enrichment on one contact, including external lookup if available |
| `overdue` | Cadence report only — who is past due, with a hook for each |
| `new` | Create contact files for people seen in the inbox or calendar with no file yet |
| `audit` | Check every contact file for schema problems and missing fields |

## Instructions

1. **Load** `contacts/`, `goals.yaml`, and the last entry date in each contact file. Cadence is
   computed from the most recent dated entry under `## Log`, never from file mtime.

2. **Gather interactions** since the last run: calendar attendees, email correspondents, chat
   DMs. Group by person. One-to-one contact counts toward cadence; group meetings and automated
   messages do not.

3. **Match to files.** Resolve each person to a `contacts/<slug>.md`. Match on email address
   first, then full name. Never merge two files automatically — if you suspect a duplicate, say
   so and ask.

4. **Log each interaction.** Append to `## Log` in reverse-chronological order:

   ```
   ### 2026-01-05 — <channel: email | call | meeting | chat>
   <One or two lines: what was discussed and what changed. Name any commitment either
   side made, and the date it is due.>
   ```

   Never rewrite an existing entry. Corrections are new entries that say what they correct.

5. **Refresh the header fields** when the interaction revealed something: role change, company
   change, new timezone, a new preference ("prefers voice notes", "never replies before noon").
   Preferences are more useful than biography — record them.

6. **External enrichment** (only when a person was named explicitly, and only if a web tool is
   available): one lookup for role changes, funding, or public news. Add at most two lines under
   `## Context`, each with the date you found it. If no web tool is available, write nothing and
   say "no external check" in the summary. Never guess at a title or employer.

7. **Cadence pass.** For every contact, compute days since last one-to-one touch and compare
   against the tier thresholds in CLAUDE.md §9. Build the overdue list, highest tier first.

8. **Find the hook.** For each overdue contact, look for a specific reason to reach out: an open
   commitment in `my-tasks.yaml`, a thread that trailed off, something in `## Context`, or a goal
   in `goals.yaml` they are a stakeholder on. **No hook, no outreach proposal** — report the
   relationship as overdue and leave it.

9. **Output:**

   ```
   ## Enrichment — <N> contacts touched

   ### Logged
   - <Name> (<tier>) — <one line of what changed>

   ### New contacts created
   - <Name> — <where they came from> — tier: cold (confirm?)

   ### Overdue (top 3)
   - <Name> (<tier>, <N>d overdue) — hook: <specific reason>
     Recommend: <a two-line note | 25 min call | nothing, it can wait>

   ### Data quality
   - <file> — <missing field or suspected duplicate>
   ```

10. **Offer to draft** outreach for at most one overdue contact — the highest-value one. If
    {{NAME}} says yes, draft it and use the approval protocol in CLAUDE.md §4. Never send.

## Guardrails

- Surface at most three overdue contacts per run. A list of twenty is a list of zero.
- Never copy health, legal, compensation, or family details into a contact file. Note that a
  sensitive topic exists if it affects scheduling, and nothing more.
- Never infer a relationship tier. New contacts are `cold` until {{NAME}} says otherwise.
- Never record speculation as fact. Anything from an external lookup is dated and attributed.
- Never propose outreach to a `cold` contact without a hook that {{NAME}} would recognize.
