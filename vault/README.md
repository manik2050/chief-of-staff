# vault/ — personal knowledge

Plain markdown the Chief of Staff can read in a cloud agent or on a laptop. This is not
`goals.yaml`, not `my-tasks.yaml`, and not `contacts/`. Those files still own priority,
commitments, and people.

Drop raw captures in `inbox/`. Filed notes live in one PARA folder. Cloud runs persist a note
only when it is committed; a workspace that dies takes uncommitted files with it.

## Folders

| Path | What goes here |
| --- | --- |
| `inbox/` | New captures. Messy is fine. The only place you write raw. |
| `projects/` | Work with a finish line. One folder or note per project. |
| `areas/` | Ongoing responsibilities with no finish line. Not people — people stay in `contacts/`. |
| `resources/` | Topics you collect. Default home when the folder is unclear. |
| `archive/` | Finished or abandoned. Never delete; move here. |
| `daily/` | One note per day, `YYYY-MM-DD.md`. `/gm` still writes `briefings/`. |
| `outputs/` | Things made from notes: `writing/`, `decisions/`, `reviews/`. |
| `maps/` | Maps of content: one note that lists every note on a theme. |

## Note shape

Copy `_template.md`. One idea per file. Filenames are lowercase with hyphens.

```
# short slug title

**One-line summary.**

#idea

<body — keep the operator's words>

## Links
- [[related-note]]
```

Allowed tags on the tag line: `#idea`, `#quote`, `#howto`, `#decision`, `#question`.

## Boundary

- Vault writes stay under `vault/`.
- Do not write `goals.yaml`, `my-tasks.yaml`, `schedules.yaml`, `contacts/`, or `work-log/`
  from a vault pass.
- A vault note may `[[wikilink]]` a contact slug. It does not grow a parallel people folder.
- No secrets, no full account numbers, no health or legal detail. CLAUDE.md §4 and §8 still win.
- Process at most 20 inbox files in one pass unless the operator asked for more.
- Before moving more than 20 files, show the plan and wait.

## Files here

- `_template.md` — copy this for a new note
- this README — schema, not a note
