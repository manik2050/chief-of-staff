---
description: File vault inbox notes into PARA folders without touching the ledgers.
argument-hint: "[optional: a filename | 'dry' | a number like '10']"
---

# /process — Empty the vault inbox

## Description

Take raw captures in `vault/inbox/` and turn each idea into one filed note. This is knowledge
mode (CLAUDE.md §5). It writes only under `vault/`.

It never sends. It never writes `goals.yaml`, `my-tasks.yaml`, `schedules.yaml`, `contacts/`,
or `work-log/`. Mail stays on `/triage`.

## Arguments

`$ARGUMENTS` is optional.

| Value | Behavior |
| --- | --- |
| _(empty)_ | Process up to 20 inbox files |
| a filename | Process only that inbox file |
| a number (`10`) | Process at most that many files, still capped at 20 unless {{NAME}} said so |
| `dry` | Propose destinations and links. Write nothing |

## Instructions

1. **Resolve the vault.** Read `paths.json` if it exists. If `$COS_HOME` is unset, the kit
   checkout is the root (`CLAUDE.md` + `core/paths.py` in the same directory). If `vault/` is
   missing, say so, offer to create it from the shipped tree, and stop.

2. **List** `vault/inbox/` files. Ignore `.gitkeep` and `README.md`. Newest first. Cap at 20
   unless {{NAME}} named a higher number in this turn. If the inbox is empty, print that and
   stop.

3. **Read each inbox file fully.** If it holds more than one idea, split it into one note per
   idea. Do not invent a third idea that is not in the file.

4. **Write each note** using `vault/_template.md`:
   - Filename: lowercase hyphenated slug, `.md`.
   - Bold one-line summary at the top.
   - One tag line: `#idea`, `#quote`, `#howto`, `#decision`, or `#question`.
   - Keep {{NAME}}'s words. Fix typos and structure only.
   - Keep any source URL at the bottom.
   - Folder: `projects/` if it has a finish line, `areas/` if it is an ongoing duty,
     `resources/` otherwise. If unsure, use `resources/` and tag `#question`.
   - Do not create `vault/areas/people`. A person belongs in `contacts/`. You may add
     `[[contact-slug]]` under Links.

5. **Link.** Search the vault (not the YAML ledgers) for 3 to 5 related notes. Add them under
   `## Links` as `[[wikilinks]]`. Append a backlink on each related note. If you find no
   related notes, write `## Links` and `none yet`.

6. **Move** the original inbox file to `vault/archive/inbox/` (create the folder if needed).
   Never delete. On `dry`, skip this step.

7. **Cloud persistence.** If this session is a Cursor cloud agent, say in one line that the
   new notes exist only after they are committed.

8. **Output:**

   ```
   ## Vault process — <N> inbox files

   | Original | New notes | Folder | Links |
   | --- | --- | --- | --- |
   | <inbox file> | <new filenames> | <folder> | <count> |

   ### Unsure
   - <note> — why the folder is a guess

   ### Left in inbox
   - <file> — over the cap, or {{NAME}} did not ask for it
   ```

   On `dry`, use the same table and write nothing.

## Guardrails

- Hard cap: 20 inbox files unless {{NAME}} asked for more in this turn.
- Before moving more than 20 files, show the plan and wait.
- Never delete. Archive instead.
- Never rewrite the operator's opinion into the agent's voice.
- Never write outside `vault/`.
- Never create a people tree. Never file a commitment into `my-tasks.yaml` from this command.
  If a capture is clearly a promise, say so in the summary and leave the task unwritten
  unless {{NAME}} asks to add it via `/my-tasks`.
- Health, legal, compensation, and family details stay out of the filed note. CLAUDE.md §4.
