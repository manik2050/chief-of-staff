# Stageshow in this kit

[Stageshow](https://benji.org/stageshow) is Benji Taylor's skill for faux product UI:
stills, cursor walkthroughs, bento grids, phones, heroes. It is a Cursor Agent Skill,
not a CoS command. It does not change `/gm`, triage, or approval.

Upstream: [benjitaylor/skills](https://github.com/benjitaylor/skills)
(`stageshow/`). Essay: [benji.org/stageshow](https://benji.org/stageshow).
Installed here as `.agents/skills/stageshow/` so this folder's agents, including
Cloud Agents, actually see it.

## What to do with it

Use it when the deliverable is a **product illustration in React**: a README hero,
a feature card, a homepage bento, a looping cursor demo of the OS, a still of a
briefing or inbox that should look like a shipping product. Ask for one interaction,
in one product, at one size.

```text
A small looping demo for a homepage hero: someone assigns a dispatch to an agent
owner. Light, standard fidelity. Crop the window off the right edge.
```

Or invoke `/stageshow` in Agent chat. To keep it on for the whole session, use it as
a Custom Mode.

Then the agent reads `.agents/skills/stageshow/SKILL.md`, copies the closest gold
example, restyles it to this product, and films the result.

## What not to do with it

Do not run it from `/gm`, `/triage`, `/my-tasks`, `/enrich`, or `/dispatch` unless
the assignment's done-when is a still or demo. A briefing is one screen of prose
(CLAUDE.md §14). A drafted email is text. A work-log file is markdown.

Do not replace Cursor Canvas with it. Canvas is a durable artifact beside chat
(`WriteCanvas`). Stageshow is ordinary React in the repo that you can ship on a
page. Pick Canvas for a metrics table; pick Stageshow for a framed product shot.

Do not copy the skill into `skills/`. That directory is reserved for this kit's
own `SKILL.md` packaging (`docs/roadmap.md`). Do not copy it into
`~/.claude/chief-of-staff/` — the installer must not.

Do not paste another company's identity onto a CoS still. Product studies in
`examples/` are for borrowing an interaction, not Linear's chrome on our briefing.

## How it runs in this repo

1. Read `SKILL.md` in full before writing UI.
2. From `.agents/skills/stageshow/`: `npm install` then `npm run dev`. Preview at
   `http://stageshow.localhost:1355` (or the Vite URL on Windows). Node 20.19+.
3. Copy the closest gold example. Film it first. Then change look and copy to this
   product. A rename-only copy is not done.
4. Output lives with the host (README assets, a docs page, a site), not in
   `briefings/` or `work-log/`.
5. Film with `node scripts/film.mjs` as the skill says. A still is not proof of
   motion.

The kit needs React, react-dom, and lucide-react. Copy `kit/` into the host
project; do not import from `.agents/skills/...` at runtime in shipping code.

## Dispatch

A still or demo is `implement` / `feature` (or a human designer). `done_when` is
the component plus a filmed still at the shown width. `out_of_scope` includes
sending, merging, and rewriting CoS playbooks. CLAUDE.md §4 still wins: publishing
the still still needs a yes.

## Update

```sh
npx skills add benjitaylor/skills --skill stageshow --agent cursor
```

Review the diff. Keep `LICENSE` and `NOTICE.md`. Do not rewrite the skill in place
to "fit CoS"; put CoS constraints in this file and in
`.cursor/rules/stageshow.mdc`.
