# Agent skills (project)

Cursor loads `SKILL.md` files from this tree automatically. They are **project skills**:
they travel with the repo, including Cloud Agents. They are not the Chief of Staff OS.

| Path | What belongs here |
| --- | --- |
| `.agents/skills/` | Third-party and project Agent Skills (Stageshow, later others) |
| `skills/` | Reserved for this kit's own packaging. Empty on purpose. Do not dump
  pstack or Stageshow there. |
| `~/.claude/chief-of-staff/` | Operator state. The installer never copies this folder into it. |

## Stageshow

Installed from [benjitaylor/skills](https://github.com/benjitaylor/skills)
(`npx skills add benjitaylor/skills --skill stageshow --agent cursor`).

How it fits this kit: [`docs/stageshow.md`](../docs/stageshow.md).
The skill itself: [`skills/stageshow/SKILL.md`](skills/stageshow/SKILL.md).
It auto-triggers from the skill description plus
`.cursor/rules/stageshow.mdc` (`alwaysApply: true`). You do not need
`/stageshow`. License and notices stay in that folder.

Refresh from upstream (re-copies; review the diff). `skills-lock.json` at the repo
root pins the hash the CLI computed.

```sh
npx skills add benjitaylor/skills --skill stageshow --agent cursor
```
