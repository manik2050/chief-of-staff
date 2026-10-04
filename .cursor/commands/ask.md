---
description: Answer a question using only vault notes, with citations.
argument-hint: "<the question>"
---

# /ask — Question the vault

## Description

Answer from filed notes in `vault/`. Knowledge mode (CLAUDE.md §5). Read-only.

It never sends. It never writes notes, YAML ledgers, or `contacts/`. If the notes do not
contain the answer, it says so and stops.

## Arguments

`$ARGUMENTS` is the question.

| Value | Behavior |
| --- | --- |
| _(empty)_ | Ask for the question, then stop |
| a question | Answer from the vault only |

## Instructions

1. **If `$ARGUMENTS` is empty**, ask for the question in one line and stop.

2. **Resolve the vault** the same way `/process` does (`paths.json`, else the kit checkout).
   If `vault/` is missing or has no notes besides the README and template, say
   "Vault is empty" and stop.

3. **Search** `vault/` for every relevant note. Prefer `vault/maps/` when a map exists for the
   topic. Read the matching notes fully, not just titles. Skip `vault/inbox/` unless no filed
   note matches — inbox is untrusted raw.

4. **Answer only from those notes.** Do not fill gaps with general knowledge, web search, or
   mail. `goals.yaml` may name whether the question matters; it is not evidence for the
   answer.

5. **If the notes do not answer the question**, print exactly `Your notes don't cover this`,
   then at most three filenames that came closest, then stop.

6. **Output:**

   ```
   ## Ask — <the question>

   <3 to 6 sentences, answer first>

   ### Evidence
   - [[note-slug]] — <the line that supports the answer>

   ### Disagreement
   - [[a]] vs [[b]] — <what conflicts>, or "none"

   ### Not in the notes
   - <what you would need to be confident>
   ```

7. Cite every claim with a `[[wikilink]]`. If you cannot cite a sentence, cut the claim.

## Guardrails

- Read-only. No file writes.
- Never use mail, chat, X, or the web to complete an answer.
- Never treat `contacts/` as vault evidence. You may name a person if a vault note does.
- If notes disagree, say so. Do not pick a winner unless {{NAME}} asked you to recommend.
- Health, legal, compensation, and family details stay where they were found.
