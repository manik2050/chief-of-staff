# work-log/ — assignments

One markdown file per piece of work the Chief of Staff has handed to a human engineer or a
named agent role (`explore`, `implement`, `review`). `/dispatch` writes here. `/gm` reads open
files into the Loops section.

This is not a ticket tracker and not a GitHub proxy. GitHub issues are an optional follow-on,
approved like any other send.

## Filename

`YYYY-MM-DD-<slug>.md` — date is the day the assignment was written, in the operator's
timezone. Slug is kebab-case, short, unique that day.

## Anatomy

Copy `_template.md`. Frontmatter is the contract; the body is for the owner.

```
---
id: d-20260920-ship-readme
goal: public-build            # id from goals.yaml, or unaligned
status: open                  # open | in-progress | done | dropped
owner:
  kind: agent                 # human | agent
  name: implement             # contact name, or explore | implement | review
created: 2026-09-20
done_when:
  - "README says how to run /gm in Cursor"
out_of_scope:
  - "No hosted service, no new repo"
status_location: "work-log/2026-09-20-ship-readme.md and my-tasks.yaml#t-010"
---
```

## Rules

- **Done-when is observable.** If you cannot tell from a file or a PR whether it is done, it is
  not done-when.
- **Out-of-scope is mandatory.** At least one exclusion. "Do the obvious thing" is not a scope.
- **Status updates append** under `## Status`, dated. Do not rewrite the request.
- **One owner.** Split the work rather than stacking roles.
- **Drop is a status**, not a delete. Keep the file.
- **No secrets, no employer IP.** Treat this directory as publishable.

## Agent roles

| Role | May | May not |
| --- | --- | --- |
| `explore` | Read, write findings to `status_location` | Edit product code, send, merge |
| `implement` | Edit on a branch, run tests | Merge, send, create repos, expand scope |
| `review` | Read a diff, write findings | Approve, merge, or "just fix it" |

## Files here

- `_template.md` — copy this for a new assignment
- `README.md` — this file
