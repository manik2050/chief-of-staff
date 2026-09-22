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
tier: balanced                # cost | balanced | intelligence
execution: feature            # pstack playbook, or null (human / pstack off)
approval_required: false      # true records a future execution gate
approval_reasons: []          # send_email, publish, merge, production_deploy, etc.
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
- **Tier is effort, not permission.** `explore` defaults to `cost`, `implement` to `balanced`,
  and `review` to `intelligence`. High-risk work can only move up.
- **Execution is the playbook, not a fourth role.** `investigation`, `feature`,
  `refactoring`, `authoring-a-skill`, or `interrogate` when pstack is enabled; `null`
  otherwise. The owner line stays a single noun.
- **Approval is explicit.** A send, publish, merge, production deploy, financial transaction,
  or deletion sets `approval_required: true`. The assignment approval does not approve that
  later action.
- **Drop is a status**, not a delete. Keep the file.
- **No secrets, no employer IP.** Treat this directory as publishable.

## Agent roles

| Role | Default tier | Default `execution` | May | May not |
| --- | --- | --- | --- | --- |
| `explore` | `cost` | `investigation` | Read, write findings to `status_location` | Edit product code, send, merge |
| `implement` | `balanced` | `feature` | Edit on a branch, run tests | Merge, send, create repos, expand scope |
| `review` | `intelligence` | `interrogate` | Read a diff, write findings | Approve, merge, or "just fix it" |

`execution` is the pstack playbook the owner runs when the plugin is on (`docs/pstack.md`).
It is `null` for a human owner, and `null` when pstack is unavailable. A playbook is not
permission: CLAUDE.md §4 still gates send, merge, and publish.

## Files here

- `_template.md` — copy this for a new assignment
- `README.md` — this file
