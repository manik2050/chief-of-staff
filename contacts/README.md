# contacts/ — the CRM

One markdown file per person, named `<first>-<last>.md` in lowercase kebab-case. No database, no
export format, no sync. A person is a file you can read, and that is the whole point.

## Anatomy of a contact file

```
---
name: Jordan Rivera          # as you would address them
tier: inner                  # inner | working | network | cold
email: jordan@example.com
company: Independent
role: Partner
timezone: America/New_York
goals: [public-build]        # goal ids from goals.yaml they are a stakeholder on
first_met: 2024-09-12
last_touch: 2026-01-02       # most recent one-to-one; mirrors the top Log entry
---

## Who they are
Two or three lines. What they do, how you know them, what they are good for.

## How to work with them
Preferences, not biography. Response patterns, channel, tone, what they dislike.

## Context
Dated facts from the outside world. One line each, with the date you learned them.

## Open threads
Live commitments in either direction. Removed when closed.

## Log
Reverse-chronological dated entries. Append only.
```

## Rules

- **`last_touch` counts one-to-one contact only.** A group meeting, a CC, or an automated
  message does not reset the clock.
- **Log entries are append-only.** Never rewrite history; a correction is a new dated entry that
  says what it corrects.
- **Preferences beat biography.** "Replies within the hour, hates scheduled calls" is worth more
  than a paragraph of career history.
- **No sensitive contents.** Health, legal, compensation, and family details stay out. Note that
  a topic exists only when it affects scheduling.
- **New people start at `tier: cold`.** The Chief of Staff never promotes a tier on its own.

## Cadence

Tiers drive outreach cadence. See CLAUDE.md §9.

| Tier | Target | Overdue at |
| --- | --- | --- |
| `inner` | 14 days | 21 days |
| `working` | 45 days | 60 days |
| `network` | 120 days | 180 days |
| `cold` | — | never |

## Files here

- `_template.md` — copy this for a new contact
- `jordan-rivera.md` — worked example; delete it once you have real contacts
