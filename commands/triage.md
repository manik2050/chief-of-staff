---
description: Tier inbound, draft responses for approval, and convert commitments into tasks.
argument-hint: "[optional: 'inbox' | 'slack' | 'all' | a person's name | a time window like '48h']"
---

# /triage — Inbound Triage

## Description

Turn a pile of inbound into three tiers, a small number of drafted responses, and a clean
`my-tasks.yaml`. Triage is where commitments get captured; anything {{NAME}} agrees to here
becomes a task in the same turn or it never existed.

Drafts are shown, never sent. Sending requires the approval protocol in CLAUDE.md §4.

## Arguments

`$ARGUMENTS` is optional.

| Value | Behavior |
| --- | --- |
| _(empty)_ | Triage the inbox since the last briefing, or the last 24h |
| `inbox` | Email only |
| `slack` | Chat only (skip with a one-line note if the Slack MCP is absent) |
| `all` | Every connected inbound source |
| a person's name | Only threads involving that person, ignoring the time window |
| a window (`48h`, `7d`) | Widen or narrow the lookback |

## Instructions

1. **Load state**: `goals.yaml`, `my-tasks.yaml`, `contacts/`. You need goals to tier and
   contacts to know who matters. Without `goals.yaml` you cannot triage — say so and stop.

2. **Pull the inbound set** for the window. Collect sender, subject/thread, timestamp, and
   whether {{NAME}} is a direct recipient or on CC. CC-only is one tier lower by default.

3. **Collapse threads.** Multiple messages from the same person on the same subject are one
   item. Report the count inside the item, not as separate items.

4. **Tier each item** per CLAUDE.md §8. For each, record privately: tier, goal id, the sender's
   contact tier, and whether it contains a request, a commitment, an FYI, or a decision.

5. **Check for escalations** before anything else: legal notice, security incident, payment
   failure, a departure, an unhappy customer. These go to the top of Tier 1 and you use the
   word "escalation" in the output.

6. **Present the triage** before drafting anything:

   ```
   ## Triage — <N> items, <window>

   ### Tier 1 — <count>
   1. <Sender> — <subject> — [goal] — <request | decision | commitment>
      Recommend: <reply | delegate to <name> | schedule | decline>

   ### Tier 2 — <count>
   ...

   ### Tier 3 — <count>
   <one line, plus: "Recommend archiving all <N>.">

   Which do you want me to draft? (numbers, "all tier 1", or "none")
   ```

   Then stop and wait. Do not draft before {{NAME}} selects.

7. **Draft the selected items.** For each:
   - Read the full thread first. Never draft against a subject line alone.
   - Match {{NAME}}'s voice from CLAUDE.md §3 — short, declarative, no filler, no emoji.
   - Answer the actual question in the first sentence.
   - Where the reply commits {{NAME}} to something, make the commitment explicit and dated.
   - If the reply needs a meeting, do not propose times here. Say you will check availability,
     and handle it in scheduling mode after this command.
   - Present each draft using the approval block from CLAUDE.md §4, one at a time, and stop
     after each. Never batch sends behind a single approval.

8. **Capture commitments.** For every item that creates an obligation for {{NAME}} — whether the
   reply was sent or not — append a task to `my-tasks.yaml`:
   - `id` from `next_id`, then increment `next_id`
   - `goal` from step 4, or `unaligned`
   - `tier` from step 4
   - `next_action` as a physical next step; if you cannot name one, the item is not a task, it
     is a decision — surface it as such instead
   - `source: email` / `slack`, `created` and `touched` as today
   - `status: waiting` with `waiting_on` set whenever the ball is in someone else's court

9. **Update the CRM.** For every person in Tier 1 or Tier 2, append a dated entry to their
   `contacts/<slug>.md` under `## Log` — what the exchange was, in one line. Create the file
   from the template if the person is new, and set `tier: cold` until {{NAME}} says otherwise.
   Do not log Tier 3 senders.

10. **Close with the ledger:**

    ```
    Drafted: <N> (awaiting your approval)
    Sent: <N>
    Tasks added: <ids>
    Contacts updated: <names>
    Archive proposed: <N> tier-3 items — say "archive" to proceed
    ```

## Guardrails

- One approval, one send. Never interpret approval of a plan as approval of a message.
- Never archive, label, or move a message without approval — archiving is a write.
- Never decline something on {{NAME}}'s behalf, even a Tier 3 invitation.
- If a thread contains health, legal, compensation, or family information, log its existence in
  the CRM without copying the contents.
- If you cannot tell whether something is Tier 1, it is Tier 1. Over-surfacing costs a line;
  under-surfacing costs a relationship.
